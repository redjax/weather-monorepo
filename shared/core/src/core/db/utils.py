from __future__ import annotations

import logging
from pathlib import Path
import sqlite3
import typing as t

log = logging.getLogger(__name__)


def backup_sqlite_db(source: str, target: str) -> None:
    try:
        connection: sqlite3.Connection = sqlite3.connect(database=source)
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception connecting to source '{source}'. Details: {exc}"
        log.error(msg)

        raise exc

    try:
        bck: sqlite3.Connection = sqlite3.connect(database=target)
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception connecting to target '{target}'. Details: {exc}"
        log.error(msg)

        connection.close()

        raise exc

    with bck:
        try:
            connection.backup(target=bck)
        except Exception as exc:
            msg = f"({type(exc)})"
            log.error(msg)

            bck.close()
            connection.close()

            raise exc

    bck.close()
    connection.close()


def dump_sqlite_db_schema(source: str, output_dir: str = "db_schema/sqlite"):
    if not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        connection: sqlite3.Connection = sqlite3.connect(database=source)
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception connecting to source '{source}'. Details: {exc}"
        log.error(msg)

        raise exc

    with open(f"{output_dir}/CREATE_schema.sql", "w+") as f:
        for line in connection.iterdump():
            if line.startswith("CREATE"):
                f.write(line + f"\n")
