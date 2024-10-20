from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from core.setup import setup_database, setup_logging
from core.setup import LOGGING_SETTINGS
import datalab
import pandas as pd

SAVE_TABLES: list[dict, t.Union[str, None]] = [
    {
        "table_name": "weatherapi_current_weather",
        "parquet_output": ".data/backup/db/weatherapi_current_weather.parquet",
        "unique_col": None,
    },
    {
        "table_name": "weatherapi_location",
        "parquet_output": ".data/backup/db/weatherapi_location.parquet",
        "unique_col": "id",
    },
    {
        "table_name": "weatherapi_current_condition",
        "parquet_output": ".data/backup/db/weatherapi_current_condition.parquet",
        "unique_col": "id",
    },
    {
        "table_name": "weatherapi_air_quality",
        "parquet_output": ".data/backup/db/weatherapi_air_quality.parquet",
        "unique_col": "id",
    },
    {
        "table_name": "weatherapi_forecast_json",
        "parquet_output": ".data/backup/db/weatherapi_forecasts.parquet",
        "unique_col": "id",
    },
]


def run(
    save_tables: list[dict[str, t.Union[str, None]]],
    log_level: str = "INFO",
):
    log.info("Saving database tables to parquet files")

    success: list[dict[str, t.Union[str, pd.DataFrame]]] = []
    errors: list[dict] = []

    for tbl_dict in save_tables:
        log.info(
            f"Saving table '{tbl_dict['table_name']}' to file: {tbl_dict['parquet_output']}"
        )

        try:
            _df: pd.DataFrame = datalab.save_db_data_to_parquet(
                table_name=tbl_dict["table_name"],
                parquet_output=tbl_dict["parquet_output"],
                unique_col=tbl_dict["unique_col"],
            )

            success_dict = {"tbl_dict": tbl_dict, "dataframe": _df}

            success.append(success_dict)
        except Exception as exc:
            msg = f"({type(exc)}) Error saving table '{tbl_dict['table_name']}'. Details: {exc}"
            log.error(msg)

            err = {"error": exc, "tbl_dict": tbl_dict}
            errors.append(err)

            continue

    log.info(f"Saved [{len(success)}] table(s) to .parquet file(s)")

    if errors:
        log.warning(
            f"Errored while saving [{len(errors)}] table(s). Printing first 5 errors"
        )

        for e in errors[:5]:
            log.error(
                f"[ERROR] Could not save table '{e['tbl_dict']['table_name']}'. Error: {e['error']}"
            )

    log.info(f"Printing [{len(success)}] dataframe(s)")

    print("")

    for s in success:
        print(f">> {s['tbl_dict']['table_name']} Dataframe:")
        print(s["dataframe"].head(5))

        print("")

    return


if __name__ == "__main__":
    setup_logging()
    setup_database()

    try:
        run(
            save_tables=SAVE_TABLES,
            log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"),
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error saving database tables to .parquet files. Details: {exc}"
        log.error(msg)
        exit(1)

    log.info("Saved database tables to .parquet file(s)")
