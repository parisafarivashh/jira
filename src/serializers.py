from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Project, Room, Message, MemberMessageSeen, RoomMember, \
    Task, Assignment
from .tasks import create_room_member


# region project serializer
# class ProjectSerializer(ModelSerializer):
#     class Meta:
#         model = Project
#         fields = ['id', 'title', 'description', 'manager_id', 'status',
#                   'public_room_id', 'private_room_id', 'created_by']
#
#         extra_kwargs = {
#             'public_room_id': {'read_only': True},
#             'private_room_id': {'read_only': True},
#             'created_by': {'read_only': True},
#         }
#
#     def create(self, validated_data):
#         user = self.context['request'].user
#         public_room_id = Room.objects.create(
#             title=validated_data['title'],
#             type='project',
#             private=False,
#             owner=user
#         )
#         private_room_id = Room.objects.create(
#             title=validated_data['title'],
#             type='project',
#             private=True,
#             owner=user
#         )
#         Message.objects.create(
#             type='alert',
#             body='Created',
#             sender_id=user,
#             room_id=public_room_id,
#         )
#
#         manager_id = validated_data['manager_id'].id
#         create_room_member.apply_async((
#             user.id, public_room_id.id, private_room_id.id, manager_id
#         ))
#
#         validated_data['public_room_id'] = public_room_id
#         validated_data['private_room_id'] = private_room_id
#
#         return super(ProjectSerializer, self).create(validated_data)


# class UpdateProjectSerializer(ModelSerializer):
#     class Meta:
#         model = Project
#         fields = ['id', 'title', 'description', 'manager_id', 'status']
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
            room_member.latest_seen_message = instance
            room_member.save(update_fields=["latest_seen_message"])
        except RoomMember.DoesNotExist:
            pass

        super().update(instance, validated_data)
        return instance


class MemberMessageSeenSerializer(ModelSerializer):

    class Meta:
        model = MemberMessageSeen
        fields = ['id', 'member_id', 'message_id']
# endregion


# region Task serializer
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

        manager_id = validated_data['manager_id'].id
        create_room_member.delay(
            user.id, public_room_id.id, private_room_id.id, manager_id
        )

        return super(TaskSerializer, self).create(validated_data)
# endregion


# region Assignment serializer
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'member_id', 'task_id', 'status',
                  'public_room_id', 'private_room_id', 'created_by']
        extra_kwargs = {
            'status': {'read_only': True},
            'public_room_id': {'read_only': True},
            'private_room_id': {'read_only': True},
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user

        task_id = validated_data['task_id']

        validated_data['public_room_id'] = task_id.public_room_id
        validated_data['private_room_id'] = task_id.private_room_id

        create_room_member.delay(user.id, task_id.public_room_id.id,
                                 task_id.private_room_id.id)

        return super(AssignmentSerializer, self).create(validated_data)


class AssignmentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = ['id', 'start_date', 'end_date', 'estimate_hours', 'status']
        extra_kwargs = {'status': {'read_only': True}}

    def validate(self, attrs):
        if attrs['start_date'].date() < datetime.today().date() or \
                attrs['end_date'].date() < datetime.today().date():

            raise ValidationError(
                detail={"error": 'date must be more than today'}
            )
        return attrs


class SummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ['id', 'title', 'type']

# endregion
