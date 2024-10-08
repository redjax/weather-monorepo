from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)

import http_lib
from core.depends.db_depends import get_session_pool
from . import requests
from domain.location import LocationIn, LocationModel, LocationOut, LocationRepository
from domain.schemas import APIResponseCurrentWeather  # , APIResponseWeatherForecast
from domain.weather.current import (
    CurrentWeatherAirQualityIn,
    CurrentWeatherAirQualityModel,
    CurrentWeatherAirQualityOut,
    CurrentWeatherAirQualityRepository,
    CurrentWeatherConditionIn,
    CurrentWeatherConditionModel,
    CurrentWeatherConditionOut,
    CurrentWeatherConditionRepository,
    CurrentWeatherIn,
    CurrentWeatherModel,
    CurrentWeatherOut,
    CurrentWeatherRepository,
)
from domain.weather.forecast import (
    ForecastJSONRepository,
    ForecastJSONIn,
    ForecastJSONModel,
    ForecastJSONOut,
)

from ..settings import weatherapi_settings

import httpx


def save_location(location: LocationIn) -> LocationOut:
    session_pool = get_session_pool()

    with session_pool() as session:
        repo = LocationRepository(session)

        existing_model: LocationModel | None = repo.get_by_country_and_state(
            state=location.name, country=location.country
        )

        if existing_model:
            log.info(
                f"Found location '{location.name}, {location.country}' in database. Returning existing database entity."
            )

            db_model = existing_model

        else:

            location_dict: dict = location.model_dump()
            location_model: LocationModel = LocationModel(**location_dict)

            try:
                db_model: LocationModel = repo.create(location_model)
            except Exception as exc:
                msg = f"({type(exc)}) Unhandled exception saving location to database. Details: {exc}"
                log.error(msg)

                raise exc

        if db_model is None:
            log.warning("Location database transaction returned None.")
            return None
        else:
            log.info("Converting database model to API schema")

            # Eager load related models
            location_model = repo.get_by_id(id=db_model.id)

            if location_model is None:
                log.error(f"Could not find location entity by ID [{db_model.id}].")
                return None

            try:
                location_schema: LocationOut = LocationOut.model_validate(
                    location_model.__dict__
                )

                return location_schema
            except Exception as exc:
                msg = f"({type(exc)}) Error converting location database model to API schema. Details: {exc}"
                log.error(msg)

                raise exc


# def save_current_weather(
#     current_weather_schema: APIResponseCurrentWeather,
# ) -> CurrentWeatherOut | None:
#     location_schema: LocationIn = current_weather_schema.location
#     current_weather: CurrentWeatherIn = current_weather_schema.weather
#     condition_schema: CurrentWeatherConditionIn = (
#         current_weather_schema.weather.condition
#     )
#     air_quality_schema: CurrentWeatherAirQualityIn = (
#         current_weather_schema.weather.air_quality
#     )

#     session_pool = get_session_pool()

#     with session_pool() as session:
#         repo = CurrentWeatherRepository(session=session)

#         try:
#             location_db_schema: LocationOut = save_location(location=location_schema)
#         except Exception as exc:
#             msg = f"({type(exc)}) Error saving location. Details: {exc}"
#             log.error(msg)

#             raise exc

#         existing_model: CurrentWeatherModel | None = repo.get_by_last_updated_epoch(
#             last_updated_epoch=current_weather.last_updated_epoch
#         )

#         if existing_model:
#             log.info(
#                 f"Last updated time has not changed between current weather requests. Returning existing database entity."
#             )

#             db_model = existing_model

#         else:

#             weather_dict: dict = current_weather.model_dump(
#                 exclude=["air_quality", "condition"]
#             )
#             weather_dict["location_id"] = location_db_schema.id
#             condition_dict: dict = condition_schema.model_dump()
#             air_quality_dict: dict = air_quality_schema.model_dump()

#             try:
#                 db_model: CurrentWeatherModel = repo.create_with_related(
#                     weather_data=weather_dict,
#                     condition_data=condition_dict,
#                     air_quality_data=air_quality_dict,
#                 )
#             except Exception as exc:
#                 msg = f"({type(exc)}) Error adding current weather to database. Details: {exc}"
#                 log.error(msg)

