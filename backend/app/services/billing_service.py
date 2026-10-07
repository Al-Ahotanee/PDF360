import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.billing import Payment, PaymentStatus, Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.system import ApiKey
from app.repositories.billing_repository import ApiKeyRepository, BillingRepository, SettingsRepository

_PLAN_PRICES = {
    SubscriptionPlan.FREE: 0,
    SubscriptionPlan.PREMIUM_MONTHLY: 9.99,
    SubscriptionPlan.PREMIUM_YEARLY: 89.99,
}


class BillingService:
    """
    Payment-provider-agnostic on purpose (see docs/01-requirements.md — the
    provider choice is deferred). `change_plan` records the subscription and
    payment state changes locally so the rest of the app (feature gating,
    the dashboard, admin revenue view) has something real to read; wiring
    an actual provider later means only replacing the body of this method,
    not any caller.
    """

    def __init__(self, db: Session):
        self.db = db
        self.billing = BillingRepository(db)

    def get_or_create_subscription(self, user_id: uuid.UUID) -> Subscription:
        sub = self.billing.get_active_subscription(user_id)
        if sub is not None:
            return sub
        return self.billing.create_subscription(user_id=user_id, plan=SubscriptionPlan.FREE, status=SubscriptionStatus.ACTIVE)

    def change_plan(self, *, user_id: uuid.UUID, plan: SubscriptionPlan, external_reference: str | None = None) -> Subscription:
        if plan not in _PLAN_PRICES:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown plan.")
        period_end = None
        if plan == SubscriptionPlan.PREMIUM_MONTHLY:
            period_end = datetime.now(timezone.utc) + timedelta(days=30)
        elif plan == SubscriptionPlan.PREMIUM_YEARLY:
            period_end = datetime.now(timezone.utc) + timedelta(days=365)

        sub = self.billing.create_subscription(
            user_id=user_id, plan=plan, status=SubscriptionStatus.ACTIVE,
            current_period_end=period_end, external_reference=external_reference,
        )
        amount = _PLAN_PRICES[plan]
        if amount > 0:
            self.billing.create_payment(
                user_id=user_id, subscription_id=sub.id, amount=amount,
                currency="USD", status=PaymentStatus.SUCCEEDED, external_reference=external_reference,
            )
        return sub

    def cancel_subscription(self, *, user_id: uuid.UUID) -> Subscription:
        sub = self.get_or_create_subscription(user_id)
        sub.status = SubscriptionStatus.CANCELED
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def list_payments(self, user_id: uuid.UUID) -> list[Payment]:
        return self.billing.list_payments(user_id)


class ApiKeyService:
    def __init__(self, db: Session):
        self.db = db
        self.keys = ApiKeyRepository(db)

    def list_for_user(self, user_id: uuid.UUID) -> list[ApiKey]:
        return self.keys.list_for_user(user_id)

    def create(self, *, user_id: uuid.UUID, name: str) -> tuple[ApiKey, str]:
        """Returns (record, raw_key) — the raw key is shown to the user exactly once."""
        raw_key = f"pdf360_{secrets.token_urlsafe(32)}"
        prefix = raw_key[:12]
        key = self.keys.create(user_id=user_id, name=name, key_prefix=prefix, hashed_key=hash_password(raw_key))
        return key, raw_key

    def revoke(self, *, user_id: uuid.UUID, key_id: uuid.UUID) -> ApiKey:
        key = self.keys.get_by_id(key_id)
        if key is None or key.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found.")
        return self.keys.revoke(key)

    def authenticate(self, raw_key: str) -> ApiKey | None:
        """For future use by an API-key auth dependency — not wired into any
        route yet (JWT is the only auth path today), kept here so adding
        that dependency later doesn't require touching this service."""
        if not raw_key.startswith("pdf360_"):
            return None
        prefix = raw_key[:12]
        for key in self.db.query(ApiKey).filter(ApiKey.key_prefix == prefix, ApiKey.is_active.is_(True)).all():
            if verify_password(raw_key, key.hashed_key):
                return key
        return None


class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = SettingsRepository(db)

    def get_preferences(self, user_id: uuid.UUID) -> dict:
        existing = self.settings.get_for_user(user_id)
        return existing.preferences if existing else {}

    def update_preferences(self, user_id: uuid.UUID, preferences: dict) -> dict:
        return self.settings.upsert(user_id, preferences).preferences
