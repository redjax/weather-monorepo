from celery.schedules import crontab
from weatherapi_client.settings import WEATHERAPI_SETTINGS

## Check for current weather every 15 minutes
TASK_SCHEDULE_15m_current_weather_check: dict = {
    "15m_current_weather_check": {
        "task": "request_current_weather",
        "schedule": crontab(minute="*/15"),
        "args": [WEATHERAPI_SETTINGS.get("WEATHERAPI_LOCATION_NAME", default=None)],
    }
}

## Count current weather table rows every 10 minutes
TASK_SCHEDULE_10m_current_weather_row_count: dict = {
    "10m_current_weather_check": {
        "task": "current_weather_count",
        "schedule": crontab(minute="*/10"),
    }
}

## Check weather forecast every 6 hours
TASK_SCHEDULE_6h_weather_forecast_check: dict = {
    "6h_weather_forecast_check": {
        "task": "request_weather_forecast",
        "schedule": crontab(minute=0, hour="*/6"),
        "args": [WEATHERAPI_SETTINGS.get("WEATHERAPI_LOCATION_NAME", default=None)],
    }
}
