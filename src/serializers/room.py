from rest_framework import serializers

from ..models import Room


class SummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ['id', 'title', 'type']

