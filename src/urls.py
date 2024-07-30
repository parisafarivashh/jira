from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateProjectView, ProjectView, TaskView, AssignmentView, \
    AssignmentUpdateView, ListAndSendMessageView, ListMemberSeenMessageView, \
    MessageView, RoomSummaryView

router = DefaultRouter()
router.register('message', MessageView, basename='messageView')
router.register('task', TaskView, basename='taskView')


urlpatterns = [
    path('projects', CreateProjectView.as_view(), name='create_list_project'),
    path('projects/<int:id>', ProjectView.as_view(), name='update_or_delete_project'),
    path('room/<int:id>/message', ListAndSendMessageView.as_view(), name='send_or_list_message'),
    path('room/<int:id>/summary', RoomSummaryView.as_view(), name='room_summary'),
    path('message/<int:id>/seen/members', ListMemberSeenMessageView.as_view(), name='members_seen_message'),


    path('assignment/', AssignmentView.as_view(), name='assignment_view'),
    path('assignment/<int:id>/', AssignmentUpdateView.as_view(), name='assignment_view'),

    path('', include(router.urls)),
]

