from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.dispatch import receiver
from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.models import TimescaleModel

from .signals import object_view_signal
from .utils import get_client_ip

# Create your models here.

User = get_user_model()


class ObjectViewed(TimescaleModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True,
                             null=True, db_index=False)
    ip_address = models.CharField(max_length=120, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=False)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    time = TimescaleDateTimeField(interval="1 day", auto_now_add=True)

    def __str__(self):
        return f' {self.content_object} viewed {self.time}'

    class Meta:
        db_tablespace = 'my_tablespace'
        ordering = ['-time']
        indexes = [models.Index(fields=['id', 'time'], name='id_time_idx', db_tablespace='my_tablespace')]
        verbose_name = 'Object Viewed'
        verbose_name_plural = 'Objects Viewed'


@receiver(signal=object_view_signal)
def object_viewed_receiver(sender, instance, request, user, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(sender)

    ObjectViewed.objects.create(
        user=user,
        content_type=c_type,
        object_id=instance.id,
        ip_address=get_client_ip(request)
    )

