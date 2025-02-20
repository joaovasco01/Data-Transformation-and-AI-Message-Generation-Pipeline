from pathlib import Path

import duckdb
import pandas as pd
from message.config import DATA_DIR, QUERIES_DIR


def open_query(query_filename: Path, **kwargs) -> str:
    """Opens a query file and formats it with the provided kwargs.

    Parameters
    ----------
    query_filename : Path
        Name of the query file to open.

    Returns
    -------
    str
        The query file content formatted with the provided kwargs.
    """
    return open(query_filename, "r").read().format(**kwargs)


def transform_features_sql(tables_to_register=None):
    """-Loads the exercise results and transforms
    them into features using the features.sql query.
        -Allows optional table registration for DuckDB.
    """

    query = open_query(Path(QUERIES_DIR, "features.sql"))

    # ✅ Register tables if provided
    if tables_to_register:
        for table_name, df in tables_to_register:
            duckdb.register(table_name, df)

    session = duckdb.sql(query).df()

    session.to_parquet(Path(DATA_DIR, "features.parquet"))


def transform_features_py():
    ###### YOUR CODE HERE ######

    ###########################

    return


def get_features(session_group: str) -> dict:
    """Gets the features for a given session group.

    Parameters
    ----------
    session_group : str
        Session group to filter the features.

    Returns
    -------
    dict
        The features for the given session group in a dict format.
    """
    session = pd.read_parquet(Path(DATA_DIR, "features_expected.parquet"))

    return session[session["session_group"] == session_group].to_dict(
        orient="records"
    )
