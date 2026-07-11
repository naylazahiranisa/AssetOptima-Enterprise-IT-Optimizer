"""Document management Pydantic schemas for the RAG knowledge base."""

from datetime import datetime
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    file_size: int
    title: str | None
    description: str | None
    category: str | None
    status: str
    chunk_count: int
    uploaded_by: str
    uploaded_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    per_page: int


class DocumentUploadResponse(BaseModel):
    id: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    message: str


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    category: str | None = None
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class DocumentSearchResult(BaseModel):
    content: str
    metadata: dict
    score: float
    document_id: str
    chunk_index: int


class DocumentSearchResponse(BaseModel):
    results: list[DocumentSearchResult]
    total: int
    query: str


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: dict
    created_at: datetime

    model_config = {"from_attributes": True}
