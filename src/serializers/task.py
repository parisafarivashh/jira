from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Task, Room, Message
from ..tasks import create_room_member


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True},
            'public_room': {'read_only': True},
            'private_room': {'read_only': True},
            'manager': {'read_only': True},
            'created_by': {'read_only': True},
        }

    def validate(self, attrs):
        # todo : better ways?
        if attrs.get('project') and attrs['project'].removed_at is not None:
            raise ValidationError(detail={"error": 'Project does not exist'})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['manager'] = validated_data['project'].manager

        public_room = Room.objects.create(
            title=validated_data['title'],
            type='task',
            private=False,
            owner=user
        )
        private_room = Room.objects.create(
            title=validated_data['title'],
            type='task',
            private=True,
            owner=user
        )
        Message.objects.create(
            type='alert',
            body='Created',
            sender=user,
            room=public_room,
        )
        validated_data['public_room'] = public_room
        validated_data['private_room'] = private_room
        manager_id = validated_data['manager'].id
        create_room_member.apply_async((
            user.id, public_room.id, private_room.id, manager_id
        ))
        return super(TaskSerializer, self).create(validated_data)


