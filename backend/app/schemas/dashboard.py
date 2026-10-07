from pydantic import BaseModel


class DashboardStats(BaseModel):
    storage_used_bytes: int
    file_count: int
    jobs_last_30_days: int
