"""OpenAI embedding provider (placeholder for future integration)."""

import logging

from app.ai.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Placeholder for OpenAI text-embedding-ada / text-embedding-3 models."""

    def __init__(self, model: str = "text-embedding-3-small", dimensions: int = 1536):
        self._model = model
        self._dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        logger.debug("OpenAIEmbeddingProvider.embed not yet implemented (model=%s)", self._model)
        return [[0.0] * self._dimensions for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        logger.debug("OpenAIEmbeddingProvider.embed_query not yet implemented")
        return [0.0] * self._dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions
