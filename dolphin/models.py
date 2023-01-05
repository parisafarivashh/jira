from django.db import models

from maestro.settings import AUTH_USER_MODEL

Member = AUTH_USER_MODEL


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='owner'
    )

    class Meta:
        db_table = 'room'


class Project(models.Model):

    class Status(models.TextChoices):
        active = 'active'
        on_hold = 'on-hold'
        queued = 'queued'
        done = 'done'

    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, blank=False, null=False)
    manager_id = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='manager'
    )
    title = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        choices=Status.choices,
        default=Status.active,
        max_length=10
    )
    created_at = models.DateTimeField(auto_now_add=True)
    public_room_id = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='pubic_room'
    )
    private_room_id = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='private_room'
    )
    created_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='createdBy'
    )

    class Meta:
        db_table = 'project'

