import os
from message.prompt_manager import get_scenario_prompt, load_prompt
import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.data import fetch_session_data
from message.model import generate_message

app = typer.Typer()


@app.command()
def transform():

    # Uncomment the function you want to run
    # transform_features_sql()
    # transform_features_py()

    return


@app.command()
async def get_message(session_group: str) -> str:
    """
    Retrieves session details for a given session_group and generates an AI-crafted message.
    """

    # 1️⃣ Fetch session details
    session_context = fetch_session_data(session_group)
    if not session_context:
        print(f"No session data found for session_group: {session_group}")
        return ""

    # 2️⃣ Load & format scenario description
    session_context["scenario_description"] = get_scenario_prompt(session_context)
    
    # 3️⃣ Load user prompt template & format with session data
    user_prompt_template = load_prompt("user_prompt.txt")

    user_prompt = user_prompt_template.format(**session_context)

    # 4️⃣ Generate AI message
    response = await generate_message(user_prompt)

    return response