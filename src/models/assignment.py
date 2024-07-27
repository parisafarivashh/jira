from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import BaseClassMixin, SoftDeleteMixin, Room, Task


Member = get_user_model()


class Assignment(BaseClassMixin, SoftDeleteMixin):
    class Status(models.TextChoices):
        ASSIGN = 'assign'
        IN_PROGRESS = 'in_progress'
        DONE = 'done'

    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='assignments')
    public_room = models.OneToOneField(Room, on_delete=models.PROTECT, related_name='public_assignments')
    private_room = models.OneToOneField(Room, on_delete=models.PROTECT, related_name='private_assignment')
    status = models.CharField(
        choices=Status.choices,
        default=Status.ASSIGN,
        max_length=12,
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    created_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='created_assignments'
    )
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    estimate_hours = models.IntegerField(default=0)

    class Meta:
        db_table = 'assignment'


@receiver(post_save, sender=Assignment)
def update_status_of_assignment(sender, instance, created, **kwargs):
    if instance.estimate_hours > 0 and instance.end_date is not None and \
            instance.end_date.date() == datetime.today().date():
        Assignment.objects.filter(id=instance.id).update(status='done')

    elif instance.estimate_hours > 0:
        Assignment.objects.filter(id=instance.id).update(status='in_progress')

    else:
        Assignment.objects.filter(id=instance.id).update(status='assign')

