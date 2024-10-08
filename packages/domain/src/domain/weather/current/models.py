from __future__ import annotations

from decimal import Decimal
import logging
import typing as t

log = logging.getLogger(__name__)

from core.db import Base, annotated

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so


class CurrentWeatherModel(Base):
    __tablename__ = "weatherapi_current_weather"
    __table_args__ = (sa.UniqueConstraint("last_updated_epoch"),)
    # __table_args__ = (sa.UniqueConstraint("last_updated_epoch", name="_last_updated_epoch_uc"),)

    id: so.Mapped[annotated.INT_PK]

    last_updated_epoch: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    last_updated: so.Mapped[str] = so.mapped_column(sa.TEXT)
    temp_c: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    temp_f: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    is_day: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    wind_mph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    wind_kph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    wind_degree: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    wind_dir: so.Mapped[str] = so.mapped_column(sa.TEXT)
    pressure_mb: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    pressure_in: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    precip_mm: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    precip_in: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    humidity: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    cloud: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    feelslike_c: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    feelslike_f: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    windchill_c: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    windchill_f: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    heatindex_c: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    heatindex_f: so.Mapped[Decimal] = so.mapped_column(
        sa.NUMERIC(precision=12, scale=2)
    )
    dewpoint_c: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    dewpoint_f: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    vis_km: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    uv: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    gust_mph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    gust_kph: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))

    condition: so.Mapped["CurrentWeatherConditionModel"] = so.relationship(
        back_populates="weather"
    )
    air_quality: so.Mapped["CurrentWeatherAirQualityModel"] = so.relationship(
        back_populates="weather"
    )

    # ForeignKey to LocationModel
    location_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("weatherapi_location.id")
    )

    # Relationship back to LocationModel using a string reference
    location: so.Mapped["LocationModel"] = so.relationship(
        "LocationModel", back_populates="current_weather_entries"
    )


class CurrentWeatherConditionModel(Base):
    __tablename__ = "weatherapi_current_condition"

    id: so.Mapped[annotated.INT_PK]

    text: so.Mapped[str] = so.mapped_column(sa.TEXT)
    icon: so.Mapped[str] = so.mapped_column(sa.TEXT)
    code: so.Mapped[int] = so.mapped_column(sa.NUMERIC)

    weather_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("weatherapi_current_weather.id")
    )
    weather: so.Mapped["CurrentWeatherModel"] = so.relationship(
        back_populates="condition"
    )


class CurrentWeatherAirQualityModel(Base):
    __tablename__ = "weatherapi_air_quality"

    id: so.Mapped[annotated.INT_PK]

    co: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    no2: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    o3: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    so2: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    pm2_5: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    pm10: so.Mapped[Decimal] = so.mapped_column(sa.NUMERIC(precision=12, scale=2))
    us_epa_index: so.Mapped[int] = so.mapped_column(sa.NUMERIC)
    gb_defra_index: so.Mapped[int] = so.mapped_column(sa.NUMERIC)

    weather_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("weatherapi_current_weather.id")
    )
    weather: so.Mapped["CurrentWeatherModel"] = so.relationship(
        back_populates="air_quality"
    )
