from cyclopts import App

from scripts import (
    save_db_tables_to_parquet,
    count_current_weather_rows,
    count_weather_forecast_rows,
)
import weatherapi_client

db_app = App(
    name="database",
    help="Database functions like getting a count of all current weather items, or running database maintenance tasks.",
    group="database",
)

db_backup_app = App(
    name="backup", help="Database backup operations", group="maintenance"
)
db_count_app = App(
    name="count", help="Count entities in database tables", group="count"
)

db_app.command(db_backup_app)
db_app.command(db_count_app)


@db_backup_app.command(name="tables-to-parquet", group="backup")
def backup_db_tables_to_parquet():
    """Backup tables in the database to .parquet files."""
    print("Backing up database tables to .parquet files")

    try:
        save_db_tables_to_parquet.run(save_tables=save_db_tables_to_parquet.SAVE_TABLES)
    except Exception as exc:
        msg = f"({type(exc)}) Error backing up database tables to .parquet files. Details: {exc}"
        print(f"[ERROR] {msg}")

        exit(1)


@db_count_app.command(name="current", group="count")
def count_current_weather():
    """Count number of rows in the current weather database table."""
    print("Getting count of current weather entities from database...")

    try:
        current_weather_count = count_current_weather_rows.run(
            location_name=weatherapi_client.settings.weatherapi_settings.location,
            task_check_sleep=2,
        )

        print(
            f"Found {current_weather_count['count']} current weather entry/ies in database"
        )
    except Exception as exc:
        msg = f"({type(exc)}) Error counting current weather entities in database. Details: {exc}"
        print(f"[ERROR] {msg}")

        exit(1)


@db_count_app.command(name="forecast", group="count")
def count_weather_forecast():
    """Count number of rows in the weather forecast database table."""
    print("Getting number of rows in the weather forecast database table")

    try:
        weather_forecast_count = count_weather_forecast_rows.run(
            location_name=weatherapi_client.settings.weatherapi_settings.location,
            task_check_sleep=2,
        )

        print(
            f"Found {weather_forecast_count['count']} weather forecast entry/ies in database"
        )

    except Exception as exc:
        msg = f"({type(exc)}) Error counting weather forecast entities in database. Details: {exc}"
        print(f"[ERROR] {msg}")

        exit(1)
