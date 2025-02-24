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


def fetch_session_data(session_group: str) -> dict:
    """Fetches and processes session data."""
    features = get_features(session_group=session_group)
    if not features:
        return {}

    session_info = features[0] if isinstance(features, list) else features
    # Ensure we always return a structured dictionary with defaults
    return {
        "patient_name": session_info.get("patient_name", "Unknown"),
        "therapy_name": session_info.get("therapy_name", "Unknown Therapy"),
        "session_number": session_info.get("session_number", None),
        "session_is_nok": session_info.get("session_is_nok", True),
        "pain": f"{session_info.get('pain', 0)}",
        "fatigue": f"{session_info.get('fatigue', 0)}",
        "quality": f"{session_info.get('quality', 5)}",
        "number_exercises": f"{session_info.get('number_exercises', 0)}",
        "exercise_with_most_incorrect": session_info.get("exercise_with_most_incorrect", "N/A"),
        "first_exercise_skipped": session_info.get("first_exercise_skipped", "N/A"),
        "leave_session": session_info.get("leave_session", "No early leave"),
        "number_of_distinct_exercises": session_info.get("number_of_distinct_exercises", "N/A"),
        "perc_correct_repeats": session_info.get("perc_correct_repeats", "N/A"),
    }

