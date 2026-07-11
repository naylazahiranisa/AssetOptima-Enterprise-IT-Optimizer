"""Document management service — upload, index, search, and delete documents.

Coordinates document storage (PostgreSQL), text extraction (DocumentLoader),
chunking (Chunker), embedding (SentenceTransformerProvider), and vector
storage (ChromaStore) into a single workflow.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import Document as AIDocument
from app.ai.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.ai.rag.chunker import RecursiveCharacterChunker
from app.ai.rag.document_loader import DocumentLoader
from app.ai.vectorstore.chroma_store import ChromaStore
from app.config.settings import settings
from app.models.document import Document as DocumentModel
from app.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)


class DocumentService:
    """Enterprise document management for RAG knowledge base."""

    def __init__(
        self,
        db: AsyncSession,
        embedder: SentenceTransformerProvider | None = None,
        vector_store: ChromaStore | None = None,
    ):
        self.db = db
        self.loader = DocumentLoader()
        self.chunker = RecursiveCharacterChunker(
            chunk_size=getattr(settings, "RAG_CHUNK_SIZE", 1000),
            chunk_overlap=getattr(settings, "RAG_CHUNK_OVERLAP", 200),
        )
        self.embedder = embedder or SentenceTransformerProvider()
        self.vector_store = vector_store or ChromaStore(
            embedding_dim=self.embedder.dimensions,
            persist_directory=getattr(settings, "CHROMA_PERSIST_DIR", "./chroma_data"),
        )

    async def upload_document(
        self,
        content: bytes,
        original_filename: str,
        uploaded_by: str,
        title: str | None = None,
        description: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Upload, extract, chunk, embed, and index a document."""
        start = time.time()

        checksum = DocumentLoader.compute_hash(content)
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "txt"
        file_size = len(content)

        # Dedup check
        existing = await self.db.execute(
            select(DocumentModel).where(
                DocumentModel.checksum == checksum,
                DocumentModel.is_deleted == False,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("A document with identical content already exists")

        # Create DB record
        doc_id = str(uuid.uuid4())
        doc = DocumentModel(
            id=doc_id,
            filename=f"{doc_id}.{ext}",
            original_filename=original_filename,
            file_type=ext,
            file_size=file_size,
            title=title or original_filename,
            description=description,
            category=category,
            status="pending",
            checksum=checksum,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(doc)
        await self.db.flush()

        try:
            # Extract text
            docs = await self.loader.load(content, original_filename)

            # Chunk
            chunked = self.chunker.chunk(docs)

            # Store chunks in DB and vector store
            chunk_ids = []
            db_chunks = []
            texts = []
            for i, chunk in enumerate(chunked):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                chunk.metadata["chunk_id"] = chunk_id
                chunk.metadata["document_id"] = doc_id
                chunk.metadata["category"] = category or "general"
                chunk.metadata["filename"] = original_filename
                texts.append(chunk.content)

                db_chunks.append(DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=doc_id,
                    content=chunk.content,
                    chunk_index=i,
                    chunk_size=len(chunk.content),
                    metadata_json=json.dumps(chunk.metadata),
                    embedding_id=chunk_id,
                ))

            # Batch insert chunks
            self.db.add_all(db_chunks)

            # Generate embeddings
            embeddings = await self.embedder.embed(texts)

            # Store in ChromaDB
            await self.vector_store.add(chunked, embeddings)

            # Update document status
            doc.status = "indexed"
            doc.chunk_count = len(chunked)
            await self.db.flush()

            elapsed = round(time.time() - start, 4)
            logger.info(
                "Document '%s' indexed: %d chunks in %.2fs",
                original_filename, len(chunked), elapsed,
            )

            return {
                "id": doc_id,
                "original_filename": original_filename,
                "file_type": ext,
                "file_size": file_size,
                "status": "indexed",
                "chunk_count": len(chunked),
                "processing_time": elapsed,
            }

        except Exception as exc:
            doc.status = "failed"
            await self.db.flush()
            logger.error("Document indexing failed for '%s': %s", original_filename, exc)
            raise

    async def list_documents(
        self,
        page: int = 1,
        per_page: int = 20,
        category: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        query = select(DocumentModel).where(DocumentModel.is_deleted == False)
        count_query = select(func.count(DocumentModel.id)).where(DocumentModel.is_deleted == False)

        if category:
            query = query.where(DocumentModel.category == category)
            count_query = count_query.where(DocumentModel.category == category)
        if status:
            query = query.where(DocumentModel.status == status)
            count_query = count_query.where(DocumentModel.status == status)

        query = query.order_by(DocumentModel.uploaded_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.db.execute(query)
        docs = result.scalars().all()

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        return {
            "items": [self._doc_to_dict(d) for d in docs],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_document(self, doc_id: str) -> dict | None:
        result = await self.db.execute(
            select(DocumentModel).where(
                DocumentModel.id == doc_id,
                DocumentModel.is_deleted == False,
            )
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            return None
        return {**self._doc_to_dict(doc), "chunks": await self._get_chunks(doc_id)}

    async def delete_document(self, doc_id: str) -> bool:
        result = await self.db.execute(
            select(DocumentModel).where(
                DocumentModel.id == doc_id,
                DocumentModel.is_deleted == False,
            )
        )
        doc = result.scalar_one_or_none()
        if doc is None:
            return False

        # Remove from ChromaDB
        try:
            await self.vector_store.delete_by_metadata("document_id", doc_id)
        except Exception as exc:
            logger.warning("Failed to delete from ChromaDB: %s", exc)

        # Soft delete
        doc.is_deleted = True
        await self.db.flush()

        # Delete chunks
        await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == doc_id)
        )
        await self.db.flush()
        return True

    async def search_documents(
        self,
        query: str,
        top_k: int = 5,
        category: str | None = None,
        score_threshold: float | None = None,
    ) -> dict[str, Any]:
        start = time.time()
        metadata_filter = None
        if category:
            metadata_filter = {"category": category}

        query_embedding = await self.embedder.embed_query(query)
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
        )

        search_results = []
        for r in results:
            search_results.append({
                "content": r.content[:500],
                "metadata": r.metadata,
                "score": r.score,
                "document_id": r.metadata.get("document_id", ""),
                "chunk_index": r.metadata.get("chunk_index", 0),
            })

        elapsed = round(time.time() - start, 4)
        logger.info("Semantic search '%s' returned %d results in %.2fs", query, len(search_results), elapsed)

        return {
            "results": search_results,
            "total": len(search_results),
            "query": query,
            "processing_time": elapsed,
        }

    async def get_chunks(self, document_id: str) -> list[dict]:
        return await self._get_chunks(document_id)

    async def get_stats(self) -> dict[str, Any]:
        total = await self.db.execute(
            select(func.count(DocumentModel.id)).where(DocumentModel.is_deleted == False)
        )
        indexed = await self.db.execute(
            select(func.count(DocumentModel.id)).where(
                DocumentModel.status == "indexed",
                DocumentModel.is_deleted == False,
            )
        )
        total_chunks = await self.db.execute(
            select(func.count(DocumentChunk.id))
        )
        chroma_count = 0
        try:
            chroma_count = await self.vector_store.count()
        except Exception:
            pass

        return {
            "total_documents": total.scalar() or 0,
            "indexed_documents": indexed.scalar() or 0,
            "total_chunks": total_chunks.scalar() or 0,
            "chroma_entries": chroma_count,
        }

    async def _get_chunks(self, document_id: str) -> list[dict]:
        result = await self.db.execute(
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.is_active == True,
            )
            .order_by(DocumentChunk.chunk_index)
        )
        chunks = result.scalars().all()
        return [
            {
                "id": c.id,
                "content": c.content[:300],
                "chunk_index": c.chunk_index,
                "chunk_size": c.chunk_size,
            }
            for c in chunks
        ]

    def _doc_to_dict(self, doc: DocumentModel) -> dict:
        return {
            "id": doc.id,
            "original_filename": doc.original_filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "title": doc.title,
            "description": doc.description,
            "category": doc.category,
            "status": doc.status,
            "chunk_count": doc.chunk_count,
            "uploaded_by": doc.uploaded_by,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
        }
