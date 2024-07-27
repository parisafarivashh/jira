from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from ..models import BaseClassMixin, SoftDeleteMixin, Room


member = get_user_model()


class Project(BaseClassMixin, SoftDeleteMixin):

    class Status(models.TextChoices):
        ACTIVE = 'active'
        ON_HOLD = 'on_hold'

    title = models.CharField(max_length=50, unique=True)
    description = models.CharField(
        max_length=150,
        validators=[
            MaxLengthValidator(150),
            MinLengthValidator(1)
        ]
    )
    manager = models.ForeignKey(member, on_delete=models.CASCADE, related_name='managed_project')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    public_room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='public_project')
    private_room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='private_project')
    created_by = models.ForeignKey(member, on_delete=models.PROTECT, related_name='created_project')

    class Meta:
        db_table = 'project'