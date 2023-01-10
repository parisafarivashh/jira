from django.urls import path

from .views import CreateProjectView, ProjectView, SeenMessageView

urlpatterns = [
    path('project', CreateProjectView.as_view(), name='create_project'),
    path('project/<int:id>', ProjectView.as_view(), name='update_or_delete_project'),
    path('project/all', ProjectView.as_view(), name='list_project'),

    path('message/<int:id>', SeenMessageView.as_view(), name='seen_message'),

]

