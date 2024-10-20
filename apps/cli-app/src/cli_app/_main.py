import logging

log = logging.getLogger(__name__)

# from .modules.demo import demo_app
from .modules.database import db_app
from .modules.celery import celery_cli_app
from .modules.weather import weather_app


from cyclopts import App

## Create main CLI app
app = App(help="CLI application for the weather-monorepo project.")

## Mount CLI sub-apps
# app.command(demo_app)
app.command(db_app)
app.command(celery_cli_app)
app.command(weather_app)


@app.command
def foo(loops: int):
    for i in range(loops):
        print(f"Looping! {i}")


@app.default
def default_action():
    print("Run --help to see options")


if __name__ == "__main__":
    app()
