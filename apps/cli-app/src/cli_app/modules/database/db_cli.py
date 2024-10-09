from cyclopts import App

from scripts import save_db_tables_to_parquet

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
    pass


@db_count_app.command(name="forecast", group="count")
def count_weather_forecast():
    """Count number of rows in the weather forecast database table."""
    pass
