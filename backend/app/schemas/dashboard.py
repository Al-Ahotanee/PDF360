import uuid
from datetime import datetime

from pydantic import BaseModel


class DashboardStats(BaseModel):
    storage_used_bytes: int
    file_count: int
    jobs_last_30_days: int


class ActivityLogOut(BaseModel):
    id: uuid.UUID
    action: str
    resource_type: str | None
    resource_id: uuid.UUID | None
    metadata_json: dict
    created_at: datetime

    model_config = {"from_attributes": True}
