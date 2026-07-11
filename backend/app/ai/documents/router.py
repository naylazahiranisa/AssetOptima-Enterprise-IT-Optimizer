"""Document management router — CRUD + search for the RAG knowledge base.

Endpoints:
  POST   /ai/documents/upload      — Upload and index a document
  GET    /ai/documents             — List all documents (paginated)
  GET    /ai/documents/{id}        — Get document details + chunks
  DELETE /ai/documents/{id}        — Delete document + remove from vector store
  POST   /ai/documents/search      — Semantic search across documents
  GET    /ai/documents/{id}/chunks — Get document chunks
  GET    /ai/documents/stats       — Knowledge base statistics
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.documents.document_service import DocumentService
from app.ai.utils.response_formatter import error_response, format_response, start_timer
from app.ai.utils.sanitizer import validate_uploaded_file
from app.database.session import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentListResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentUploadResponse,
)
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/documents", tags=["ai-documents"])


def _get_doc_service(db: AsyncSession) -> DocumentService:
    return DocumentService(db=db)


@router.post("/upload", summary="Upload and index a document (Admin only)")
async def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    description: str | None = Form(None),
    category: str | None = Form(None),
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))] = ...,
):
    start_timer()
    content = await file.read()
    valid, error_msg = validate_uploaded_file(file.filename or "document", content)
    if not valid:
        return error_response(message=error_msg)

    try:
        service = _get_doc_service(db)
        result = await service.upload_document(
            content=content,
            original_filename=file.filename or "document",
            uploaded_by=str(current_user.id),
            title=title,
            description=description,
            category=category,
        )
        return format_response(
            data=result,
            message="Document uploaded and indexed successfully",
            processing_time=result.get("processing_time", 0.0),
        )
    except ValueError as exc:
        return error_response(message=str(exc))
    except Exception as exc:
        logger.error("Document upload failed: %s", exc, exc_info=True)
        return error_response(message=f"Document upload failed: {str(exc)}")


@router.get("", summary="List all documents (paginated)")
async def list_documents(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    status: str | None = Query(None),
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
):
    start_timer()
    try:
        service = _get_doc_service(db)
        result = await service.list_documents(
            page=page, per_page=per_page, category=category, status=status
        )
        return format_response(data=result)
    except Exception as exc:
        logger.error("Document list failed: %s", exc)
        return error_response(message="Failed to fetch documents")


@router.get("/stats", summary="Knowledge base statistics")
async def get_document_stats(
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
):
    start_timer()
    try:
        service = _get_doc_service(db)
        stats = await service.get_stats()
        return format_response(data=stats)
    except Exception as exc:
        logger.error("Document stats failed: %s", exc)
        return error_response(message="Failed to fetch document stats")


@router.get("/{document_id}", summary="Get document details with chunks")
async def get_document(
    document_id: str,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
):
    start_timer()
    try:
        service = _get_doc_service(db)
        doc = await service.get_document(document_id)
        if doc is None:
            return error_response(message="Document not found")
        return format_response(data=doc)
    except Exception as exc:
        logger.error("Get document failed: %s", exc)
        return error_response(message="Failed to fetch document")


@router.delete("/{document_id}", summary="Delete document (Admin only)")
async def delete_document(
    document_id: str,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))] = ...,
):
    start_timer()
    try:
        service = _get_doc_service(db)
        deleted = await service.delete_document(document_id)
        if not deleted:
            return error_response(message="Document not found")
        return format_response(message="Document deleted successfully", data={"id": document_id})
    except Exception as exc:
        logger.error("Delete document failed: %s", exc)
        return error_response(message="Failed to delete document")


@router.post("/search", summary="Semantic search across indexed documents")
async def search_documents(
    body: DocumentSearchRequest,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
):
    start_timer()
    try:
        service = _get_doc_service(db)
        result = await service.search_documents(
            query=body.query,
            top_k=body.top_k,
            category=body.category,
            score_threshold=body.score_threshold,
        )
        return format_response(
            data=result,
            processing_time=result.get("processing_time", 0.0),
        )
    except Exception as exc:
        logger.error("Document search failed: %s", exc)
        return error_response(message="Search failed")


@router.get("/{document_id}/chunks", summary="Get all chunks for a document")
async def get_document_chunks(
    document_id: str,
    db: Annotated[AsyncSession, Depends(get_db)] = ...,
    current_user: Annotated[User, Depends(get_current_user)] = ...,
):
    start_timer()
    try:
        service = _get_doc_service(db)
        chunks = await service.get_chunks(document_id)
        return format_response(data={"document_id": document_id, "chunks": chunks})
    except Exception as exc:
        logger.error("Get chunks failed: %s", exc)
        return error_response(message="Failed to fetch chunks")
