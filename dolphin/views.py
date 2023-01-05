from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CreateProjectSerializer


class CreateProjectView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateProjectSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

