"""Initialize the weather database."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

from core import setup
from core.db import Base, create_base_metadata
from core.depends.db_depends import (
    get_db_engine,
    get_db_uri,
    get_session_pool,
)
from weatherapi_client.domain.weather.current import models

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so


def init_pg_database(create_dbs: list[str], engine: sa.Engine = None):
    log.info("START init postgres database")

    errored = []
    already_existed = []
    created = []

    ## Create temporary engine that connects to initial 'postgres' database.
    #  This avoids an error about a non existent DB on first initialization.
    tmp_db_uri = get_db_uri(database="postgres")
    tmp_engine = get_db_engine(db_uri=tmp_db_uri, echo=True)

    try:
        log.info(
            f"Connecting to database: {tmp_engine.engine.url.database} on host: {'localhost' if tmp_engine.engine.url.host is None else tmp_engine.engine.url.host}"
        )
        with tmp_engine.connect() as conn:
            try:
                ## Connection starts in a transaction, write a commit to end the transaction
                conn.execute(sa.text("commit"))
            except Exception as exc:
                msg = f"({type(exc)}) Error closing initial transaction. Details: {exc}"
                log.error(msg)

                return False

            log.info(f"Creating [{len(create_dbs)}] database(s)")
            for db in create_dbs:
                log.info(f"Creating database: {db}")

                query: str = f"CREATE DATABASE {db}"

                try:
                    conn.execute(sa.text(query))

                    created.append(db)
                except sa_exc.ProgrammingError as db_exists_exc:
                    if "already exists" in f"{db_exists_exc}":
                        log.warning(f"SKIP CREATE DB: '{db}', REASON: already exists.")
                        already_existed.append(db)

                        continue
                    else:
                        msg = f"({type(db_exists_exc)}) Error creating database: {db_exists_exc}"
                        log.error(msg)
                        errored.append(db)

                        continue
                except Exception as exc:
                    msg = f"({type(exc)}) Error creating database: {db}. Details: {exc}"
                    log.error(msg)
                    errored.append(db)

                    continue

                log.debug(f"Success creating database '{db}'.")

    except sa_exc.OperationalError as sql_exc:
        msg = f"({type(sql_exc)}) Error opening SQL connection. Details: {sql_exc}"
        log.error(msg)

        return False

    log.info(f"Successfully created [{len(created)}] database(s)")
    log.info(
        f"Of the [{len(create_dbs)}] database(s) to create, [{len(already_existed)}] already existed."
    )

    log.info(f"Errored on [{len(errored)}] CREATE database statement(s)")
    if errored:
        for db_err in errored:
            print(f"[ERROR] Failed creating DB: {db_err}")

    log.info("Creating SQLAlchemy Base metadata.")
    try:
        create_base_metadata(base=Base, engine=engine)
        log.info("Metadata created successfully")
    except Exception as exc:
        msg = f"({type(exc)}) Error creating SQLAlchemy Base metadata. Details: {exc}"
        log.error(msg)

        return False

    log.info("END init postgres database")
    return True


def init_sqlite_database(engine: sa.Engine = None):
    log.info("START init sqlite database")

    try:
        create_base_metadata(base=Base, engine=engine)
        log.info("Metadata created successfully")
    except Exception as exc:
        msg = f"({type(exc)}) Error creating SQLAlchemy Base metadata. Details: {exc}"
        log.error(msg)

        return False

    log.info("END init sqlite database")

    return True


def main(create_dbs: list[str], db_uri: sa.URL, db_echo: bool = False):
    log.info("Getting SQLAlchemy engine")

    try:
        engine: sa.Engine = get_db_engine(db_uri=db_uri, echo=db_echo)
    except Exception as exc:
        msg = f"({type(exc)}) Error getting database engine. Details: {exc}"
        log.error(msg)

        return False

    match engine.dialect.name:
        case "postgresql":
            log.info("[DETECT DB]: Detected postgresql database")

            ## Set engine's database to default 'postgres' database to allow connecting
            init_pg_database(create_dbs=create_dbs, engine=engine)

        case "mysql":
            log.info("[DETECT DB]: Detected mysql/mariadb database")

            raise NotImplementedError("MySQL/MariaDB database is not supported")
        case "sqlite":
            log.info("[DETECT DB]: Detected sqlite database")

            engine.echo = True
            init_sqlite_database(engine=engine)
        case _:
            raise NotImplementedError(
                f"{engine.dialect.name.title()} database is not supported"
            )


if __name__ == "__main__":
    setup.setup_logging()

    # DB_URI: sa.URL = get_db_uri(database="postgres")
    DB_URI: sa.URL = get_db_uri()
    DB_ECHO: bool = False
    CREATE_DATABASES: list[str] = ["weathersched", "weathersched_dev"]

    main(db_uri=DB_URI, db_echo=DB_ECHO, create_dbs=CREATE_DATABASES)
