from __future__ import annotations

from . import location, weather
from .schemas import APIResponseCurrentWeather, APIResponseForecastWeather

from .location import LocationIn, LocationModel, LocationOut, LocationRepository

from .weather.current import (
    CurrentWeatherIn,
    CurrentWeatherOut,
    CurrentWeatherModel,
    CurrentWeatherRepository,
)
from .weather.current import (
    CurrentWeatherAirQualityIn,
    CurrentWeatherAirQualityModel,
    CurrentWeatherAirQualityOut,
    CurrentWeatherAirQualityRepository,
)

from .weather.current import (
    CurrentWeatherConditionIn,
    CurrentWeatherConditionModel,
    CurrentWeatherConditionOut,
    CurrentWeatherConditionRepository,
)

from .weather.forecast import (
    ForecastJSONIn,
    ForecastJSONOut,
    ForecastJSONModel,
    ForecastJSONRepository,
)
