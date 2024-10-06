from __future__ import annotations

from decimal import Decimal
import logging
import typing as t

log = logging.getLogger(__name__)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

class CurrentWeatherConditionIn(BaseModel):
    text: str
    icon: str
    code: int


class CurrentWeatherConditionOut(CurrentWeatherConditionIn):
    id: int


class CurrentWeatherAirQualityIn(BaseModel):
    co: Decimal
    no2: Decimal
    o3: Decimal
    so2: Decimal
    pm2_5: Decimal
    pm10: Decimal
    us_epa_index: int = Field(alias="us-epa-index", default=None)
    gb_defra_index: int = Field(alias="gb-defra-index", default=None)


class CurrentWeatherAirQualityOut(CurrentWeatherAirQualityIn):
    id: int


class CurrentWeatherIn(BaseModel):
    last_updated_epoch: int
    last_updated: str
    temp_c: Decimal
    temp_f: Decimal
    is_day: int
    condition: CurrentWeatherConditionIn
    wind_mph: Decimal
    wind_kph: Decimal
    wind_degree: int
    wind_dir: str
    pressure_mb: Decimal
    pressure_in: Decimal
    precip_mm: Decimal
    precip_in: Decimal
    humidity: int
    cloud: int
    feelslike_c: Decimal
    feelslike_f: Decimal
    windchill_c: Decimal
    windchill_f: Decimal
    heatindex_c: Decimal
    heatindex_f: Decimal
    dewpoint_c: Decimal
    dewpoint_f: Decimal
    vis_km: Decimal
    uv: Decimal
    gust_mph: Decimal
    gust_kph: Decimal
    air_quality: CurrentWeatherAirQualityIn | None = Field(default=None)


class CurrentWeatherOut(CurrentWeatherIn):
    id: int
