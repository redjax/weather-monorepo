from __future__ import annotations

from . import location, weather
from .schemas import APIResponseCurrentWeather, APIResponseForecastWeather
from .weather.current import (
    CurrentWeatherAirQualityIn,
    CurrentWeatherAirQualityOut,
    CurrentWeatherConditionIn,
    CurrentWeatherConditionOut,
    CurrentWeatherIn,
    CurrentWeatherOut,
)
from .weather.forecast import ForecastJSONIn, ForecastJSONOut
