from django.db.models import Q
from django_filters import FilterSet, filters

from .models import Message, Assignment, Project, Task


class MessageFilterSet(FilterSet):
    entity_name = filters.CharFilter(field_name="metadata__entityName", lookup_expr="exact")  # icontains

    class Meta:
        model = Message
        fields = ['entity_name']


class AssignmentFilterSet(FilterSet):
    time = filters.CharFilter(method='filter_by_time')

    def filter_by_time(self, queryset, name, value):
        start_time = value
        end_time = value
        return queryset.filter(Q(start_date=start_time) | Q(end_date=end_time))

    class Meta:
        model = Assignment
        fields = '__all__'


class ProjectFilterSet(FilterSet):
    manager_name = filters.CharFilter(field_name='manager__title', lookup_expr='icontains')

    class Meta:
        model = Project
        fields = '__all__'


class TaskFilterSet(FilterSet):
    title = filters.CharFilter(method='search_by_title')

    def search_by_title(self, queryset, name, value):
        return queryset.filter(
            Q(manager__title__icontains=value) |
            Q(project__title__icontains=value) |
            Q(created_by__title__icontains=value)
        )

    class Meta:
        model = Task
        fields = '__all__'