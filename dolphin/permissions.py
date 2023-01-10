from rest_framework.permissions import BasePermission

from .models import MemberMessageSeen


class SeenOwnMessagePermission(BasePermission):
    message = 'Can Not See Own Message'

    def has_object_permission(self, request, view, obj):
        if obj.sender_id != request.user:
            return True


class SeenPermission(BasePermission):
    message = 'Message Is Already Seen'

    def has_object_permission(self, request, view, obj):
        seen = MemberMessageSeen.objects.filter(
            message_id=obj.id,
            member_id=request.user
        )
        if seen is not None:
            return False
