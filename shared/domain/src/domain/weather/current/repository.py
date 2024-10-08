from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from .models import (
    CurrentWeatherAirQualityModel,
    CurrentWeatherConditionModel,
    CurrentWeatherModel,
)

from core.db.base import BaseRepository
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

class CurrentWeatherRepository(BaseRepository[CurrentWeatherModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherModel)

    def create_with_related(
        self, weather_data: dict, condition_data: dict, air_quality_data: dict
    ) -> CurrentWeatherModel:
        weather = CurrentWeatherModel(**weather_data)
        condition = CurrentWeatherConditionModel(**condition_data)
        air_quality = CurrentWeatherAirQualityModel(**air_quality_data)

        # Associate the related models with the main weather model
        weather.condition = condition
        weather.air_quality = air_quality

        # Add and commit all models in one transaction
        self.session.add(weather)
        self.session.commit()
        self.session.refresh(weather)

        return weather

    def update_with_related(
        self,
        weather: CurrentWeatherModel,
        weather_data: dict,
        condition_data: dict = None,
        air_quality_data: dict = None,
    ) -> CurrentWeatherModel:
        # Update main weather model
        self.update(weather, weather_data)

        # Update condition if provided
        if condition_data and weather.condition:
            self.update(weather.condition, condition_data)

        # Update air quality if provided
        if air_quality_data and weather.air_quality:
            self.update(weather.air_quality, air_quality_data)

        return weather

    def get_by_id(self, id: int):
        return (
            self.session.query(CurrentWeatherModel)
            .filter(CurrentWeatherModel.id == id)
            .one_or_none()
        )

    def get_by_last_updated_epoch(self, last_updated_epoch: int):
        return (
            self.session.query(CurrentWeatherModel)
            .filter(CurrentWeatherModel.last_updated_epoch == last_updated_epoch)
            .one_or_none()
        )

    def get_by_last_updated(self, last_updated: str):
        return (
            self.session.query(CurrentWeatherModel)
            .filter(CurrentWeatherModel.last_updated == last_updated)
            .one_or_none()
        )

    def get_with_related(self, id: int):
        try:
            _weather: CurrentWeatherModel = (
                self.session.query(CurrentWeatherModel)
                .options(
                    so.joinedload(CurrentWeatherModel.condition),
                    so.joinedload(CurrentWeatherModel.air_quality),
                )
                .filter(CurrentWeatherModel.id == id)
                .one()
            )

            return _weather
        except Exception as exc:
            msg = f"({type(exc)}) Error retrieving related entities. Details: {exc}"
            log.error(msg)

            raise exc


class CurrentWeatherConditionRepository(BaseRepository[CurrentWeatherConditionModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherConditionModel)


class CurrentWeatherAirQualityRepository(BaseRepository[CurrentWeatherAirQualityModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, CurrentWeatherAirQualityModel)
