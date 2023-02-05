from rest_framework import status
from rest_framework.response import Response

from .models import RoomMember

#
# def create_universal_filter(klass):
#     """
#     Creates filter class with all lookups  for all fields of given class
#     """
#     field_filters = dict((f, filters.ALL_LOOKUPS)
#                     for f in klass._meta.get_all_field_names())
#     print(field_filters)
#
#     class MyFilter(filters.FilterSet):
#         class Meta:
#             model = klass
#             fields = field_filters
#     return MyFilter
#
#
# class GenericFilterModelViewSet(viewsets.ModelViewSet):
#     """Allows all lookups on all fields"""
#
#     def __init__(self, *args, **kwargs):
#         self.filter_class = create_universal_filter(self.queryset.model)


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

