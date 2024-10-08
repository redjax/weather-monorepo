from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from .settings import CELERY_SETTINGS
from .tasks.scheduled import (
    TASK_SCHEDULE_6h_weather_forecast_check,
    TASK_SCHEDULE_10m_current_weather_row_count,
    TASK_SCHEDULE_15m_current_weather_check,
)

from celery import Celery, current_app
from celery.result import AsyncResult

INCLUDE_TASK_PATHS: list[str] = [
    "celeryapp.tasks.weather_apis.weatherapi",
    "celeryapp.tasks.scheduled",
]


def print_discovered_tasks() -> list[str]:
    current_app.loader.import_default_modules()

    tasks: list[str] = list(
        sorted(name for name in current_app.tasks if not name.startswith("celery."))
    )

    log.debug(f"Discovered [{len(tasks)}] Celery task(s): {[t for t in tasks]}")

    return tasks


def return_celery_broker_url(
    user: str,
    password: str,
    port: t.Union[int, str],
    host: str = "localhost",
    proto: str = "amqp",
) -> str:
    if user and password:
        broker_url: str = f"{proto}://{user}:{password}@{host}"
    else:
        broker_url: str = f"{proto}://{host}"

    if port:
        broker_url = f"{broker_url}:{port}"

    log.debug(f"Broker URL: {broker_url}")

    return broker_url


def return_celery_backend_url(
    host: str, port: t.Union[int, str], proto: str = "redis"
) -> str:
    backend_url: str = f"{proto}://{host}:{port}"

    if proto == "redis":
        backend_url: str = f"{backend_url}/0"

    return backend_url


BROKER_URL: str = return_celery_broker_url(
    user=CELERY_SETTINGS.get("CELERY_BROKER_USER", default=""),
    password=CELERY_SETTINGS.get("CELERY_BROKER_PASSWORD", default=""),
    host=CELERY_SETTINGS.get("CELERY_BROKER_HOST", default="localhost"),
    port=CELERY_SETTINGS.get("CELERY_BROKER_PORT", default=None),
)

BACKEND_URL: str = return_celery_backend_url(
    host=CELERY_SETTINGS.get("CELERY_BACKEND_HOST", default=""),
    port=CELERY_SETTINGS.get("CELERY_BACKEND_PORT", default=None),
)

celery_app = Celery(
    "celeryapp",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=INCLUDE_TASK_PATHS,
)

celery_app.conf.update(
    timzone=CELERY_SETTINGS.get("CELERY_TZ", default="Etc/UTC"), enable_utc=True
)


## Periodic jobs
@celery_app.on_after_finalize.connect
def scheduled_tasks(sender, **kwargs):
    ## Configure celery beat schedule
    celery_app.conf.beat_schedule = {
        **TASK_SCHEDULE_15m_current_weather_check,
        **TASK_SCHEDULE_10m_current_weather_row_count,
        **TASK_SCHEDULE_6h_weather_forecast_check,
    }


print_discovered_tasks()


def check_task(task_id: str = None, app: Celery = celery_app) -> AsyncResult | None:
    """Check a Celery task by its ID.

    Params:
        task_id (str): The Celery task's ID.
        app (Celery): An initialized Celery app.

    Returns:
        (AsyncResult): Returns a Celery `AsyncResult` object, if task is found.
        (None): If no task is found or an exception occurs.

    """
    assert task_id, ValueError("Missing a Celery task_id")
    task_id: str = f"{task_id}"

    log.info(f"Checking Celery task '{task_id}'")
    try:
        task_res: AsyncResult = app.AsyncResult(task_id)

        return task_res
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting task by ID '{task_id}'. Details: {exc}"
        )
        log.error(msg)

        return None
