import uuid
from datetime import datetime

from pydantic import BaseModel


class SetRoleRequest(BaseModel):
    role_name: str


class SetActiveRequest(BaseModel):
    is_active: bool


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class AuditLogOut(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    target_type: str | None
    target_id: uuid.UUID | None
    metadata_json: dict

    model_config = {"from_attributes": True}


class SystemHealthOut(BaseModel):
    status: str
    queued_jobs: int
    processing_jobs: int
    failed_jobs_last_100: int


class AnalyticsOut(BaseModel):
    total_users: int
    active_users: int
    total_files: int
    total_jobs: int
    premium_subscribers: int
    total_revenue: float


class FeatureFlagOut(BaseModel):
    key: str
    value: dict
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagSetRequest(BaseModel):
    key: str
    value: dict
    description: str | None = None

