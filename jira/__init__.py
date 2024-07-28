# django_celery/__init__.py
import logging

from .celery import celery_app

__all__ = ("celery_app",)
logger = logging.getLogger('jira')

