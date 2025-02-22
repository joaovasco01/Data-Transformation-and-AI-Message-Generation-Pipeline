from message.prompt_manager import load_prompt
import openai
from message.config import get_settings


class OpenAIKeys(str):
    ROLE = "role"
    CONTENT = "content"
    ANSWER = "answer"


class ChatModel:
    def __init__(self):
        settings = get_settings()
        openai.api_key = settings.OPENAI_API_KEY

    def get_completion(
        self,
        **kwargs,
    ) -> str:
        """Creates a new chat completion for the provided messages and parameters.

        See https://platform.openai.com/docs/api-reference/chat/create
        for a list of valid parameters.

        Returns
        -------
        str
            The chat completion response.
        """

        chat_completion = openai.ChatCompletion.create(**kwargs)

        return chat_completion.choices[0].message[OpenAIKeys.CONTENT]

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