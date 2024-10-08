from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from .. import db
from ..db.settings import DB_SETTINGS

import sqlalchemy as sa
import sqlalchemy.orm as so


def get_db_uri(
    drivername: str = DB_SETTINGS.get("DB_drivername", default="sqlite+pysqlite"),
    username: str | None = DB_SETTINGS.get("DB_USERNAME", default=None),
    password: str | None = DB_SETTINGS.get("DB_PASSWORD", default=None),
    host: str | None = DB_SETTINGS.get("DB_HOST", default=None),
    port: int | None = DB_SETTINGS.get("DB_PORT", default=None),
    database: str = DB_SETTINGS.get("DB_DATABASE", default="demo.sqlite"),
    as_str: bool = False,
) -> sa.URL:
    db_uri: sa.URL = db.get_db_uri(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    if as_str:
        return str(db_uri)
    else:
        return db_uri


def get_db_engine(db_uri: sa.URL = get_db_uri(), echo: bool = False) -> sa.Engine:
    engine: sa.Engine = db.get_engine(url=db_uri, echo=echo)

    return engine


def get_session_pool(
    engine: sa.Engine = get_db_engine(),
) -> so.sessionmaker[so.Session]:
    session: so.sessionmaker[so.Session] = db.get_session_pool(engine=engine)

    return session
