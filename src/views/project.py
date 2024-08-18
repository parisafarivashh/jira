import traceback

import ujson
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin

from ..filtersets import ProjectFilterSet
from ..models import Project
from ..serializers import ProjectSerializer, UpdateProjectSerializer
from jira import logger

from analytics.mixins import SignalModelMixin


class CreateProjectView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    django_filters = [DjangoFilterBackend]
    filterset_class = ProjectFilterSet

    def get_queryset(self):
        project = Project.objects.filter(
            Q(status='active') & Q(removed_at=None)
        ).all()
        return project

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context=dict(request=request),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ProjectView(
    SignalModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        project = Project.objects.filter(
            Q(status='active') & Q(removed_at=None)
        ).all()
        return project

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectSerializer
        else:
            return UpdateProjectSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, partial=True, *args, **kwargs)

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

