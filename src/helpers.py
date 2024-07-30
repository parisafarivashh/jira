from rest_framework import status
from rest_framework.exceptions import ValidationError
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
    if RoomMember.objects.is_room_member(room_id=room.id, member_id=user.id) \
            is False:
        raise ValidationError(detail=dict(detail='You are not member of room'))

    # try:
    #     RoomMember.objects.get(
    #         room_id=room,
    #         member_id=user,
    #     )
    # except RoomMember.DoesNotExist:
    #   raise ValidationError(detail=dict(detail='You are not member of room'))


