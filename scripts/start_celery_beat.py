from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from celery import Celery
from celeryapp import CELERY_SETTINGS, celery_app
from core.setup import setup_database, setup_logging

def run(log_level: str = "INFO"):
    log.info("Start Celery beat")

    log_level = log_level.upper()

    try:
        celery_app.Beat(loglevel=log_level).run()
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception starting Celery beat. Details: {exc}"
        log.error(msg)

        raise exc


if __name__ == "__main__":
    setup_logging()
    setup_database()

    try:
        run(log_level=CELERY_SETTINGS.get("CELERY_BEAT_LOG_LEVEL", default="INFO"))
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery beat. Details: {exc}"
        log.error(msg)
        exit(1)

    log.info("Gracefully exiting Celery beat.")
