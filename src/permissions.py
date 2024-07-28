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
        if seen.count() == 0:
            return True


class EditOwnMessage(BasePermission):
    message = 'Can Not Edit Message'

    def has_object_permission(self, request, view, obj):
        if obj.sender_id == request.user:
            return True


class EditOwnAssignment(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.member == request.user or obj.created_by == request.user:
            return True

