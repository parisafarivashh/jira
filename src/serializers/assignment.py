from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Assignment
from ..tasks import create_room_member


class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = ['id', 'member', 'task', 'status', 'public_room',
                  'private_room', 'created_by']
        extra_kwargs = {
            'status': {'read_only': True},
            'public_room': {'read_only': True},
            'private_room': {'read_only': True},
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        task = validated_data['task']
        validated_data['public_room'] = task.public_room
        validated_data['private_room'] = task.public_room

        create_room_member.apply_async((
            user.id,
            task.public_room.id,
            task.private_room.id,
        ))
        return super(AssignmentSerializer, self).create(validated_data)


class AssignmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'start_date', 'end_date', 'estimate_hours', 'status']
        extra_kwargs = {'status': {'read_only': True}}

    def validate(self, attrs):
        if attrs['start_date'].date() > attrs['end_date'].date():
            raise ValidationError(
                detail={"error": 'start date must be lower than end date'}
            )

        if attrs['start_date'].date() < datetime.today().date() or \
                attrs['end_date'].date() < datetime.today().date():
            raise ValidationError(
                detail={"error": 'date must be more than today'}
            )

        return attrs

