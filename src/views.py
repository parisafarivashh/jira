from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, \
    UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, Message
from .permissions import SeenOwnMessagePermission, SeenPermission
from .serializers import ProjectSerializer, UpdateProjectSerializer, \
    SeenMessageSerializer


# region project view
class CreateProjectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

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
class SeenMessageView(UpdateAPIView):
    permission_classes = [
        IsAuthenticated,
        SeenOwnMessagePermission,
        SeenPermission
    ]
    serializer_class = SeenMessageSerializer
    queryset = Message.objects.all()
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super(SeenMessageView, self).get_serializer_context()
        context.update({'request': self.request})
        return context
# endregion

