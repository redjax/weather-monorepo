from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)

from weatherapi_client.domain.location import LocationIn, LocationOut
from weatherapi_client.domain.schemas import APIResponseForecastWeather
from weatherapi_client.domain.weather.forecast import ForecastJSONIn, ForecastJSONOut
from weatherapi_client.domain.weather.weather_alerts import (
    WeatherAlertIn,
    WeatherAlertOut,
    WeatherAlertsIn,
    WeatherAlertsOut,
)
from weatherapi_client.settings import weatherapi_settings
from .__methods import save_forecast, save_location

from . import requests

import http_lib
import httpx


def get_weather_forecast(
    location: str = weatherapi_settings.location,
    days: int = 1,
    api_key: str = weatherapi_settings.api_key,
    include_aqi: bool = True,
    include_alerts: bool = True,
    headers: dict | None = None,
    use_cache: bool = False,
    retry: bool = True,
    max_retries: int = 3,
    retry_sleep: int = 5,
    retry_stagger: int = 3,
    save_to_db: bool = True,
):
    if days > 10:
        log.warning(
            f"WeatherAPI only allows 10-day forecasts. {days} is too many, setting to 10."
        )
        days: int = 10

    weather_forecast_request: httpx.Request = requests.return_weather_forecast_request(
        days=days,
        api_key=api_key,
        location=location,
        include_aqi=include_aqi,
        headers=headers,
    )

    log.info(f"Requesting weather forecast for location: {location}")

    with http_lib.get_http_controller(use_cache=use_cache) as http:
        try:
            res: httpx.Response = http.client.send(weather_forecast_request)
        except httpx.ReadTimeout as timeout:
            log.warning(
                f"({type(timeout)}) Operation timed out while requesting weather forecast."
            )

            if not retry:
                raise timeout
            else:
                log.info(f"Retrying {max_retries} time(s)")
                current_attempt = 0
                _sleep = retry_sleep

                while current_attempt < max_retries:
                    if current_attempt > 0:
                        _sleep += retry_stagger

                    log.info(f"[Retry {current_attempt}/{max_retries}]")

                    try:
                        res: httpx.Response = http.client.send(weather_forecast_request)
                        break
                    except httpx.ReadTimeout as timeout_2:
                        log.warning(
                            f"ReadTimeout on attempt [{current_attempt}/{max_retries}]"
                        )

                        current_attempt += 1

                        time.sleep(retry_sleep)

                        continue

    log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

    if res.status_code in http_lib.constants.SUCCESS_CODES:
        log.info("Success requesting weather forecast")
        decoded = http_lib.decode_response(response=res)
    elif res.status_code in http_lib.constants.ALL_ERROR_CODES:
        log.warning(f"Error: [{res.status_code}: {res.reason_phrase}]: {res.text}")

        return None
    else:
        log.error(
            f"Unhandled error code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
        )

        return None

    # log.debug(f"Decoded: {decoded}")

    location_schema: LocationIn = LocationIn.model_validate(decoded["location"])
    forecast_schema = ForecastJSONIn(forecast_json=decoded)

    api_response = APIResponseForecastWeather(
        forecast=forecast_schema, location=location_schema
    )

    if save_to_db:
        log.info("Saving forecast to database")

        try:
            db_forecast: ForecastJSONOut = save_forecast(forecast_schema)

            return db_forecast
        except Exception as exc:
            msg = f"({type(exc)}) Error saving forecast to database. Details: {exc}"
            log.error(msg)

            raise exc

    return api_response
