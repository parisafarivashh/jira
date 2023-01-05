from django.db import models

from maestro.settings import AUTH_USER_MODEL

Member = AUTH_USER_MODEL


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='room'
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
        related_name='managerProject'
    )
    title = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        choices=Status.choices,
        default=Status.active,
        max_length=10
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    public_room_id = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='publicProject'
    )
    private_room_id = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='privateProject'
    )
    created_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='ownerProject'
    )

    class Meta:
        db_table = 'project'


class Message(models.Model):

    class Type(models.TextChoices):
        message = 'message'
        alert = 'alert'

    id = models.AutoField(primary_key=True)
    type = models.CharField(
        max_length=10,
        default=Type.message,
        choices=Type.choices
    )
    sender_id = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    room_id = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    body = models.TextField()
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'message'

