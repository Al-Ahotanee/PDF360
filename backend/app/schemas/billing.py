import uuid
from datetime import datetime

from pydantic import BaseModel


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    plan: str
    status: str
    current_period_end: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangePlanRequest(BaseModel):
    plan: str  # free | premium_monthly | premium_yearly


class PaymentOut(BaseModel):
    id: uuid.UUID
    amount: float
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApiKeyCreated(ApiKeyOut):
    raw_key: str  # only ever present in the create response


class ApiKeyCreateRequest(BaseModel):
    name: str


class SettingsOut(BaseModel):
    preferences: dict


class SettingsUpdateRequest(BaseModel):
    preferences: dict
