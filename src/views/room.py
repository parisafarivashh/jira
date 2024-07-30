from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import SummarySerializer
from ..tasks import summary_room


class RoomSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer

    def get(self, request, id=None):
        summary_room().delay(request.user.id, id)
        return Response(status=status.HTTP_200_OK)

