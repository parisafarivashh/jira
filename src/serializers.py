from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.serializers import ModelSerializer

from .models import Project, Room, Message, MemberMessageSeen, RoomMember, Task


# region project serializer
class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager_id', 'status',
                  'public_room_id', 'private_room_id', 'created_by']

        extra_kwargs = {
            'public_room_id': {'read_only': True},
            'private_room_id': {'read_only': True},
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        # ToDo: use celery task for created room and message
        user = self.context['request'].user
        public_room_id = Room.objects.create(
            title=validated_data['title'],
            type='project',
            private=False,
            owner=user
        )
        private_room_id = Room.objects.create(
            title=validated_data['title'],
            type='project',
            private=True,
            owner=user
        )
        Message.objects.create(
            type='alert',
            body='Created',
            sender_id=user,
            room_id=public_room_id,
        )
        RoomMember.objects.bulk_create([
            RoomMember(member_id=user, room_id=public_room_id),
            RoomMember(member_id=user, room_id=private_room_id),
            RoomMember(member_id=validated_data['manager_id'], room_id=public_room_id),
            RoomMember(member_id=validated_data['manager_id'], room_id=private_room_id),
        ])

        validated_data['public_room_id'] = public_room_id
        validated_data['private_room_id'] = private_room_id

        return super(ProjectSerializer, self).create(validated_data)


class UpdateProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager_id', 'status']
# endregion


# region message serializer
class MessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'body', 'room_id', 'type', 'sender_id', 'is_seen']
        extra_kwargs = {
            'room_id': {'read_only': True},
            'type': {'read_only': True},
            'sender_id': {'read_only': True},
            'is_seen': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        room_id = self.context['room_id']

        validated_data['room_id'] = room_id
        validated_data['type'] = 'message'
        validated_data['sender_id'] = user
        return super(MessageSerializer, self).create(validated_data)


class EditMessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'body']


class SeenMessageSerializer(ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'is_seen']

    @transaction.atomic()
    def update(self, instance, validated_data):
        user = self.context['request'].user
        MemberMessageSeen.objects.create(
            member_id=user,
            message_id=instance
        )
        try:
            room_member = RoomMember.objects.get(
                member_id=user, room_id=instance.room_id
            )
            room_member.latest_seen_message_id = instance
            room_member.save(update_fields=["latest_seen_message_id"])
        except RoomMember.DoesNotExist:
            pass

        super().update(instance, validated_data)
        return instance


class MemberMessageSeenSerializer(ModelSerializer):

    class Meta:
        model = MemberMessageSeen
        fields = ['id', 'member_id', 'message_id']

# endregion


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True},
            'public_room_id': {'read_only': True},
            'private_room_id': {'read_only': True},
            'manager_id': {'read_only': True},
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        # ToDo: use celery task
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['manager_id'] = validated_data['project_id'].manager_id

        public_room_id = Room.objects.create(
            title=validated_data['title'],
            type='task',
            private=False,
            owner=user
        )
        private_room_id = Room.objects.create(
            title=validated_data['title'],
            type='task',
            private=True,
            owner=user
        )

        Message.objects.create(
            type='alert',
            body='Created',
            sender_id=user,
            room_id=public_room_id,
        )
        validated_data['public_room_id'] = public_room_id
        validated_data['private_room_id'] = private_room_id

        RoomMember.objects.bulk_create([
            RoomMember(member_id=user, room_id=public_room_id),
            RoomMember(member_id=user, room_id=private_room_id),
            RoomMember(
                member_id=validated_data['manager_id'],
                room_id=public_room_id
            ),
            RoomMember(
                member_id=validated_data['manager_id'],
                room_id=private_room_id
            ),
        ], ignore_conflicts=True)

        return super(TaskSerializer, self).create(validated_data)

