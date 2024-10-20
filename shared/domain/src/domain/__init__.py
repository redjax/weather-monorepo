from __future__ import annotations

from . import location, weather
from .location import LocationIn, LocationModel, LocationOut, LocationRepository
from .schemas import APIResponseCurrentWeather, APIResponseForecastWeather
from .weather.current import (
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
from .weather.forecast import (
    ForecastJSONIn,
    ForecastJSONModel,
    ForecastJSONOut,
    ForecastJSONRepository,
)
