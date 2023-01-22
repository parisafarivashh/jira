from rest_framework import status
from rest_framework.response import Response

from .models import RoomMember


def check_room_member(room, user):
    room_member = RoomMember.objects.get(
        room_id=room,
        member_id=user,
    )

    if room_member is None:
        return Response(
            dict(detail='You are not member of room'),
            status=status.HTTP_400_BAD_REQUEST
        )

