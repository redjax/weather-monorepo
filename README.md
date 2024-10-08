# weather-monorepo

A Python monorepo managed with [`pdm`](https://pdm-project.org).

## Description

The purpose of this repository is to help me practice building apps as monorepos. The app serves as a backend for checking the weather across multiple APIs.

The weather APIs I intend to use in this app are:

- [weatherapi](https://www.weatherapi.com)
- [open-meteo](https://open-meteo.com)
- [openweathermap](https://openweathermap.org)

This repository was built by following the [`pdm-example-monorepo` repository](https://github.com/pdm-project/pdm-example-monorepo).

## Demo Usage

Install [`pdm`](https://pdm-project.org/en/latest/#installation).

Once `pdm` is installed, run `pdm install` to "install" the monorepo. This compiles the packages in the [`./packages`](./packages/) directory, making them available to each other, and installs the dependencies for each package.

Edit the config file(s) in [`./config`](./config/). Do not directly edit any `settings.toml` files under `./config/`. Instead, copy them to a `.local.toml` version, i.e. `cp settings.toml settings.local.toml` and `cp .secrets.example.toml .secrets.toml`.

Add your WeatherAPI API key and location to [`./config/apis/weatherapi`](./config/apis/weatherapi/).

Now you can import the packages from `./packages`. Create a file, i.e. `demo.py`, and import the necessary code to get the current weather:

```python
## demo.py
import logging

log = logging.getLogger(__name__)

from core import setup
import weatherapi_client

from dynaconf import Dynaconf

## Load logging settings from config/settings.toml
LOG_SETTINGS = Dynaconf(
    environments=True,
    env="logging",
    envvar_prefix="LOG",
    settings_files=["settings.toml", ".secrets.toml"],
)

def demo_weatherapi():
    current_weather = weatherapi_client.client.get_current_weather()
    log.debug(f"Current weather: {current_weather}")


def main():
    demo_weatherapi()


if __name__ == "__main__":
    setup.setup_logging(
        level=LOG_SETTINGS.get("LOG_LEVEL", default="INFO"),
        silence_loggers=LOG_SETTINGS.get(
            "LOG_SILENCE_LOGGERS", default=["httpx", "hishel", "httpcore"]
        ),
    )

    main()
```

To run the demo, execute `pdm run python demo.py`, or activate the `.venv` created by `pdm` and simply run `python demo.py`.

## Monorepo Notes

Building a monorepo with `pdm` is different from building a library or application. Each package has its own `pyproject.toml` file and dependencies.

When adding a new package, create a directory for the project in `./packages`, i.e. `mkdir packages/new-pkg`. Add the new package to the [root `pyproject.toml`](./pyproject.toml) with `pdm add ./packages/new-pkg`.

This package is now managed by `pdm`, and is available for import. If your package name is `./packages/new-pkg/src/new_pkg`, you can add it to other packages in the `./packages` directory by navigating to the package's root (where that package's `pyproject.toml` resides), and run `pdm add ../pkg-core` (or some other package name that already exists in [`./packages`](./packages/)).

### Updating code in a package

Every time you make changes to a package's code, you must run `pdm lock && pdm install` (see this note in the [pdm monorepo example repository](https://github.com/pdm-project/pdm-example-monorepo?tab=readme-ov-file#note-about-pdm-install)).

This project also includes [`nox`](https://nox.thea.codes/en/stable/), a tool to simplify running tasks/CI jobs locally (`nox` is a similar tool to `tox`, if you are familiar with that).

The [`noxfile.py`](./noxfile.py) defines `nox` sessions. To see a list of available sessions, run `nox -l` at the project root.

Re-building the monorepo at code changes can be done with `nox` by running `nox -s install-repo`. This will run the `pdm lock` and `pdm install` commands.

You can also add a script to the [`pyproject.toml`](./pyproject.toml) file, and call that to rebuild the monorepo:

```toml
## pyproject.toml

...

[tool.pdm.scripts]

lock-install = { shell = "pdm lock && pdm install" }
```

Then you can call `pdm run lock-install` to rebuild the repository.
