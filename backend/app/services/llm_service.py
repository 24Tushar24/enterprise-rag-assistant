import logging
from groq import Groq, RateLimitError
from app.core.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def generate(self, prompt: str, request_id: str | None = None) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        except RateLimitError:
            logger.warning(
                f"[{request_id}] Groq rate limit exceeded"
            )
            raise
        
        if response.usage:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

            logger.info(
                f"[{request_id}] LLM usage: "
                f"model={self.model}, "
                f"input_tokens={input_tokens}, "
                f"output_tokens={output_tokens}, "
                f"total_tokens={total_tokens}"
            )

        return response.choices[0].message.content
