from django.db.models import Q
from django_filters import FilterSet, filters

from .models import Message, Assignment


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
        fields = ['time']
