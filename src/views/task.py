import traceback

import ujson
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Task
from ..serializers import TaskSerializer
from jira import logger

from analytics.mixins import SignalModelViewSet


class TaskView(SignalModelViewSet, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tasks = Task.objects \
            .filter(
                Q(manager=self.request.user) |
                Q(created_by=self.request.user)
            )
        return tasks

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=True)

    def destroy(self, request, *args, **kwargs):
        try:
            self.get_object().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            logger.error(
                ujson.dumps(dict(
                    message=exc.__doc__,
                    stackTrace=traceback.format_exc(),
                ))
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)

