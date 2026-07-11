"""AI Platform router — all /ai/* endpoints.

Provides enterprise AI capabilities:
  - POST /ai/chat                    — RAG-powered assistant
  - POST /ai/predict/licenses        — License renewal prediction
  - POST /ai/anomaly/licenses         — Software wastage & anomaly detection
  - POST /ai/recommendations          — Recommendation engine
  - GET  /ai/analytics                — AI-powered analytics dashboard data
  - POST /ai/documents/upload         — Upload & index document (Admin)
  - GET  /ai/documents                — List documents (paginated)
  - GET  /ai/documents/stats          — Knowledge base stats
  - GET  /ai/documents/{id}           — Get document + chunks
  - DELETE /ai/documents/{id}         — Delete document (Admin)
  - POST /ai/documents/search         — Semantic search
  - GET  /ai/documents/{id}/chunks    — Get document chunks
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas import (
    AnomalyRequest,
    ChatRequest,
    PredictLicensesRequest,
    RecommendationRequest,
)
from app.ai.service import AIService
from app.ai.utils.response_formatter import error_response, start_timer
from app.database.session import get_db
from app.models.user import User
from app.security.dependencies import get_current_user, require_roles
from app.security.permissions import Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


def _get_ai_service(db: AsyncSession) -> AIService:
    """Dependency factory — builds a fully-wired AI service instance."""
    from app.ai.anomaly.isolation_forest import IsolationForestDetector
    from app.ai.anomaly.local_outlier_factor import LocalOutlierFactorDetector
    from app.ai.anomaly.wastage_detection_service import WastageDetectionService
    from app.ai.assistant.assistant_service import AssistantService
    from app.ai.embeddings.sentence_transformer_provider import SentenceTransformerProvider
    from app.ai.llm.openai_provider import OpenAIProvider
    from app.ai.prediction.arima_model import ARIMAPredictor
    from app.ai.prediction.license_prediction_service import LicensePredictionService
    from app.ai.prediction.prophet_model import ProphetPredictor
    from app.ai.prediction.random_forest_model import RandomForestPredictor
    from app.ai.rag.rag_service import RAGService
    from app.ai.recommendation.engine import RecommendationEngine
    from app.ai.vectorstore.chroma_store import ChromaStore

    embedder = SentenceTransformerProvider()
    vector_store = ChromaStore(embedding_dim=embedder.dimensions)
    rag_service = RAGService(embedder, vector_store, db)
    llm = OpenAIProvider()
    assistant = AssistantService(rag_service, llm=llm, db=db)

    predictor = LicensePredictionService(db)
    predictor.register_predictor(ProphetPredictor())
    predictor.register_predictor(ARIMAPredictor())
    predictor.register_predictor(RandomForestPredictor())

    wastage = WastageDetectionService(db)
    wastage.register_detector(IsolationForestDetector())
    wastage.register_detector(LocalOutlierFactorDetector())

    recommender = RecommendationEngine()

    return AIService(
        assistant=assistant,
        predictor=predictor,
        wastage=wastage,
        recommender=recommender,
    )


@router.post("/chat", summary="Enterprise AI assistant — RAG-powered Q&A")
async def ai_chat(
    body: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    start_timer()
    try:
        service = _get_ai_service(db)
        result = await service.chat(
            question=body.question,
            user_id=str(current_user.id),
            top_k=body.top_k,
            domain=body.domain,
        )
        return result
    except Exception as exc:
        logger.error("AI chat error: %s", exc, exc_info=True)
        return error_response(message=f"AI chat failed: {str(exc)}")


@router.post("/predict/licenses", summary="Predict optimal license count and renewal date")
async def predict_licenses(
    body: PredictLicensesRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    start_timer()
    try:
        service = _get_ai_service(db)
        result = await service.predict_licenses(
            features=body.model_dump(),
            user_id=str(current_user.id),
        )
        return result
    except Exception as exc:
        logger.error("License prediction error: %s", exc, exc_info=True)
        return error_response(message=f"Prediction failed: {str(exc)}")


@router.post("/anomaly/licenses", summary="Detect dormant accounts and license wastage")
async def detect_anomalies(
    body: AnomalyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    start_timer()
    try:
        service = _get_ai_service(db)
        result = await service.detect_anomalies(
            usage_data=body.usage_data,
            user_id=str(current_user.id),
            db=db,
        )
        return result
    except Exception as exc:
        logger.error("Anomaly detection error: %s", exc, exc_info=True)
        return error_response(message=f"Anomaly detection failed: {str(exc)}")


@router.post("/recommendations", summary="Generate IT asset management recommendations")
async def get_recommendations(
    body: RecommendationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER, Role.IT_SUPPORT))],
):
    start_timer()
    try:
        service = _get_ai_service(db)
        result = await service.get_recommendations(
            context=body.model_dump(),
            user_id=str(current_user.id),
        )
        return result
    except Exception as exc:
        logger.error("Recommendation error: %s", exc, exc_info=True)
        return error_response(message=f"Recommendation failed: {str(exc)}")


@router.get("/analytics", summary="AI-powered analytics dashboard data")
async def get_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.SUPER_ADMIN, Role.IT_MANAGER))],
):
    start_timer()
    try:
        service = _get_ai_service(db)
        result = await service.get_analytics(db)
        return result
    except Exception as exc:
        logger.error("Analytics error: %s", exc, exc_info=True)
        return error_response(message=f"Analytics failed: {str(exc)}")


# Include document management sub-router (lazy import — chromadb may be unavailable)
try:
    from app.ai.documents.router import router as documents_router
    router.include_router(documents_router)
except ImportError as exc:
    logger.warning("Documents router not loaded (%s). Document endpoints will be unavailable.", exc)
