from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)

from .settings import PANDAS_ENGINE

from core.depends.db_depends import get_db_engine
import pandas as pd
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

def load_db_data(engine, query: str) -> pd.DataFrame:
    """Load data from a PostgreSQL database into a DataFrame."""
    return pd.read_sql_query(query, con=engine)


def load_parquet_file(parquet_file: str) -> pd.DataFrame:
    """Load data from a Parquet file into a DataFrame, or return an empty DataFrame if it doesn't exist."""
    if Path(parquet_file).exists():
        return pd.read_parquet(parquet_file)
    return pd.DataFrame()  # Return an empty DataFrame if no file exists


def merge_dataframes(
    db_data: pd.DataFrame, parquet_data: pd.DataFrame, unique_column: str
) -> pd.DataFrame:
    """Concatenate two DataFrames and remove duplicates based on a unique column."""
    combined_df = pd.concat([parquet_data, db_data])
    return combined_df.drop_duplicates(subset=[unique_column])


def save_to_parquet(df: pd.DataFrame, parquet_file: str):
    """Save the DataFrame to a Parquet file, overwriting any existing file."""
    df.to_parquet(parquet_file, engine="pyarrow", compression="snappy", index=False)


def save_db_data_to_parquet(
    table_name: str,
    parquet_output: str,
    unique_col: str = "id",
    engine: sa.Engine = get_db_engine(),
) -> pd.DataFrame:
    if not Path(parquet_output).parent.exists():
        try:
            Path(parquet_output).parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = f"({type(exc)}) Error creating path '{Path(parquet_output).parent}'. Details: {exc}"
            log.error(msg)

    query: str = f"SELECT * FROM {table_name}"

    db_data: pd.DataFrame = load_db_data(engine=engine, query=query)
    pq_data: pd.DataFrame = load_parquet_file(parquet_file=parquet_output)
    combined_data: pd.DataFrame = merge_dataframes(
        db_data=db_data, parquet_data=pq_data, unique_column=unique_col
    )

    save_to_parquet(df=combined_data, parquet_file=parquet_output)

    return combined_data
