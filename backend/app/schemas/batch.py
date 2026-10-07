import uuid

from pydantic import BaseModel


class BatchMergeRequest(BaseModel):
    groups: list[list[uuid.UUID]]  # each inner list is one merge job's file_ids


class BatchCompressRequest(BaseModel):
    file_ids: list[uuid.UUID]
    quality: str = "medium"


class BatchSplitRequest(BaseModel):
    file_ids: list[uuid.UUID]
    page_ranges: list[tuple[int, int]]


class BatchConvertRequest(BaseModel):
    file_ids: list[uuid.UUID]
    target_format: str


class BatchOCRRequest(BaseModel):
    file_ids: list[uuid.UUID]
    languages: list[str] = ["english"]


class BatchWatermarkRequest(BaseModel):
    file_ids: list[uuid.UUID]
    text: str
    opacity: float = 0.3


class BatchEncryptRequest(BaseModel):
    file_ids: list[uuid.UUID]
    user_password: str


class BatchJobOut(BaseModel):
    job_ids: list[uuid.UUID]
