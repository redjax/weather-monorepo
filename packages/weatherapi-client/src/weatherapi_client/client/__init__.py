from __future__ import annotations

from . import current, forecast
from .current import get_current_weather
from .forecast import get_weather_forecast

from .__methods import save_current_weather, save_forecast, save_location
