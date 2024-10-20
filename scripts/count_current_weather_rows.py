from __future__ import annotations

import logging
import time
import typing as t

log = logging.getLogger(__name__)

from celery.result import AsyncResult
from celeryapp import CELERY_SETTINGS, celery_app, check_task
from celeryapp.tasks.weather_apis.weatherapi import (
    task_count_current_weather_rows,
)
from core.setup import setup_database, setup_logging
from weatherapi_client.settings import WEATHERAPI_SETTINGS

def run(task_check_sleep: int = 5, location_name: str = None):
    task_result: AsyncResult = task_count_current_weather_rows.delay()

    while not check_task(task_id=task_result.task_id, app=celery_app).ready():
        log.info(f"Task {task_result.task_id} is in state [{task_result.state}]")

        if task_result.state == "FAILURE":
            log.error(f"Error executing task {task_result.id}.")

            return None

        if task_check_sleep:
            log.info(f"Sleeping for [{task_check_sleep}] second(s)...")
            time.sleep(task_check_sleep)

    ## Task is ready
    log.info(
        f"Task {task_result.task_id} ready=True. State: {check_task(task_id=task_result.task_id, app=celery_app).state}"
    )

    log.info("Finish counting current weather rows")

    if task_result.result is None:
        log.warning("Result is None, an error may have occurred")

        return None
    else:
        if task_result and task_result.result:
            log.debug(f"Results: {task_result.result}")
            log.debug(f"task_result.result type: ({type(task_result.result)})")

            return task_result.result
        else:
            log.warning(
                "Task's result field is None. This could indicate an error, but may be normal operation."
            )


if __name__ == "__main__":
    setup_logging()

    run(task_check_sleep=2)
