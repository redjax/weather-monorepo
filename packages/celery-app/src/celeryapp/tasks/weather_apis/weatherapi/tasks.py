import logging
from pathlib import Path
import time
import typing as t

log = logging.getLogger(__name__)

import weatherapi_client
from core.depends.db_depends import get_session_pool
from celeryapp.celery_main import celery_app


@celery_app.task(name="request_current_weather")
def task_current_weather(
    location: str,
) -> dict[str, weatherapi_client.domain.CurrentWeatherOut]:
    if location is None:
        log.warning(
            "No location detected. Set a WEATHERAPI_LOCATION_NAME environnment variable with a value of a location to search WeeatherAPI for."
        )

        return None

    log.info("Getting current weather in background")

    try:
        current_weather: weatherapi_client.domain.CurrentWeatherOut = (
            weatherapi_client.client.get_current_weather(location=location)
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error running background task to get current weather. Details: {exc}"
        log.error(msg)

        raise exc

    if current_weather:
        log.info(f"Current weather: {current_weather}")
        return {"current_weather": current_weather.model_dump()}
    else:
        log.warning("Current weather object is None. An error may have occurred.")
        return {"current_weather": None}


@celery_app.task(name="current_weather_count")
def task_count_current_weather_rows():
    session_pool = get_session_pool()

    with session_pool() as session:
        repo = weatherapi_client.domain.CurrentWeatherRepository(session=session)

        rows = repo.count()

    log.info(f"Found [{rows}] row(s) in the current weather table")

    return {"count": rows}


@celery_app.task(name="request_weather_forecast")
def task_weather_forecast(
    location: str,
) -> dict[str, weatherapi_client.domain.weather.forecast.ForecastJSONOut]:
    if location is None:
        log.warning(
            "No location detected. Set a WEATHERAPI_LOCATION_NAME environnment variable with a value of a location to search WeeatherAPI for."
        )

        return None

    log.info("Getting weather forecast in background")

    try:
        weather_forecast: weatherapi_client.domain.weather.forecast.ForecastJSONOut = (
            weatherapi_client.client.get_weather_forecast(location=location)
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error running background task to get weather forecast. Details: {exc}"
        log.error(msg)

        raise exc

    if weather_forecast:
        log.info(f"Weather forecast: {weather_forecast}")
        return {"weather_forecast": weather_forecast.model_dump()}
    else:
        log.warning("Weather forecast object is None. An error may have occurred.")
        return {"weather_forecast": None}


@celery_app.task(name="weather_forecast_count")
def task_count_weather_forecast_rows():
    session_pool = get_session_pool()

    with session_pool() as session:
        repo = weatherapi_client.domain.ForecastJSONRepository(session=session)

        rows = repo.count()

    log.info(f"Found [{rows}] row(s) in the weather forecast table")

    return {"count": rows}
