import traceback
import ujson
from celery import Task

from jira import logger


class MyTask(Task):
    max_retries = 10
    time_limit = None
    soft_time_limit = None
    acks_late = True
    default_retry_delay = 2

    def on_retry(
            self,
            exc: Exception,
            task_id: str,
            args: tuple,
            kwargs: dict,
            einfo: traceback,
    ) -> None:
        """Handle retry logging for a failed task.

        Args:
            self: The instance of the class containing this method.
            exc (Exception): The exception instance raised during task
                execution.
            task_id (str): The ID of the task being retried.
            args (tuple): The positional arguments passed to the task.
            kwargs (dict): The keyword arguments passed to the task.
            einfo (traceback): Traceback instance containing error information.

        Returns:
            None
        """
        if self.request.retries == 0:
            logger.error(ujson.dumps(dict(
                message=exc.__doc__,
                stackTrace=traceback.format_exc(),
                taskId=task_id,
            )))

