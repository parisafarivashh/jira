from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, \
    UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project
from .serializers import ProjectSerializer, UpdateProjectSerializer


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
        elif self.request.method == 'PUT' or self.request.method == 'PATCH':
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

    # def delete(self, request, id=None):
    #     if id:
              # bayad har chizi ke be in marbote ham delete beshe
    #         return self.destroy(request, id)
    #     else:
    #         raise NotFound


