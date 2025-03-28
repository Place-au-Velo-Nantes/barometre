import logging

from celery import shared_task

logger = logging.getLogger("celery")


@shared_task
def heartbeat_task():
    """A simple task that confirms that celery and celery beat are active."""
    logger.info("Celery hearbeat.")
