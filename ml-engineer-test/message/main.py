import pandas as pd
import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.data import get_features
from pathlib import Path
from message.config import DATA_DIR
app = typer.Typer()


@app.command()
def transform():

    # Uncomment the function you want to run
    
    exercise_df = pd.read_parquet(Path(DATA_DIR, "exercise_results.parquet"))
    transform_features_sql(tables_to_register=[("exercise_results", exercise_df)])
    # transform_features_py()

    return


@app.command()
def get_message(session_group: str) -> str:

    features = get_features(session_group=session_group)  # noqa

    ###### YOUR CODE HERE ######

    ###########################

    return ""
