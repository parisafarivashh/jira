from rest_framework import serializers

from user.models import Member
from user.serializers import MemberDetailsSerializer
from .room import SummarySerializer
from ..models import Project, Message, Room
from ..tasks import create_room_member


class ProjectSerializer(serializers.ModelSerializer):
    manager = MemberDetailsSerializer(read_only=True)
    created_by = MemberDetailsSerializer(read_only=True)
    private_room = SummarySerializer(read_only=True)
    public_room = SummarySerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        source='manager',
        write_only=True,
        required=True,
    )

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager_id', 'manager',
                  'status', 'public_room', 'private_room', 'created_by']

    def create(self, validated_data):
        user = self.context['request'].user

        public_room = Room.objects.create(
            title=validated_data['title'],
            type='project',
            private=False,
            owner=user
        )
        private_room = Room.objects.create(
            title=validated_data['title'],
            type='project',
            private=True,
            owner=user
        )
        Message.objects.create(
            type='alert',
            body='Created',
            sender=user,
            room=public_room,
        )

        manager_id = validated_data['manager'].id
        create_room_member.apply_async((
            user.id, public_room.id, private_room.id, manager_id
        ))

        validated_data['public_room'] = public_room
        validated_data['private_room'] = private_room

        return super(ProjectSerializer, self).create(validated_data)


class UpdateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager_id', 'status']

