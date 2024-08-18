import traceback

import ujson
from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from jira.paginations import LargeResultPagination

from ..filtersets import TaskFilterSet
from ..models import Task
from ..serializers import TaskSerializer
from jira import logger

from analytics.mixins import SignalModelViewSet

from ..serializers.task import TaskListSerializer


class TaskView(SignalModelViewSet, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    pagination_class = LargeResultPagination
    django_filters = [DjangoFilterBackend]
    filterset_class = TaskFilterSet
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            self.serializer_class = TaskListSerializer
        return self.serializer_class

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

    @action(detail=False, url_path='search', methods=['GET'])
    def search(self, request, *args, **kwargs):
        MINIMUM_MATCH_SCORE = 0.11
        search_key = request.query_params.get('search_key')
        if not search_key:
            raise ValidationError(detail={'error': 'SearchKey Does Not Exist'})

        # # Full-text search vectors and query
        # vectors = SearchVector('title', 'project__title')
        # search_qry = SearchQuery(search_key)
        #
        # # Full-text search query
        # full_text_results = self.get_queryset() \
        #     .annotate(score=SearchRank(vectors, search_qry)) \
        #     .filter(score__gte=MINIMUM_MATCH_SCORE) \
        #     .order_by('-score')
        #
        # partial_results = full_text_results
        # # If full-text search yields no results, fall back to partial match
        # if not full_text_results.exists():
        #     partial_results = self.get_queryset().filter(
        #         Q(title__icontains=search_key) |
        #         Q(project__title__icontains=search_key)
        #     )

        query = self.get_queryset()\
            .annotate(
                similarity=TrigramSimilarity('title', search_key) +
                TrigramSimilarity('project__title', search_key)
            ) \
            .filter(similarity__gte=MINIMUM_MATCH_SCORE) \
            .order_by('-similarity') \
            .all()

        serializer = self.serializer_class(query, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

