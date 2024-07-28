import traceback

import ujson
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Task
from ..serializers import TaskSerializer
from jira import logger


class TaskView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    lookup_field = 'id'

    def get_queryset(self):
        # todo : better ways? use queryset custom for filtering removed at
        #  every place
        tasks = Task.objects \
            .filter(removed_at=None) \
            .filter(
                Q(manager=self.request.user) |
                Q(created_by=self.request.user)
            ).all()
        return tasks

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def update(self, request, *args, **kwargs):
        return super().update(request, partial=True)

    def delete(self, request, *args, **kwargs):
        try:
            self.get_object().soft_delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            logger.error(
                ujson.dumps(dict(
                    message=exc.__doc__,
                    stackTrace=traceback.format_exc(),
                ))
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)

