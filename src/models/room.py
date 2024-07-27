from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from rest_framework.exceptions import NotFound

from ..models import BaseClassMixin, SoftDeleteMixin


member = get_user_model()


class Room(BaseClassMixin, SoftDeleteMixin):
    title = models.CharField(
        max_length=50,
        validators=[
            MaxLengthValidator(50),
            MinLengthValidator(1),
        ]
    )
    type = models.CharField(
        max_length=50,
        validators=[
            MaxLengthValidator(50),
            MinLengthValidator(1)
        ]
    )
    private = models.BooleanField(default=False)
    owner = models.ForeignKey(member, on_delete=models.CASCADE)

    class Meta:
        db_table = 'room'
        ordering = ['title']

    def get_object(self, room_id: int):
        try:
            room = self.objects.get(id=room_id)
            return room
        except self.DoesNotExist:
            raise NotFound
