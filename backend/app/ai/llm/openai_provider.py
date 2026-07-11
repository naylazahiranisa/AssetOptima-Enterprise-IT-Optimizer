"""OpenAI LLM integration for the AI assistant."""

import logging
from typing import Any

from openai import AsyncOpenAI

from app.config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """Call OpenAI chat completion API to generate answers."""

    def __init__(self):
        self.client: AsyncOpenAI | None = None
        api_key = settings.OPENAI_API_KEY
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI provider initialized")
        else:
            logger.warning("OPENAI_API_KEY not set — LLM disabled")

    @property
    def available(self) -> bool:
        return self.client is not None

    async def generate(self, prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 1024) -> str:
        if not self.client:
            return ""

        try:
            resp = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are AssetOptima AI, an enterprise IT asset management assistant. Answer concisely and professionally based on the provided context."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI API call failed: %s", exc)
            return ""
