"""Document chunk ORM model — tracks which chunks belong to which document."""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON string of metadata
    embedding_id = Column(String(100), nullable=True)  # ChromaDB ID for re-sync
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    document = relationship("Document", backref="chunks")

    def __repr__(self) -> str:
        return f"<Chunk {self.document_id}[{self.chunk_index}]>"
