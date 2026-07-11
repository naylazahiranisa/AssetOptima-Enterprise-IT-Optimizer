"""Base interfaces and types for the AssetOptima AI Platform.

Every AI sub-module (RAG, prediction, anomaly, recommendation) follows
the interface pattern defined here so ML models can be swapped without
changing the orchestration layer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AIResponse:
    """Standard response envelope for all AI endpoints."""

    success: bool = True
    message: str = "Operation successful"
    data: Any = None
    confidence: float | None = None
    source_documents: list[dict] = field(default_factory=list)
    processing_time: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Document:
    """A single document chunk with metadata."""

    content: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0


class EmbeddingProvider(ABC):
    """Abstract interface for text embedding models."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        ...


class VectorStore(ABC):
    """Abstract interface for vector databases."""

    @abstractmethod
    async def add(self, documents: list[Document], embeddings: list[list[float]]) -> None:
        ...

    @abstractmethod
    async def search(self, query_embedding: list[float], top_k: int = 5,
                     metadata_filter: dict | None = None,
                     score_threshold: float | None = None) -> list[Document]:
        ...

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        ...


class BasePredictor(ABC):
    """Abstract interface for time-series / regression prediction models."""

    @abstractmethod
    async def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def train(self, historical_data: list[dict]) -> None:
        ...


class BaseAnomalyDetector(ABC):
    """Abstract interface for anomaly / outlier detection models."""

    @abstractmethod
    async def detect(self, features: list[dict]) -> list[dict]:
        ...

    @abstractmethod
    async def fit(self, data: list[dict]) -> None:
        ...


class BaseRecommender(ABC):
    """Abstract interface for the recommendation engine."""

    @abstractmethod
    async def generate(self, context: dict[str, Any]) -> list[dict]:
        ...