#                 raise exc

#         if db_model is None:
#             log.warning("Current weather database transaction returned None.")
#             return None
#         else:
#             log.info("Converting database model to API schema")

#             # Eager load related models
#             weather_model = repo.get_with_related(id=db_model.id)

#             if weather_model is None:
#                 log.error(f"Could not find weather entity by ID [{db_model.id}].")
#                 return None

#             try:
#                 current_weather_schema: CurrentWeatherOut = (
#                     CurrentWeatherOut.model_validate(
#                         {
#                             **weather_model.__dict__,
#                             "condition": weather_model.condition.__dict__,
#                             "air_quality": weather_model.air_quality.__dict__,
#                         }
#                     )
#                 )

#                 return current_weather_schema
#             except Exception as exc:
#                 msg = f"({type(exc)}) Error converting current weather database model to API schema. Details: {exc}"
#                 log.error(msg)

#                 raise exc


def save_current_weather(
    current_weather_schema: CurrentWeatherIn, location_schema: LocationIn
) -> CurrentWeatherOut | None:
    condition_schema: CurrentWeatherConditionIn = current_weather_schema.condition
    air_quality_schema: CurrentWeatherAirQualityIn = current_weather_schema.air_quality

    session_pool = get_session_pool()

    with session_pool() as session:
        repo = CurrentWeatherRepository(session=session)

        try:
            location_db_schema: LocationOut = save_location(location=location_schema)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving location. Details: {exc}"
            log.error(msg)

            raise exc

        existing_model: CurrentWeatherModel | None = repo.get_by_last_updated_epoch(
            last_updated_epoch=current_weather_schema.last_updated_epoch
        )

        if existing_model:
            log.info(
                f"Last updated time has not changed between current weather requests. Returning existing database entity."
            )

            db_model = existing_model

        else:

            weather_dict: dict = current_weather_schema.model_dump(
                exclude=["air_quality", "condition"]
            )
            weather_dict["location_id"] = location_db_schema.id
            condition_dict: dict = condition_schema.model_dump()
            air_quality_dict: dict = air_quality_schema.model_dump()

            try:
                db_model: CurrentWeatherModel = repo.create_with_related(
                    weather_data=weather_dict,
                    condition_data=condition_dict,
                    air_quality_data=air_quality_dict,
                )
            except Exception as exc:
                msg = f"({type(exc)}) Error adding current weather to database. Details: {exc}"
                log.error(msg)

                raise exc

        if db_model is None:
            log.warning("Current weather database transaction returned None.")
            return None
        else:
            log.info("Converting database model to API schema")

            # Eager load related models
            weather_model = repo.get_with_related(id=db_model.id)

            if weather_model is None:
                log.error(f"Could not find weather entity by ID [{db_model.id}].")
                return None

            try:
                current_weather_schema: CurrentWeatherOut = (
                    CurrentWeatherOut.model_validate(
                        {
                            **weather_model.__dict__,
                            "condition": weather_model.condition.__dict__,
                            "air_quality": weather_model.air_quality.__dict__,
                        }
                    )
                )

                return current_weather_schema
            except Exception as exc:
                msg = f"({type(exc)}) Error converting current weather database model to API schema. Details: {exc}"
                log.error(msg)

                raise exc


def save_forecast(
    forecast_schema: ForecastJSONIn,
) -> ForecastJSONOut:
    session_pool = get_session_pool()

    with session_pool() as session:
        repo = ForecastJSONRepository(session=session)

        forecast_model = ForecastJSONModel(**forecast_schema.model_dump())

        try:
            db_forecast = repo.create(forecast_model)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving weather forecast JSON. Details: {exc}"
            log.error(msg)

            raise exc

    try:
        forecast_out: ForecastJSONOut = ForecastJSONOut.model_validate(
            forecast_model.__dict__
        )

        return forecast_out
    except Exception as exc:
        msg = f"({type(exc)}) Error converting JSON from database to ForecastJSONOut schema. Details: {exc}"
        log.error(msg)

        raise exc
