import logging

log = logging.getLogger(__name__)

from pkg_core import setup
import weatherapi_client

from dynaconf import Dynaconf

LOG_SETTINGS = Dynaconf(
    environments=True,
    env="logging",
    envvar_prefix="LOG",
    settings_files=["settings.toml", ".secrets.toml"],
)


def demo_weatherapi():
    current_weather = weatherapi_client.client.get_current_weather()
    log.debug(f"Current weather: {current_weather}")

    weather_forecast = weatherapi_client.client.get_weather_forecast()
    log.debug(f"Weather forecast: {weather_forecast}")


def main():
    demo_weatherapi()


if __name__ == "__main__":
    setup.setup_logging(
        level=LOG_SETTINGS.get("LOG_LEVEL", default="INFO"),
        silence_loggers=LOG_SETTINGS.get(
            "LOG_SILENCE_LOGGERS", default=["httpx", "hishel", "httpcore"]
        ),
    )

    main()
