from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from ..designPattern.message import MessageFacade
from ..helpers import check_room_member
from ..models import Message, MemberMessageSeen, RoomMember, Room


class SeenMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'is_seen']

    @transaction.atomic()
    def update(self, instance, validated_data):
        user = self.context['request'].user
        MemberMessageSeen.objects.create(
            member=user,
            message=instance
        )
        try:
            room_member = RoomMember.objects.get(
                member=user, room=instance.room
            )
            room_member.latest_seen_message = instance
            room_member.save(update_fields=["latest_seen_message"])
        except RoomMember.DoesNotExist:
            pass

        return super().update(instance, validated_data)


class EditMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'body']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'body', 'room', 'type', 'sender', 'is_seen']
        extra_kwargs = {
            'room': {'read_only': True},
            'type': {'read_only': True},
            'sender': {'read_only': True},
            'is_seen': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        room_id = self.context['format'].room_id
        print(room_id)
        room = get_object_or_404(Room, id=self.context['format'].id)

        check_room_member(room, user)

        validated_data['room'] = room_id
        validated_data['type'] = 'message'
        validated_data['sender'] = user

        message = super(MessageSerializer, self).create(validated_data)

        MessageFacade(
            message=message,
            room=room,
            user=user
        ).send_message()
        return message

