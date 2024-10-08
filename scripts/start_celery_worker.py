from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from celery import current_app
from celeryapp import CELERY_SETTINGS, celery_app
from core.setup import setup_database, setup_logging

def run(worker_log_level: str = "INFO", uid: int = 0, gid: int = 0):
    log.info("Auto-discovering Celery tasks.")
    celery_app.autodiscover_tasks(["celeryapp"])

    worker_log_level = worker_log_level.upper()

    try:
        worker = celery_app.worker_main(
            argv=[
                "worker",
                f"--loglevel={worker_log_level}",
                f"--uid={uid}",
                f"--gid={gid}",
            ]
        )
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception getting Celery worker. Details: {exc}"
        log.error(msg)

        raise exc

    log.info("Starting Celery worker")
    try:
        worker.start()
    except Exception as exc:
        msg = (
            f"({type(exc)}) Unhandled exception starting Celery worker. Details: {exc}"
        )
        log.error(msg)

        raise exc


if __name__ == "__main__":
    setup_logging()
    setup_database()

    run(
        worker_log_level=CELERY_SETTINGS.get("CELERY_WORKER_LOG_LEVEL", default="INFO"),
        uid=CELERY_SETTINGS.get("CELERY_WORKER_UID", 0),
        gid=CELERY_SETTINGS.get("CELERY_WORKER_GID", 0),
    )

    log.info("Gracefully exiting Celery worker.")
