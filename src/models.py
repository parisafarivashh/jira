from datetime import datetime

import django
from django.db import models

from jira.settings import AUTH_USER_MODEL
from rest_framework.exceptions import NotFound

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

    @staticmethod
    def get_room_object(room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound
        return room


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

    @staticmethod
    def get_message_object(message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            raise NotFound
        return message


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


class RoomMember(BaseClass):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name='room_member'
    )
    member_id = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name='room_member'
    )
    latest_seen_message_id = models.ForeignKey(
        Message,
        on_delete=models.PROTECT,
        related_name='latest_message_room',
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'room_member'
        constraints = [
            models.UniqueConstraint(
                fields=['room_id', 'member_id'],
                name='unique_room_member',
            )
        ]


class Task(BaseClass, SoftDelete):

    class Status(models.TextChoices):
        to_do = 'toDo'
        assign = 'assign'
        in_progress = 'inProgress'
        done = 'done'

    id = models.AutoField(primary_key=True)
    status = models.CharField(
        choices=Status.choices,
        default=Status.to_do,
        max_length=12,
    )
    title = models.CharField(unique=True, max_length=100)
    project_id = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='tasks',
    )
    public_room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='publicRoomTask'
    )
    private_room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='privateRoomTask'
    )
    manager_id = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='managerTask'
    )
    created_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='createdTask'
    )

    class Meta:
        db_table = 'task'

    # def update_status(self):
    #     status = Assignment.objects.filter(task_id=self.id).value('status')
    #     print(status)


class Assignment(BaseClass, SoftDelete):
    class Status(models.TextChoices):
        assign = 'assign'
        in_progress = 'inProgress'
        done = 'done'

    id = models.AutoField(primary_key=True)
    description = models.CharField(
        unique=True,
        max_length=250,
        blank=True,
        null=True
    )
    member_id = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='assignment'
    )
    public_room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='publicRoomAssignment'
    )
    private_room_id = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='privateRoomAssignment'
    )
    status = models.CharField(
        choices=Status.choices,
        default=Status.assign,
        max_length=12,
    )
    task_id = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    start_date = models.DateTimeField(blank=False, null=False)
    end_date = models.DateTimeField(blank=False, null=False)
    estimate_hours = models.IntegerField(default=0)

    class Meta:
        db_table = 'assignment'

