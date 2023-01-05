from django.db import transaction
from rest_framework.serializers import ModelSerializer

from .models import Project, Room


class CreateProjectSerializer(ModelSerializer):
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
        public_room_id = Room.objects.create(
            title=validated_data['title'],
            type='project',
            private=False,
            owner=self.context['request'].user
        )
        private_room_id = Room.objects.create(
            title=validated_data['title'],
            type='project',
            private=True,
            owner=self.context['request'].user
        )

        validated_data['public_room_id'] = public_room_id
        validated_data['private_room_id'] = private_room_id

        return super(CreateProjectSerializer, self).create(validated_data)

