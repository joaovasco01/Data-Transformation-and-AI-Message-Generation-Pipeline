import os
from message.prompt_manager import get_scenario_prompt
import typer
from message.data import transform_features_py  # noqa
from message.data import transform_features_sql  # noqa
from message.data import fetch_session_data
from message.model import ChatModel, OpenAIKeys

app = typer.Typer()


@app.command()
def transform():

    # Uncomment the function you want to run
    # transform_features_sql()
    # transform_features_py()

    return


# Load prompt from files
def load_prompt(file_name: str) -> str:
    """Loads a prompt file from the prompts directory."""
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    file_path = os.path.join(prompts_dir, file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

@app.command()
def get_message(session_group: str) -> str:
    """
    Retrieves session details for a given session_group and generates an AI-crafted message.
    """

    # 1️⃣ Fetch session details
    session_context = fetch_session_data(session_group)
    if not session_context:
        print(f"⚠️ No session data found for session_group: {session_group}")
        return ""

    # 2️⃣ Load & format scenario description
    session_context["scenario_description"] = get_scenario_prompt(session_context)
    
    # 3️⃣ Load user prompt template & format with session data
    user_prompt_template = load_prompt("user_prompt.txt")

    user_prompt = user_prompt_template.format(**session_context)

    # 4️⃣ Generate AI message
    response = generate_message(user_prompt)

    return response


def generate_message(user_prompt: str) -> str:
    """Calls OpenAI GPT model to generate a session message."""
    chat_model = ChatModel()
    
    system_prompt = load_prompt("system_prompt.txt")

    response = chat_model.get_completion(
        temperature=0.7,
        model="gpt-4-turbo-preview",
        messages=[
            {OpenAIKeys.ROLE: "system", OpenAIKeys.CONTENT: system_prompt},
            {OpenAIKeys.ROLE: "user", OpenAIKeys.CONTENT: user_prompt},
        ],
    )

    return response