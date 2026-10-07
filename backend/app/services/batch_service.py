"""
Batch service — thin fan-out layer over PDFService. Each item in a batch
becomes its own Job (same uniform job model as single-file operations), so
the client polls/tracks N job_ids exactly like it would for N separate
requests — batch just saves the round trips of submitting them one by one.

Deliberately does NOT create a "batch" DB entity — job list identity lives
in the response the client receives when submitting, keeping the schema
from growing a redundant parallel concept. If batch-level progress
dashboards are needed later, that's a query grouping jobs by
created_at + owner, not a new table.
"""
import uuid

from sqlalchemy.orm import Session

from app.services.pdf_service import PDFService


class BatchService:
    def __init__(self, db: Session):
        self.db = db
        self.pdf = PDFService(db)

    def batch_merge(self, *, owner_id: uuid.UUID, groups: list[list[uuid.UUID]]) -> list[uuid.UUID]:
        return [self.pdf.merge(owner_id=owner_id, file_ids=group).id for group in groups]

    def batch_compress(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID], quality: str) -> list[uuid.UUID]:
        return [self.pdf.compress(owner_id=owner_id, file_id=fid, quality=quality).id for fid in file_ids]

    def batch_split(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID], page_ranges: list[tuple[int, int]]) -> list[uuid.UUID]:
        return [self.pdf.split(owner_id=owner_id, file_id=fid, page_ranges=page_ranges).id for fid in file_ids]

    def batch_convert(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID], target_format: str) -> list[uuid.UUID]:
        return [self.pdf.convert_from_pdf(owner_id=owner_id, file_id=fid, target_format=target_format).id for fid in file_ids]

    def batch_ocr(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID], languages: list[str]) -> list[uuid.UUID]:
        return [self.pdf.ocr(owner_id=owner_id, file_id=fid, languages=languages, force=False).id for fid in file_ids]

    def batch_watermark(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID], text: str, opacity: float) -> list[uuid.UUID]:
        return [self.pdf.watermark(owner_id=owner_id, file_id=fid, text=text, opacity=opacity).id for fid in file_ids]

    def batch_encrypt(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID], user_password: str) -> list[uuid.UUID]:
        return [
            self.pdf.encrypt(
                owner_id=owner_id, file_id=fid, user_password=user_password,
                owner_password=None, allow_printing=True, allow_copying=True,
            ).id
            for fid in file_ids
        ]
