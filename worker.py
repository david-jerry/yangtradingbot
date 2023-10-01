# -*- coding: utf-8 -*-
"""
   Description:
        -
        -
"""
from celery import Celery


def create_worker():
    _celery = Celery(__name__, broker="redis://:p9068b2095a4b8c7eba54981c1ed8768f2636ba8086ac6ca298580b6d40896cae@ec2-52-202-215-144.compute-1.amazonaws.com:18509/0")
    _celery.conf.update(
        CELERY_IMPORTS=["tasks"],
        ENABLE_UTC=True,
        BROKER_USE_SSL=True,
        # CELERY_INCLUDE=["tasks"],
    )

    return _celery


worker = create_worker()
