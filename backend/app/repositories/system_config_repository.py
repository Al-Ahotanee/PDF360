from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.system import SystemConfiguration


class SystemConfigRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[SystemConfiguration]:
        stmt = select(SystemConfiguration).order_by(SystemConfiguration.key.asc())
        return list(self.db.execute(stmt).scalars().all())

    def get_by_key(self, key: str) -> SystemConfiguration | None:
        stmt = select(SystemConfiguration).where(SystemConfiguration.key == key)
        return self.db.execute(stmt).scalar_one_or_none()

    def set_key(self, key: str, value: dict, description: str | None = None) -> SystemConfiguration:
        config = self.get_by_key(key)
        if config:
            config.value = value
            if description is not None:
                config.description = description
            self.db.commit()
            self.db.refresh(config)
            return config

        config = SystemConfiguration(key=key, value=value, description=description)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def delete_key(self, key: str) -> bool:
        config = self.get_by_key(key)
        if config:
            self.db.delete(config)
            self.db.commit()
            return True
        return False
