from message.prompt_manager import load_prompt
import openai
import asyncio
import random
import logging
from openai.error import RateLimitError, APIError, Timeout, InvalidRequestError
from message.config import get_settings
import tiktoken
# OpenAI pricing (adjust if model changes)
MAX_RETRIES = 3
PRICING = {
        "gpt-4-turbo-preview": {"input": 0.01 / 1000, "output": 0.03 / 1000},  # $0.01 per 1k input tokens, $0.03 per 1k output tokens
    }
class OpenAIKeys(str):
    ROLE = "role"
    CONTENT = "content"
    ANSWER = "answer"


class ChatModel:

    def __init__(self):
        settings = get_settings()
        openai.api_key = settings.OPENAI_API_KEY
        
    async def get_completion(
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
        
        for attempt in range(MAX_RETRIES):
            try:
                chat_completion = await openai.ChatCompletion.acreate(**kwargs)
                return chat_completion.choices[0].message[OpenAIKeys.CONTENT]

            except RateLimitError:
                if attempt < MAX_RETRIES - 1:  # If it's not the last attempt
                    wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff
                    self.logger.warning(f"Rate limit hit! Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)  # Async sleep to wait before retrying
                else:
                    self.logger.error("Max retries exceeded for rate limits.")
                    raise  # If max retries exceeded, raise the error
            except (APIError, Timeout) as e:
                self.logger.error(f"OpenAI API error: {e}")
                raise  # Re-raise critical API errors
    @staticmethod
    def count_tokens(text: str, model="gpt-4-turbo-preview") -> int:
            """Counts tokens in a given text."""
            enc = tiktoken.encoding_for_model(model)
            return len(enc.encode(text))

    @staticmethod
    def estimate_cost(input_tokens: int, output_tokens: int, model="gpt-4-turbo-preview") -> float:
            """Estimates the cost of an OpenAI API call."""
            input_cost = input_tokens * PRICING[model]["input"]
            output_cost = output_tokens * PRICING[model]["output"]
            return input_cost + output_cost


async def generate_message(user_prompt: str) -> str:
    """Calls OpenAI GPT model to generate a session message."""
    chat_model = ChatModel()
    
    system_prompt = load_prompt("system_prompt.txt")

    response = await chat_model.get_completion(
        temperature=0.7,
        model="gpt-4-turbo-preview",
        messages=[
            {OpenAIKeys.ROLE: "system", OpenAIKeys.CONTENT: system_prompt},
            {OpenAIKeys.ROLE: "user", OpenAIKeys.CONTENT: user_prompt},
        ],
    )
    group_tokens(response,system_prompt,user_prompt,chat_model)
    return response


def group_tokens(response: str,system_prompt: str,user_prompt: str, chat_model: ChatModel):
    output_tokens = chat_model.count_tokens(response)
    input_tokens = chat_model.count_tokens(system_prompt) + chat_model.count_tokens(user_prompt)

    # 8️⃣ Estimate cost
    estimated_price = chat_model.estimate_cost(input_tokens, output_tokens)
    
    logging.info(f"Input Tokens: {input_tokens}, Output Tokens: {output_tokens}")
    logging.info(f"Estimated Cost: ${estimated_price:.6f}")
    
    return