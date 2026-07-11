"""AssetHistory Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel


class AssetHistoryResponse(BaseModel):
    id: str
    asset_id: str
    action: str
    performed_by: str | None
    performed_at: datetime
    old_values: str | None
    new_values: str | None
    notes: str | None

    model_config = {"from_attributes": True}
