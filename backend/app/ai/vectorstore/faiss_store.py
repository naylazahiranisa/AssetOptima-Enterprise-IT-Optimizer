"""FAISS vector store (placeholder for local in-memory vector search)."""

import logging

from app.ai.base import Document, VectorStore

logger = logging.getLogger(__name__)


class FAISStore(VectorStore):
    """Placeholder for FAISS-based local vector store."""

    def __init__(self, embedding_dim: int = 384):
        self._dim = embedding_dim

    async def add(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        logger.debug("FAISStore.add not yet implemented (%d docs)", len(documents))

    async def search(self, query_embedding: list[float], top_k: int = 5,
                     metadata_filter: dict | None = None,
                     score_threshold: float | None = None) -> list[Document]:
        logger.debug("FAISStore.search not yet implemented")
        return []

    async def delete(self, ids: list[str]) -> None:
        logger.debug("FAISStore.delete not yet implemented")
