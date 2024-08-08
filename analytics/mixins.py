from django.db import transaction
from rest_framework.generics import GenericAPIView

from analytics.signals import object_view_signal
from rest_framework.viewsets import GenericViewSet


class SignalModelMixin(GenericAPIView):

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method in ['GET', 'PATCH', 'PUT']:
            instance = self.get_object()
            object_view_signal.send(
                sender=instance.__class__,
                instance=instance,
                request=request,
                user=request.user,
            )
        return response


class SignalModelViewSet(GenericViewSet):

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        if request.method in ['PUT', 'PATCH']:
            instance = self.get_object()
            object_view_signal.send(
                sender=instance.__class__,
                instance=instance,
                request=request,
                user=request.user
            )
        return super().dispatch(request, *args, **kwargs)

