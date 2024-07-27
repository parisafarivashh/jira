from datetime import datetime

from django.db import models


class BaseClassMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    removed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        if self.removed_at is not None:
            raise ValueError('Object is already deleted')

        self.removed_at = datetime.utcnow()
        self.save(update_fields=['removed_at'])

    def restore(self):
        self.removed_at = None
        self.save(update_fields=['removed_at'])


