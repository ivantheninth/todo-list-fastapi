import json

from openai import AsyncOpenAI, OpenAIError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.chat import ChatResponse


SYSTEM_PROMPT = """
You are an AI assistant for a Todo application.

Always answer politely.

If the user asks for a plan, task list, study schedule,
shopping list, or anything that can be converted into TODO items,
suggest useful tasks.

Return ONLY valid JSON.
Do not use markdown.
Do not wrap JSON in code blocks.
Do not add any text outside JSON.

Response format:

{
    "answer": "...",
    "tasks": [
        {
            "title": "...",
            "note": "..."
        }
    ]
}

If no tasks are needed:

{
    "answer": "...",
    "tasks": []
}
"""


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    async def ask(
        self,
        message: str,
    ) -> ChatResponse:
        try:
            response = await self.client.responses.create(
                model=settings.OPENAI_MODEL,
                input=f"{SYSTEM_PROMPT}\n\nUser:\n{message}",
            )

            data = json.loads(
                response.output_text
            )

            return ChatResponse.model_validate(data)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "LLM returned invalid JSON"
            ) from exc

        except ValidationError as exc:
            raise RuntimeError(
                "LLM returned invalid response structure"
            ) from exc

        except OpenAIError as exc:
            raise RuntimeError(
                "LLM service is unavailable"
            ) from exc


llm_service = LLMService()