from __future__ import annotations

from decimal import Decimal
import logging
import typing as t

log = logging.getLogger(__name__)

from .location import LocationIn, LocationOut
from .weather.current import CurrentWeatherIn, CurrentWeatherOut
from .weather.forecast import ForecastJSONIn, ForecastJSONOut
from .weather.weather_alerts import (
    WeatherAlertsIn,
    WeatherAlertsOut,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

class APIResponseWeatherBase(BaseModel):
    location: t.Union[LocationIn, LocationOut]


class APIResponseCurrentWeather(APIResponseWeatherBase):
    weather: t.Union[CurrentWeatherIn, CurrentWeatherOut]


class APIResponseForecastWeather(APIResponseWeatherBase):
    forecast: t.Union[ForecastJSONIn, ForecastJSONOut]
