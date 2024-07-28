from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..models import Assignment
from ..permissions import EditOwnAssignment
from ..serializers import AssignmentSerializer, AssignmentUpdateSerializer


class AssignmentView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AssignmentSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Assignment.objects.is_user_assign(self.request.user)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AssignmentUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, EditOwnAssignment]
    serializer_class = AssignmentUpdateSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Assignment.objects.is_user_assign(self.request.user)

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        return super().update(request, partial=True)





