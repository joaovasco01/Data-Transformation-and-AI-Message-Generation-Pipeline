import os

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")

def load_prompt(file_name: str) -> str:
    """Loads a prompt file from the prompts directory."""
    file_path = os.path.join(PROMPT_DIR, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def get_scenario_prompt(session_context: dict) -> str:
    """Loads and formats the appropriate scenario template."""
    file_name = "scenario_nok.txt" if session_context["session_is_nok"] == True else "scenario_ok.txt"
    template = load_prompt(file_name)
    return template.format(**session_context)
