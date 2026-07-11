"""Document ORM model for the AssetOptima RAG knowledge base."""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx, txt, csv
    file_size = Column(Integer, nullable=False)  # bytes
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # policy, procedure, sop, inventory, license, security, asset, general
    status = Column(String(20), nullable=False, default="pending")  # pending, indexed, failed
    chunk_count = Column(Integer, nullable=False, default=0)
    checksum = Column(String(64), nullable=True)  # SHA-256 for dedup
    uploaded_by = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    uploader = relationship("User", backref="documents")

    def __repr__(self) -> str:
        return f"<Document {self.original_filename} ({self.status})>"
