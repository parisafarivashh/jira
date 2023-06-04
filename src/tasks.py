from celery import shared_task
from rest_framework.exceptions import NotFound

from .models import RoomMember, Room
from user.models import Member


@shared_task()
def create_room_member(user_id, manager_id, public_room_id, private_room_id):
    try:
        private_room = Room.objects.get(id=private_room_id)
        public_room = Room.objects.get(id=public_room_id)

        user = Member.objects.get(id=user_id)
        manager = Member.objects.get(id=manager_id)

    except Exception:
        raise NotFound()

    RoomMember.objects.bulk_create([
        RoomMember(member_id=user, room_id=public_room),
        RoomMember(member_id=user, room_id=private_room),
        RoomMember(member_id=manager, room_id=public_room),
        RoomMember(member_id=manager, room_id=private_room),
    ], ignore_conflicts=True)

