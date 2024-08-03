from rest_framework.generics import GenericAPIView

from analytics.signals import object_view_signal


class SignalModelMixin(GenericAPIView):

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.method in ['GET', 'PATCH', 'PUT', 'DELETE']:
            instance = self.get_object()
            object_view_signal.send(
                sender=instance.__class__,
                instance=instance,
                request=request,
                user=request.user,
            )
        return response
