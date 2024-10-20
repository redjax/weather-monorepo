from __future__ import annotations

import logging

log = logging.getLogger(__name__)

from .settings import WEATHERAPI_SETTINGS

from core import setup
import http_lib

def get_current_weather(location: str, api_key: str):
    http_ctl = http_lib.get_http_controller()

    params = {"key": api_key, "q": location, "aqi": "yes"}

    req = http_lib.build_request(
        url="https://api.weatherapi.com/v1/current.json", params=params
    )

    with http_ctl as http:
        res = http.client.send(req)

    log.info(f"Current weather response: [{res.status_code}: {res.reason_phrase}]")

    log.debug(f"Response content: {res.text}")

    return res


if __name__ == "__main__":
    setup.setup_logging(level="DEBUG", silence_loggers=["httpx", "hishel", "httpcore"])

    API_KEY = WEATHERAPI_SETTINGS.get("WEATHERAPI_API_KEY", default="")
    LOCATION = WEATHERAPI_SETTINGS.get("WEATHERAPI_LOCATION_NAME", default="London")

    log.debug(f"API key: {API_KEY}")
    log.debug(f"Location: {LOCATION}")

    get_current_weather(api_key=API_KEY, location=LOCATION)
