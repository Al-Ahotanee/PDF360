import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.billing import SubscriptionPlan
from app.models.user import User
from app.schemas.billing import (
    ApiKeyCreateRequest,
    ApiKeyCreated,
    ApiKeyOut,
    ChangePlanRequest,
    PaymentOut,
    SettingsOut,
    SettingsUpdateRequest,
    SubscriptionOut,
)
from app.services.billing_service import ApiKeyService, BillingService, SettingsService

router = APIRouter(prefix="/billing", tags=["Billing"])
settings_router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/subscription", response_model=SubscriptionOut)
def get_subscription(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BillingService(db).get_or_create_subscription(user.id)


@router.post("/subscription", response_model=SubscriptionOut)
def change_plan(data: ChangePlanRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BillingService(db).change_plan(user_id=user.id, plan=SubscriptionPlan(data.plan))


@router.post("/subscription/cancel", response_model=SubscriptionOut)
def cancel_subscription(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BillingService(db).cancel_subscription(user_id=user.id)


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return BillingService(db).list_payments(user.id)


@router.get("/api-keys", response_model=list[ApiKeyOut])
def list_api_keys(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ApiKeyService(db).list_for_user(user.id)


@router.post("/api-keys", response_model=ApiKeyCreated, status_code=201)
def create_api_key(data: ApiKeyCreateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    key, raw_key = ApiKeyService(db).create(user_id=user.id, name=data.name)
    return ApiKeyCreated(
        id=key.id, name=key.name, key_prefix=key.key_prefix, is_active=key.is_active,
        last_used_at=key.last_used_at, created_at=key.created_at, raw_key=raw_key,
    )


@router.delete("/api-keys/{key_id}", response_model=ApiKeyOut)
def revoke_api_key(key_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ApiKeyService(db).revoke(user_id=user.id, key_id=key_id)


@settings_router.get("", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return SettingsOut(preferences=SettingsService(db).get_preferences(user.id))


@settings_router.patch("", response_model=SettingsOut)
def update_settings(data: SettingsUpdateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return SettingsOut(preferences=SettingsService(db).update_preferences(user.id, data.preferences))
