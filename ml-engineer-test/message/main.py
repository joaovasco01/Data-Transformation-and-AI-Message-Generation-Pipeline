import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.data import get_features

app = typer.Typer()


@app.command()
def transform():

    # Uncomment the function you want to run
    # transform_features_sql()
    # transform_features_py()

    return


@app.command()
def get_message(session_group: str) -> str:

    features = get_features(session_group=session_group)  # noqa

    ###### YOUR CODE HERE ######

    ###########################

    return ""
