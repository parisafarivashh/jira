from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, \
    UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import check_is_room_member
from .models import Project, Message, Room
from .permissions import SeenOwnMessagePermission, SeenPermission, \
    EditOwnMessage
from .serializers import ProjectSerializer, UpdateProjectSerializer, \
    SeenMessageSerializer, EditMessageSerializer, CreateMessageSerializer


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

    def get_serializer_context(self):
        context = super(MessageView, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateMessageSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        room = Room.get_room_object(kwargs['id'])
        user = request.user

        if room.private is True:
            if check_is_room_member(room, user) is False:
                return Response(
                    dict(detail='You are not member of room'),
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.serializer_class(
            context={'request': request, 'room_id': room},
            data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

# endregion

