"""AI Platform Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000, description="User question about IT assets, licenses, or policies")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    domain: str | None = Field(None, description="Optional domain filter: policy, procedure, sop, inventory, license, security, asset")


class ChatResponse(BaseModel):
    answer: str
    source_documents: list[dict] = []
    confidence: float = 0.0
    processing_time: float = 0.0


class PredictLicensesRequest(BaseModel):
    software_id: str | None = None
    software_name: str | None = Field(None, max_length=255)
    current_license_count: int = Field(default=0, ge=0)
    current_renewal_date: str | None = None
    employee_count: int = Field(default=0, ge=0)
    department_growth_rate: float = Field(default=0.0, ge=-1.0, le=10.0)
    historical_usage: list[dict] = Field(default_factory=list)


class AnomalyRequest(BaseModel):
    software_id: str | None = None
    days_threshold: int = Field(default=30, ge=1, le=365)
    usage_data: list[dict] = Field(default_factory=list)


class RecommendationRequest(BaseModel):
    dormant_accounts: list[dict] = Field(default_factory=list)
    potential_annual_savings: float = 0.0
    predicted_count: int | None = None
    current_license_count: int | None = None
    expiring_licenses: list[dict] = Field(default_factory=list)
    unused_assets: list[dict] = Field(default_factory=list)
