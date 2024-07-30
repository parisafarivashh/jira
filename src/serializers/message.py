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
    # sender_name = serializers.StringRelatedField(
    #     source='sender.title',
    #     read_only=True
    # )
    sender_name = serializers.ReadOnlyField(source='sender.title')
    # sender_name = serializers.PrimaryKeyRelatedField(source='sender.title',
    #                                             read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'body', 'room', 'type', 'sender', 'is_seen',
                  'sender_name']
        extra_kwargs = {
            'room': {'read_only': True},
            'type': {'read_only': True},
            'sender': {'read_only': True},
            'is_seen': {'read_only': True},
            # 'sender_name': {'read_only': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender_email'] = instance.sender.email
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        kwargs = self.context['request'].parser_context['kwargs']
        room_id = kwargs['id']
        room = get_object_or_404(Room, id=room_id)

        check_room_member(room, user)
        print('okeeeeee')

        validated_data['room'] = room
        validated_data['type'] = 'message'
        validated_data['sender'] = user

        message = super(MessageSerializer, self).create(validated_data)

        MessageFacade(
            message=message,
            room=room,
            user=user
        ).send_message()
        return message


class MemberMessageSeenSerializer(serializers.ModelSerializer):

    class Meta:
        model = MemberMessageSeen
        fields = ['id', 'member', 'message']

