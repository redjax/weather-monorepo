from cyclopts import App

from scripts import current_weather_background_task
import weatherapi_client

weather_app = App(name="weather", help="Run weather API tasks.", group=["weather"])

VALID_GET_WEATHER_TYPES = ["current"]


@weather_app.command(
    name="get",
    help="Make a GET request to a weather API endpoint. Runs as a background task.",
    group=["weather"],
)
def get_weather(weather_type: str):
    if weather_type not in VALID_GET_WEATHER_TYPES:
        raise ValueError(
            f"Invalid GET weather type: {weather_type}. Must be one of: {VALID_GET_WEATHER_TYPES}"
        )

    match weather_type:
        case "current":
            print(f"Getting current weather (background task)")

            try:
                current_weather = current_weather_background_task.run(
                    location_name=weatherapi_client.settings.weatherapi_settings.location
                )
                print(f"Current weather: {current_weather}")
            except Exception as exc:
                msg = f"({type(exc)}) Error executing GET current weather background task. Details: {exc}"
                print(f"[ERROR] {msg}")

                exit(1)
