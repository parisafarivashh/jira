from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import NotFound

from ..models import BaseClassMixin, SoftDeleteMixin, Room


member = get_user_model()


class Message(BaseClassMixin, SoftDeleteMixin):

    class Type(models.TextChoices):
        MESSAGE = 'message'
        ALERT = 'alert'

    type = models.CharField(max_length=10, choices=Type.choices, default=Type.MESSAGE)
    sender = models.ForeignKey(member, on_delete=models.PROTECT, related_name='sender_message')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='messages')
    body = models.TextField()
    is_seen = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'message'

    def get_object(self, message_id: int):
        try:
            message = self.object.get(id=message_id)
            return message
        except self.DoesNotExist:
            raise NotFound



