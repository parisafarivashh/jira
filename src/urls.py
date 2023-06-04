from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateProjectView, ProjectView, ListAndSendMessageView, \
    MessageView, ListMemberSeenMessageView, TaskView, AssignmentView, \
    AssignmentUpdateView

router = DefaultRouter()
router.register('message', MessageView, basename='messageView')
router.register('task', TaskView, basename='taskView')


urlpatterns = [
    path('project', CreateProjectView.as_view(), name='create_project'),
    path('project/<int:id>', ProjectView.as_view(), name='update_or_delete_project'),
    path('project/all', ProjectView.as_view(), name='list_project'),
    path('room/<int:id>/message', ListAndSendMessageView.as_view(), name='send_or_list_message'),
    path('message/<int:id>/seen/members', ListMemberSeenMessageView.as_view(), name='members_seen_message'),


    path('assignment/', AssignmentView.as_view(), name='assignment_view'),
    path('assignment/<int:id>/', AssignmentUpdateView.as_view(), name='assignment_view'),

    path('', include(router.urls)),
]

