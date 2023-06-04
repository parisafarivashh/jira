from celery import Task


class MyTask(Task):
    max_retries = 100
    time_limit = None
    soft_time_limit = None
    acks_late = True
    default_retry_delay = 2

