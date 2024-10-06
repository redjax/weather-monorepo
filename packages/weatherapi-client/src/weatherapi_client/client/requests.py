from __future__ import annotations

import logging

log = logging.getLogger(__name__)

from weatherapi_client.constants import WEATHERAPI_BASE_URL

import http_lib
import httpx

def return_current_weather_request(
    api_key: str, location: str, include_aqi: bool = False, headers: dict | None = None
) -> httpx.Request:
    """Return an httpx.Request object for the current weather."""
    url: str = f"{WEATHERAPI_BASE_URL}/current.json"
    params: dict = {
        "key": api_key,
        "q": location,
        "aqi": f"{'yes' if include_aqi else 'no'}",
    }

    log.debug(f"Building WeatherAPI current weather request")
    req: httpx.Request = http_lib.build_request(url=url, params=params, headers=headers)

    return req


def return_weather_forecast_request(
    api_key: str,
    location: str,
    days: int = 1,
    include_aqi: bool = False,
    include_alerts: bool = False,
    headers: dict | None = None,
) -> httpx.Request:
    """Return an httpx.Request object for the weather forecast."""
    url: str = f"{WEATHERAPI_BASE_URL}/forecast.json"
    params: dict = {
        "key": api_key,
        "q": location,
        "aqi": f"{'yes' if include_aqi else 'no'}",
        "alerts": f"{'yes' if include_alerts else 'no'}",
        "days": days,
    }

    log.debug(f"Building WeatherAPI weather forecast request")
    req: httpx.Request = http_lib.build_request(url=url, params=params, headers=headers)

    return req
