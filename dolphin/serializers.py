from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .models import Project, Room, Message


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

    @transaction.atomic
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

        validated_data['public_room_id'] = public_room_id
        validated_data['private_room_id'] = private_room_id

        return super(ProjectSerializer, self).create(validated_data)


class UpdateProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager_id', 'status']

