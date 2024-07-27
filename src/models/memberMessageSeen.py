from django.contrib.auth import get_user_model
from django.db import models

from . import BaseClassMixin, Message


member = get_user_model()


class MemberMessageSeen(BaseClassMixin):
    message = models.ForeignKey(Message, on_delete=models.PROTECT, related_name='seen', db_index=True)
    member = models.ForeignKey(member, on_delete=models.PROTECT, related_name='message_seen')

    class Meta:
        db_table = 'member_message_seen'
        constraints = [
            models.UniqueConstraint(
                fields=['message', 'member'],
                name='unique_member_seen_message',
            )
        ]

