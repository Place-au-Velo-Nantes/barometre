"""Copyright 2025  Place au Vélo"""

# import logging
import os

# logger = logging.getLogger("django")


def this_is_celery():
    if os.getenv("RUNNING_IN_CELERY"):
        return True
    return False
