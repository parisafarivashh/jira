from django.urls import path

from .views import CreateProjectView, ProjectView

urlpatterns = [
    path('project', CreateProjectView.as_view(), name='create_project'),
    path('project/<int:id>', ProjectView.as_view(), name='update_or_delete_project'),
    path('project/all', ProjectView.as_view(), name='list_project'),
]

