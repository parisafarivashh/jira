from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, \
    UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .designPattern.message import MessageFacade, MessageFactory
from .helpers import check_room_member
from .models import Project, Message, Room, MemberMessageSeen, Task
from .permissions import SeenOwnMessagePermission, SeenPermission, \
    EditOwnMessage
from .serializers import ProjectSerializer, UpdateProjectSerializer, \
    SeenMessageSerializer, EditMessageSerializer, MessageSerializer, \
    MemberMessageSeenSerializer, TaskSerializer


# region project view
class CreateProjectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class ProjectView(GenericAPIView, RetrieveModelMixin, ListModelMixin,
                  UpdateModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Project.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectSerializer
        else:
            return UpdateProjectSerializer

    def get(self, request, id=None):
        if id:
            return self.retrieve(request, id)
        else:
            return self.list(request)

    def put(self, request, id):
        return self.update(request, id)

    def patch(self, request, id):
        return self.update(request, id, partial=True)

    def delete(self, request, id=None):
        if id:
            try:
                Project.objects.get(id=id).soft_delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except Exception as ex:
                return Response(
                    data=str(ex), status=status.HTTP_400_BAD_REQUEST
                )
        else:
            raise NotFound
# endregion


# region message view
class MessageView(viewsets.ModelViewSet):
    queryset = Message.objects.all()

    @action(detail=True, url_path='see', methods=['patch'],
            serializer_class=SeenMessageSerializer)
    def see(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='edit', methods=['patch'],
            serializer_class=EditMessageSerializer)
    def edit(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'see':
            permission_classes = [
                IsAuthenticated,
                SeenOwnMessagePermission,
                SeenPermission
            ]
        elif self.action == 'edit':
            permission_classes = [
                IsAuthenticated,
                EditOwnMessage,
            ]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MessageSerializer

    def get_serializer_context(self):
        context = super(MessageView, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class ListAndSendMessageView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_seen']

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        room = Room.get_room_object(kwargs['id'])

        check_room_member(room, request.user)

        serializer = self.serializer_class(
            context={'request': request, 'room_id': room},
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        message = MessageFactory().get_message(serializer.data['id'])

        MessageFacade(
            message=message,
            room=room,
            user=request.user
        ).send_message()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        room = Room.get_room_object(kwargs['id'])
        check_room_member(room, request.user)

        queryset = Message.objects.filter(room_id=room)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListMemberSeenMessageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberMessageSeenSerializer

    def get(self, request, *args, **kwargs):
        message = Message.get_message_object(kwargs['id'])

        queryset = MemberMessageSeen.objects.filter(message_id=message.id)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# endregion


class CreateTask(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

