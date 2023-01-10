from datetime import datetime

from django.db import models

from jira.settings import AUTH_USER_MODEL

Member = AUTH_USER_MODEL


class BaseClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDelete(models.Model):
    removed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        if self.removed_at is not None:
            raise ValueError('Object is already deleted.')
        self.removed_at = datetime.utcnow()
        self.save()

    def restore(self):
        self.removed_at = None
        self.save()


class Room(BaseClass, SoftDelete):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    private = models.BooleanField(default=False)
    owner = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='room'
    )

    class Meta:
        db_table = 'room'


class Project(BaseClass, SoftDelete):

    class Status(models.TextChoices):
        active = 'active'
        on_hold = 'on-hold'
        queued = 'queued'
        done = 'done'

    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, blank=False, null=False)
    manager_id = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='managerProject'
    )
    title = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        choices=Status.choices,
        default=Status.active,
        max_length=10
    )
    public_room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='publicProject'
    )
    private_room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='privateProject'
    )
    created_by = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='ownerProject'
    )

    class Meta:
        db_table = 'project'


class Message(BaseClass, SoftDelete):

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
        on_delete=models.PROTECT,
        related_name='messages'
    )
    room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='messages'
    )
    body = models.TextField()
    is_seen = models.BooleanField(default=False)

    class Meta:
        db_table = 'message'


class MemberMessageSeen(models.Model):
    id = models.AutoField(primary_key=True)
    message_id = models.ForeignKey(
        Message,
        on_delete=models.PROTECT,
        related_name='seen'
    )
    member_id = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='seenMessages'
    )

    class Meta:
        db_table = 'member_message_seen'
        constraints = [
            models.UniqueConstraint(
                fields=['message_id', 'member_id'],
                name='unique_member_message_seen',
            )
        ]

