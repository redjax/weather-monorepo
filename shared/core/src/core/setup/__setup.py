from __future__ import annotations

import logging

log: logging.Logger = logging.getLogger(__name__)

from core import db
from core.depends import db_depends

from dynaconf import Dynaconf

LOGGING_SETTINGS = Dynaconf(
    environments=True,
    env="logging",
    envvar_prefix="LOG",
    settings_files=["settings.toml", ".secrets.toml"],
)


def setup_logging(
    level: str = "INFO",
    format: str = "%(asctime)s | [%(levelname)s] | (%(name)s): %(module)s.%(funcName)s:%(lineno)s |> %(message)s",
    datefmt: str = "%Y-%m-%d_%H-%M-%S",
    silence_loggers: list[str] = [],
):
    logging.basicConfig(level=level.upper(), format=format, datefmt=datefmt)

    if silence_loggers:
        for _logger in silence_loggers:
            logging.getLogger(_logger).setLevel("WARNING")


def setup_database():
    engine = db_depends.get_db_engine()
    db.create_base_metadata(base=db.Base, engine=engine)
