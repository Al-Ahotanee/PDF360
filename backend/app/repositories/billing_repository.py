import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.billing import Payment, Subscription
from app.models.system import ApiKey, Setting


class BillingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_subscription(self, user_id: uuid.UUID) -> Subscription | None:
        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
        )
        return self.db.execute(stmt).scalars().first()

    def create_subscription(self, **kwargs) -> Subscription:
        sub = Subscription(**kwargs)
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def list_payments(self, user_id: uuid.UUID, limit: int = 50) -> list[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def create_payment(self, **kwargs) -> Payment:
        payment = Payment(**kwargs)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment


class ApiKeyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: uuid.UUID) -> list[ApiKey]:
        stmt = select(ApiKey).where(ApiKey.user_id == user_id).order_by(ApiKey.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_id(self, key_id: uuid.UUID) -> ApiKey | None:
        return self.db.get(ApiKey, key_id)

    def create(self, **kwargs) -> ApiKey:
        key = ApiKey(**kwargs)
        self.db.add(key)
        self.db.commit()
        self.db.refresh(key)
        return key

    def revoke(self, key: ApiKey) -> ApiKey:
        key.is_active = False
        self.db.commit()
        self.db.refresh(key)
        return key


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_for_user(self, user_id: uuid.UUID) -> Setting | None:
        stmt = select(Setting).where(Setting.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert(self, user_id: uuid.UUID, preferences: dict) -> Setting:
        existing = self.get_for_user(user_id)
        if existing:
            existing.preferences = {**existing.preferences, **preferences}
            self.db.commit()
            self.db.refresh(existing)
            return existing
        setting = Setting(user_id=user_id, preferences=preferences)
        self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting
