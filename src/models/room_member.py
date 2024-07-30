from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from . import BaseClassMixin, Room, Message


Member = get_user_model()


class RoomMemberQueryset(models.QuerySet):

    def is_room_member(self, member_id, room_id):
        return self.filter(Q(member__id=member_id) & Q(room__id=room_id)) \
                .exists()


class RoomMemberManager(models.Manager):

    def get_queryset(self):
        return RoomMemberQueryset(self.model, self._db)

    def is_room_member(self, member_id, room_id):
        return self.get_queryset().is_room_member(member_id, room_id)


class RoomMember(BaseClassMixin):

    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='room_members')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='members')
    latest_seen_message = models.ForeignKey(Message, on_delete=models.PROTECT, related_name='latest_message_room', blank=True, null=True)

    objects = RoomMemberManager()

    class Meta:
        db_table = 'room_member'
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'room'],
                name='unique_room_member',
            )
        ]
        indexes = [
            models.Index(
                fields=['member'],
                name='room_member_index'
            )
        ]

