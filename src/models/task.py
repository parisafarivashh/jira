from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Manager

from . import BaseClassMixin, SoftDeleteMixin, Project, Room


Member = get_user_model()


class TaskManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(removed_at__isnull=True)


class Task(BaseClassMixin, SoftDeleteMixin):

    class Status(models.TextChoices):
        TODO = 'to_do'
        ASSIGN = 'assign'
        IN_PROGRESS = 'in_progress'
        DONE = 'done'

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    title = models.CharField(unique=True, max_length=100)
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='tasks')
    public_room = models.OneToOneField(Room, on_delete=models.PROTECT, related_name='public_tasks')
    private_room = models.OneToOneField(Room, on_delete=models.PROTECT, related_name='private_tasks')
    manager = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='manage_tasks')
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='create_tasks')

    objects = TaskManager()

    class Meta:
        db_table = 'task'
        verbose_name = "UndeletedTask"
        verbose_name_plural = "UndeletedTasks"


class TaskProxy(Task):

    objects = Manager()

    class Meta:
        proxy = True
        verbose_name = "DeletedTask"
        verbose_name_plural = "DeletedTasks"

