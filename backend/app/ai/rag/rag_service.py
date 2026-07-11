"""RAG orchestration service that coordinates loading, chunking, embedding,
retrieval, and prompt building.

Now accepts an optional DB session for logging and document tracking.
"""

import logging
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import Document, EmbeddingProvider, VectorStore
from app.ai.prompts.chat_template import build_rag_prompt
from app.ai.rag.chunker import RecursiveCharacterChunker
from app.ai.rag.document_loader import DocumentLoader
from app.ai.rag.retriever import Retriever

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates the full RAG pipeline for question answering."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        db: AsyncSession | None = None,
    ):
        self.loader = DocumentLoader()
        self.chunker = RecursiveCharacterChunker()
        self.retriever = Retriever(embedder, vector_store)
        self.db = db
        self._documents_indexed = 0

    async def index_document(self, content: bytes, filename: str) -> int:
        """Load, chunk, embed, and store a document."""
        docs = await self.loader.load(content, filename)
        chunked = self.chunker.chunk(docs)

        texts = [d.content for d in chunked]
        embeddings = await self.retriever.embedder.embed(texts)

        await self.retriever.store.add(chunked, embeddings)
        self._documents_indexed += len(chunked)
        logger.info("Indexed %d chunks from '%s'", len(chunked), filename)
        return len(chunked)

    async def answer(
        self,
        question: str,
        top_k: int = 5,
        metadata_filter: dict | None = None,
    ) -> dict[str, Any]:
        """Retrieve relevant documents and build a RAG prompt."""
        start = time.time()
        retrieved = await self.retriever.retrieve(
            question, top_k=top_k, metadata_filter=metadata_filter
        )

        context = (
            "\n\n".join(d.content for d in retrieved)
            if retrieved
            else "No relevant documents found."
        )
        prompt = build_rag_prompt(question, context)

        elapsed = round(time.time() - start, 4)
        return {
            "prompt": prompt,
            "context": context,
            "source_documents": [
                {
                    "content": d.content[:300],
                    "metadata": d.metadata,
                    "score": d.score,
                }
                for d in retrieved
            ],
            "processing_time": elapsed,
        }

    @property
    def indexed_count(self) -> int:
        return self._documents_indexed
