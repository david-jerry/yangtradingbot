# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from celery import Celery


def create_worker():
    _celery = Celery(__name__, broker="redis://localhost:6379/0")
    _celery.conf.update(
        CELERY_IMPORTS=["tasks"],
        ENABLE_UTC=True,
        BROKER_USE_SSL=True,
        # CELERY_INCLUDE=["tasks"],
    )

    return _celery


worker = create_worker()
