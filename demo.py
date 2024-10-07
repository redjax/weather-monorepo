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


def demo_weatherapi(save_to_db: bool = False):
    current_weather = weatherapi_client.client.get_current_weather(
        save_to_db=save_to_db
    )
    # log.debug(f"Current weather: {current_weather}")

    weather_forecast = weatherapi_client.client.get_weather_forecast(
        save_to_db=save_to_db
    )
    # log.debug(f"Weather forecast: {weather_forecast}")

    # if save_to_db:
    #     log.info("Saving current weather to database")

    #     try:
    #         weatherapi_client.client.save_current_weather(
    #             current_weather_schema=current_weather.weather,
    #             location_schema=current_weather.location,
    #         )

    #         log.info("[SUCCESS] Saved current weather to DB")
    #     except Exception as exc:
    #         msg = f"({type(exc)}) Error saving current weather to database. Details: {exc}"
    #         log.error(msg)

    #     log.info("Saving weather forecast to database")

    #     try:
    #         weatherapi_client.client.save_forecast(
    #             forecast_schema=weather_forecast.forecast
    #         )

    #         log.info("[SUCCEESS] Saved weather forecast to database")
    #     except Exception as exc:
    #         msg = f"({type(exc)}) Error saving weather forecast JSON to database. Details: {exc}"
    #         log.error(msg)

    #         raise exc


def main(save_to_db: bool = False):
    demo_weatherapi(save_to_db=save_to_db)


if __name__ == "__main__":
    setup.setup_logging(
        level=LOG_SETTINGS.get("LOG_LEVEL", default="INFO"),
        silence_loggers=LOG_SETTINGS.get(
            "LOG_SILENCE_LOGGERS", default=["httpx", "hishel", "httpcore"]
        ),
    )

    setup.setup_database()

    log.debug(f"Database settings: {DB_SETTINGS.as_dict()}")

    main(save_to_db=True)
