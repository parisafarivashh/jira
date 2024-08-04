from django.db.models import Count
from django.db.models.functions import TruncMinute
from django.shortcuts import render

from .models import ObjectViewed
from rest_framework.views import APIView


class AnalyticsDashboard(APIView):
    """from django.db.models.functions import (
         TruncDate,
         TruncDay,
         TruncHour,
         TruncMinute,
         TruncSecond,
     )
    """
    def get(self, request, *args, **kwargs):
        result_list = ObjectViewed.objects \
            .annotate(minute=TruncMinute('time')) \
            .values('minute', 'user_id') \
            .annotate(request_count=Count('id')) \
            .order_by('-minute', '-request_count')

        return render(request, 'dashbord.html', {'results': result_list})

