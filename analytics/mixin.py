from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden

from .signals import object_view_signal


class ObjectViewMixin:

    def dispatch(self, request, *args, **kwargs):
        # Initialize instance as None for safe handling in case of POST requests
        instance = None

        if not request.user.is_authenticated:
            return HttpResponseForbidden("User is not authenticated")

        # Attempt to retrieve the object only in cases that likely require it
        if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            try:
                instance = self.get_object()
            except (AssertionError, AttributeError, ObjectDoesNotExist):
                print(instance)
                instance = None

        # Send the signal if an instance was found or for POST requests
        if instance is not None:
            print('1111111111111111111111111111')
            user = request.user
            print(user)
            object_view_signal.send(sender=instance.__class__,
                                    instance=instance, request=request, user=user)

        # Continue with the usual dispatch
        response = super().dispatch(request, *args, **kwargs)
        return response
