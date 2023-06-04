# django_celery/celery.py

import os
from kombu import Queue, Exchange

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jira.settings")
celery_app = Celery("jira")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.conf.task_queues = [
    Queue(
        'jira_celery_task',
        Exchange('jira_celery_task'),
        routing_key='jira_celery_task',
        queue_arguments={'x-max-priority': 10},
    ),
]
celery_app.conf.CELERY_DEFAULT_QUEUE = 'jira_celery_task'
celery_app.autodiscover_tasks()

