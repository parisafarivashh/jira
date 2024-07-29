from django.db.models import Q
from rest_framework.exceptions import NotFound

from ..models import Message, MemberMessageSeen, RoomMember


class MessageFacade:

    def __init__(self, message: Message, **kwargs):
        self.message = message
        self.room = kwargs.get('room')
        self.user = kwargs.get('user')

    def send_message(self):
        self._update_latest_message_seen()
        self._insert_member_message_seen()
        self._update_is_seen()

    def _update_latest_message_seen(self):
        try:
            room_member = RoomMember.objects.get(
                room_id=self.room,
                member_id=self.user,
            )
            room_member.latest_seen_message = self.message
            room_member.save(update_fields=["latest_seen_message"])

        except Exception:
            pass

    def _update_is_seen(self):
        Message.objects.filter(
            ~Q(sender=self.user),
            id__lt=self.message.id,
            room=self.room,
        ).update(is_seen=True)

    def _insert_member_message_seen(self):
        messages = Message.objects.filter(
            ~Q(sender=self.user),
            room=self.room.id,
            id__lt=self.message.id,
        )
        if messages is not None:
            objects = [
                MemberMessageSeen(
                    message=message,
                    member=self.user
                ) for message in messages
            ]
            MemberMessageSeen.objects.bulk_create(
                objects,
                ignore_conflicts=True
            )


