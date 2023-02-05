from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateProjectView, ProjectView, ListAndSendMessageView, \
    MessageView, ListMemberSeenMessageView

router = DefaultRouter()
router.register('message', MessageView, basename='messageView')


urlpatterns = [
    path('project', CreateProjectView.as_view(), name='create_project'),
    path('project/<int:id>', ProjectView.as_view(), name='update_or_delete_project'),
    path('project/all', ProjectView.as_view(), name='list_project'),
    path('room/<int:id>/message', ListAndSendMessageView.as_view(), name='send_or_list_message'),
    path('message/<int:id>/seen/members', ListMemberSeenMessageView.as_view(), name='members_seen_message'),
    path('', include(router.urls)),
]

