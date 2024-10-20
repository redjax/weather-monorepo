from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)

from weatherapi_client.settings import weatherapi_settings

from . import requests
from .__methods import save_current_weather, save_forecast, save_location

from domain.location import LocationIn, LocationOut
from domain.schemas import APIResponseCurrentWeather
from domain.weather.current import (
    CurrentWeatherAirQualityIn,
    CurrentWeatherAirQualityOut,
    CurrentWeatherConditionIn,
    CurrentWeatherConditionOut,
    CurrentWeatherIn,
    CurrentWeatherOut,
)
import http_lib
import httpx

def get_current_weather(
    location: str = weatherapi_settings.location,
    api_key: str = weatherapi_settings.api_key,
    include_aqi: bool = True,
    headers: dict | None = None,
    use_cache: bool = False,
    retry: bool = True,
    max_retries: int = 3,
    retry_sleep: int = 5,
    retry_stagger: int = 3,
    save_to_db: bool = True,
) -> APIResponseCurrentWeather | None:
    current_weather_request: httpx.Request = requests.return_current_weather_request(
        api_key=api_key, location=location, include_aqi=include_aqi, headers=headers
    )

    log.info(f"Requesting current weather for location: {location}")

    with http_lib.get_http_controller(use_cache=use_cache) as http:
        try:
            res: httpx.Response = http.client.send(current_weather_request)
        except httpx.ReadTimeout as timeout:
            log.warning(
                f"({type(timeout)}) Operation timed out while requesting current weather."
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
                        res: httpx.Response = http.client.send(current_weather_request)
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
        log.info("Success requesting current weather")
        decoded = http_lib.decode_response(response=res)
    elif res.status_code in http_lib.constants.ALL_ERROR_CODES:
        log.warning(f"Error: [{res.status_code}: {res.reason_phrase}]: {res.text}")

        return None
    else:
        log.error(
            f"Unhandled error code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
        )

        return None

    location: LocationIn = LocationIn.model_validate(decoded["location"])
    # log.debug(f"Location: {location}")
    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
        decoded["current"]
    )
    # log.debug(f"Weather: {current_weather}")

    api_response: APIResponseCurrentWeather = APIResponseCurrentWeather(
        location=location, weather=current_weather
    )
    # log.debug(f"API response: {api_response}")

    if save_to_db:
        log.info("Saving current weather to database")
        try:
            current_weather_out: CurrentWeatherOut | None = save_current_weather(
                current_weather_schema=api_response.weather,
                location_schema=api_response.location,
            )
        except Exception as exc:
            msg = f"({type(exc)}) Error saving current weather response. Details: {exc}"
            log.error(msg)

    log.info(
        f"Success requesting current weather for location '{location}' from WeatherAPI"
    )

    return api_response
