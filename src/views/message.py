from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg import openapi

from ..helpers import check_room_member
from ..models import Message, Room
from ..permissions import SeenOwnMessagePermission, SeenPermission, \
    EditOwnMessage
from ..serializers import SeenMessageSerializer, EditMessageSerializer, \
    MessageSerializer


class MessageView(viewsets.GenericViewSet):
    queryset = Message.objects.all()

    @action(detail=True, url_path='see', methods=['patch'],
            serializers_class=SeenMessageSerializer)
    def see(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=instance)
        serializer.is_valis(raise_exception=True)
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
            self.permission_classes = [
                IsAuthenticated,
                SeenOwnMessagePermission,
                SeenPermission
            ]

        if self.action == 'edit':
            self.permission_classes = [
                IsAuthenticated,
                EditOwnMessage,
            ]
        else:
            self.permission_classes = [IsAuthenticated]
        return self.permission_classes

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MessageSerializer


class ListAndSendMessageView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_seen']

    @swagger_auto_schema(
        operation_id="message_create",
        responses={200: openapi.Response("Success response description")},
    )
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="message_list",
        responses={200: openapi.Response("Success response description")},
    )
    def get(self, request, *args, **kwargs):
        room = get_object_or_404(Room, kwargs['id'])
        check_room_member(room, request.user)

        queryset = Message.objects.filter(room=room)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


