from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Room
from ..serializers import SummarySerializer
from ..tasks import summary_room
from analytics.mixins import SignalModelMixin


class RoomSummaryView(SignalModelMixin, APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    queryset = Room.objects.all()
    lookup_field = 'id'

    def get(self, request, id=None):
        summary_room.apply_async((request.user.id, id),)
        return Response(status=status.HTTP_200_OK)

