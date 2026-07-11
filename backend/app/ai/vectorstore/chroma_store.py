"""ChromaDB vector store implementation with persistent local storage.

Stores document embeddings in a local ChromaDB collection for semantic
retrieval with metadata filtering and score thresholding.
"""

import json
import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.ai.base import Document, VectorStore
from app.config.settings import settings

logger = logging.getLogger(__name__)


class ChromaStore(VectorStore):
    """Persistent ChromaDB vector store for RAG embeddings."""

    def __init__(
        self,
        collection_name: str = "assetoptima",
        persist_directory: str | None = None,
        embedding_dim: int = 384,
    ):
        self._collection_name = collection_name
        self._persist_directory = (
            persist_directory or getattr(settings, "CHROMA_PERSIST_DIR", "./chroma_data")
        )
        self._embedding_dim = embedding_dim
        self._client: chromadb.PersistentClient | None = None
        self._collection: chromadb.Collection | None = None

    async def _ensure_client(self) -> None:
        """Lazy-init ChromaDB client and collection."""
        if self._client is not None:
            return
        self._client = chromadb.PersistentClient(
            path=self._persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB connected: collection='%s' at '%s'",
            self._collection_name,
            self._persist_directory,
        )

    async def add(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        await self._ensure_client()
        ids = []
        metadatas = []
        texts = []
        for i, doc in enumerate(documents):
            chunk_id = doc.metadata.get("chunk_id", f"chunk_{i}")
            ids.append(chunk_id)
            texts.append(doc.content)
            meta = dict(doc.metadata)
            meta.pop("chunk_id", None)
            metadatas.append(meta)
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        logger.debug("Added %d documents to ChromaDB collection '%s'", len(documents), self._collection_name)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        metadata_filter: dict | None = None,
        score_threshold: float | None = None,
    ) -> list[Document]:
        await self._ensure_client()
        where = None
        if metadata_filter:
            where = {k: v for k, v in metadata_filter.items() if v is not None}

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        documents: list[Document] = []
        if not results["ids"] or not results["ids"][0]:
            return documents

        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i] if results.get("distances") else 0.0
            score = 1.0 - distance  # cosine distance -> similarity
            if score_threshold is not None and score < score_threshold:
                continue

            meta = dict(results["metadatas"][0][i]) if results.get("metadatas") else {}
            documents.append(
                Document(
                    content=str(results["documents"][0][i]),
                    metadata=meta,
                    score=round(score, 4),
                )
            )
        logger.debug("ChromaDB search returned %d results (top_k=%d)", len(documents), top_k)
        return documents

    async def delete(self, ids: list[str]) -> None:
        await self._ensure_client()
        self._collection.delete(ids=ids)
        logger.debug("Deleted %d documents from ChromaDB", len(ids))

    async def delete_by_metadata(self, metadata_key: str, metadata_value: str) -> None:
        """Delete all chunks matching a metadata key/value pair."""
        await self._ensure_client()
        results = self._collection.get(where={metadata_key: metadata_value})
        if results["ids"]:
            self._collection.delete(ids=results["ids"])
            logger.debug(
                "Deleted %d ChromaDB entries where %s=%s",
                len(results["ids"]),
                metadata_key,
                metadata_value,
            )

    async def count(self) -> int:
        await self._ensure_client()
        return self._collection.count()

    @property
    def collection_name(self) -> str:
        return self._collection_name
