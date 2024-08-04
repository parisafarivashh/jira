# Assuming you are editing the project's urls.py or the app's urls.py that includes admin URLs
from django.urls import path
from .views import AnalyticsDashboard


urlpatterns = [
    path('', AnalyticsDashboard.as_view(), name='analytics-dashboard'),
]
