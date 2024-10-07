import logging

log = logging.getLogger(__name__)

from core import setup
from core.depends.db_depends import get_db_engine, get_db_uri, get_session_pool
from core.db.settings import DB_SETTINGS
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
    # demo_weatherapi()

    pass


if __name__ == "__main__":
    setup.setup_logging(
        level=LOG_SETTINGS.get("LOG_LEVEL", default="INFO"),
        silence_loggers=LOG_SETTINGS.get(
            "LOG_SILENCE_LOGGERS", default=["httpx", "hishel", "httpcore"]
        ),
    )

    setup.setup_database()

    log.debug(f"Database settings: {DB_SETTINGS.as_dict()}")

    main()
