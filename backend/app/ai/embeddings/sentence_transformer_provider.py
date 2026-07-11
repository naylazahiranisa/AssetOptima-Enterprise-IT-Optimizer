"""Sentence-Transformers embedding provider using local HuggingFace models.

Generates embeddings locally using all-MiniLM-L6-v2 (384 dims) for
offline RAG without any external API dependencies.
"""

import logging
from typing import Any

from app.ai.base import EmbeddingProvider

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer as _STModel
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False
    logger.warning("sentence-transformers not installed; using zero-vector fallback")


class SentenceTransformerProvider(EmbeddingProvider):
    """Local sentence-transformers embedding provider (all-MiniLM-L6-v2)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimensions: int = 384):
        self._model_name = model_name
        self._dimensions = dimensions
        self._model: Any = None

    def _load_model(self) -> None:
        if self._model is not None:
            return
        if not _ST_AVAILABLE:
            logger.warning("sentence-transformers unavailable; embedding will return zero vectors")
            return
        try:
            self._model = _STModel(self._model_name)
            logger.info("Loaded sentence-transformers model: %s", self._model_name)
        except Exception as exc:
            logger.error("Failed to load model %s: %s", self._model_name, exc)
            self._model = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        if self._model is None:
            return [[0.0] * self._dimensions for _ in texts]
        try:
            embeddings = self._model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
        except Exception as exc:
            logger.error("Embedding failed: %s", exc)
            return [[0.0] * self._dimensions for _ in texts]

    async def embed_query(self, text: str) -> list[float]:
        result = await self.embed([text])
        return result[0] if result else [0.0] * self._dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    @property
    def model_name(self) -> str:
        return self._model_name
