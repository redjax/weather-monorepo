"""I foolishly deleted data without doing any modifications to existing IDs,
and now my database starts at index 7 instead of 1.

As an exercise, I use DuckDB to load my database into a local copy, modify the IDs by shifting them down
and updating foreign keys, then overwrite the data in the live database with the DuckDB copy.
"""

import logging

log = logging.getLogger(__name__)

from core import setup, db, db_depends

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc
import sqlalchemy.types as sa_type

import duckdb as duck
import pandas as pd


def read_table_to_df(engine: sa.Engine, query: str | None):
    table_df = pd.read_sql(query, engine)

    engine.dispose()

    return table_df


def main(engine: sa.Engine, tables: list[str]):
    tbl_dataframes: list[dict[str, pd.DataFrame]] = []

    for tbl in tables:
        log.info(f"Loading table '{tbl}' into dataframe")

        query = f"SELECT * FROM {tbl};"

        try:
            tbl_df = read_table_to_df(engine=engine, query=query)
            tbl_dataframes.append({"table": tbl, "df": tbl_df})
        except Exception as exc:
            msg = f"({type(exc)}) Error reading table '{tbl}' into dataframe. Details: {exc}"
            log.error(msg)

            raise exc

        # log.debug(f"Table '{tbl}' dataframe:\n{tbl_df.head(5)}")

    log.debug(f"Loaded [{len(tbl_dataframes)}] database table(s) into dataframes")

    current_weather_df_dict = next(
        (
            df_dict
            for df_dict in tbl_dataframes
            if df_dict["table"] == "weatherapi_current_weather"
        ),
        None,  # Default value if no match is found
    )

    if current_weather_df_dict is None:
        raise ValueError(f"Could not find weatherapi_current_weather dataframe.")

    current_weather_df = current_weather_df_dict["df"]
    log.debug(f"Current weather dataframe:\n{current_weather_df.head(5)}")


if __name__ == "__main__":
    setup.setup_logging(level=setup.LOGGING_SETTINGS.get("LOG_LEVEL", default=""))

    ENGINE = db_depends.get_db_engine()

    table_names: list[str] = [
        "weatherapi_air_quality",
        "weatherapi_current_condition",
        "weatherapi_current_weather",
        "weatherapi_forecast_json",
        "weatherapi_location",
    ]

    main(engine=ENGINE, tables=table_names)
