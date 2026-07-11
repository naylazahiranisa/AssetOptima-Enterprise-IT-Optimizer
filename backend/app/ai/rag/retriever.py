"""Retriever that combines embeddings, vector store, and metadata filtering."""

import logging
from typing import Any

from app.ai.base import Document, EmbeddingProvider, VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """High-level retriever that embeds queries and searches the vector store."""

    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore):
        self.embedder = embedding_provider
        self.store = vector_store

    async def retrieve(self, query: str, top_k: int = 5,
                       metadata_filter: dict | None = None,
                       score_threshold: float | None = None) -> list[Document]:
        query_embedding = await self.embedder.embed_query(query)
        results = await self.store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
        )
        logger.debug("Retrieved %d documents for query (len=%d)", len(results), len(query))
        return results
