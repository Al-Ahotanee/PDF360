import io
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file import File
from app.models.job import Job, JobType
from app.repositories.file_repository import FileRepository
from app.repositories.job_repository import JobRepository
from app.services.pdf_engine import core as pdf_engine
from app.services.pdf_engine import security as sec
from app.services.storage.factory import get_storage_provider
from app.workers.tasks.conversion_tasks import convert_from_pdf_task, convert_to_pdf_task, ocr_task
from app.workers.tasks.pdf_tasks import compress_task, merge_task, split_task
from app.workers.tasks.security_tasks import decrypt_task, encrypt_task, metadata_task, redact_task, watermark_task
from app.workers.tasks.page_ops_tasks import (
    crop_task, delete_pages_task, duplicate_page_task, extract_task, header_footer_task,
    insert_blank_page_task, page_numbers_task, remove_watermark_task, reorder_pages_task,
    replace_pages_task, rotate_task, set_permissions_task, sign_task,
)


class PDFService:
    """
    Thin orchestration layer: verifies the caller owns every file involved,
    creates a Job row, and dispatches the matching Celery task. Contains no
    PDF logic itself — that all lives in pdf_engine and the task modules.
    """

    def __init__(self, db: Session):
        self.db = db
        self.jobs = JobRepository(db)
        self.files = FileRepository(db)

    def _dispatch(self, job: Job, task, *args, **kwargs) -> Job:
        task.delay(*args, **kwargs)
        if settings.CELERY_ALWAYS_EAGER:
            try:
                self.db.refresh(job)
            except Exception:
                pass
        return job

    def _assert_owns_all(self, owner_id: uuid.UUID, file_ids: list[uuid.UUID], required_permission=None) -> None:
        from app.models.file_share import SharePermission
        from app.services.file_access import has_at_least
        perm = required_permission or SharePermission.EDIT

        found = self.files.get_many_by_ids(file_ids)
        found_ids = {f.id for f in found}
        missing = set(file_ids) - found_ids
        if missing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Files not found: {missing}")
        for f in found:
            if not has_at_least(self.db, file=f, user_id=owner_id, required=perm):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have required permission for all requested files.")

    def merge(self, *, owner_id: uuid.UUID, file_ids: list[uuid.UUID]) -> Job:
        if len(file_ids) < 2:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Merge requires at least 2 files.")
        self._assert_owns_all(owner_id, file_ids)
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.MERGE, input_params={"file_ids": [str(f) for f in file_ids]})
        return self._dispatch(job, merge_task, str(job.id), str(owner_id), [str(f) for f in file_ids])

    def split(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, page_ranges: list[tuple[int, int]]) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(
            owner_id=owner_id, job_type=JobType.SPLIT,
            input_params={"file_id": str(file_id), "page_ranges": page_ranges},
        )
        return self._dispatch(job, split_task, str(job.id), str(owner_id), str(file_id), [list(r) for r in page_ranges])

    def compress(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, quality: str,
                 custom_dpi_target: int | None = None, custom_quality: int | None = None) -> Job:
        if quality not in ("low", "medium", "high", "custom"):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="quality must be low, medium, high, or custom.")
        if quality == "custom" and (custom_dpi_target is None or custom_quality is None):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                 detail="custom_dpi_target and custom_quality are required for quality='custom'.")
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(
            owner_id=owner_id, job_type=JobType.COMPRESS,
            input_params={"file_id": str(file_id), "quality": quality},
        )
        return self._dispatch(job, compress_task, str(job.id), str(owner_id), str(file_id), quality, custom_dpi_target, custom_quality)

    def get_owned_job(self, *, job_id: uuid.UUID, owner_id: uuid.UUID) -> Job:
        job = self.jobs.get_by_id(job_id)
        if job is None or job.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        return job

    def convert_to_pdf(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.CONVERT_TO_PDF, input_params={"file_id": str(file_id)})
        return self._dispatch(job, convert_to_pdf_task, str(job.id), str(owner_id), str(file_id))

    def convert_from_pdf(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, target_format: str) -> Job:
        allowed = {"docx", "pptx", "xlsx", "png", "jpg", "txt", "html", "epub"}
        if target_format not in allowed:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"target_format must be one of {sorted(allowed)}.")
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(
            owner_id=owner_id, job_type=JobType.CONVERT_FROM_PDF,
            input_params={"file_id": str(file_id), "target_format": target_format},
        )
        return self._dispatch(job, convert_from_pdf_task, str(job.id), str(owner_id), str(file_id), target_format)

    def ocr(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, languages: list[str], force: bool) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(
            owner_id=owner_id, job_type=JobType.OCR,
            input_params={"file_id": str(file_id), "languages": languages, "force": force},
        )
        return self._dispatch(job, ocr_task, str(job.id), str(owner_id), str(file_id), languages, force)

    def encrypt(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, user_password: str,
                owner_password: str | None, allow_printing: bool, allow_copying: bool) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.ENCRYPT, input_params={"file_id": str(file_id)})
        return self._dispatch(job, encrypt_task, str(job.id), str(owner_id), str(file_id), user_password, owner_password, allow_printing, allow_copying)

    def decrypt(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, password: str) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.DECRYPT, input_params={"file_id": str(file_id)})
        return self._dispatch(job, decrypt_task, str(job.id), str(owner_id), str(file_id), password)

    def watermark(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, text: str, opacity: float) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(
            owner_id=owner_id, job_type=JobType.WATERMARK,
            input_params={"file_id": str(file_id), "text": text},
        )
        return self._dispatch(job, watermark_task, str(job.id), str(owner_id), str(file_id), text, opacity)

    def redact(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, redactions: list[dict]) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.REDACT, input_params={"file_id": str(file_id)})
        return self._dispatch(job, redact_task, str(job.id), str(owner_id), str(file_id), redactions)

    def set_metadata(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, metadata: dict) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.METADATA, input_params={"file_id": str(file_id), "action": "set"})
        return self._dispatch(job, metadata_task, str(job.id), str(owner_id), str(file_id), "set", metadata)

    def remove_metadata(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.METADATA, input_params={"file_id": str(file_id), "action": "remove"})
        return self._dispatch(job, metadata_task, str(job.id), str(owner_id), str(file_id), "remove", None)

    def get_metadata(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> dict:
        """Synchronous — metadata reads are fast and don't warrant a job."""
        from app.models.file_share import SharePermission
        self._assert_owns_all(owner_id, [file_id], required_permission=SharePermission.VIEW)
        file = self.files.get_by_id(file_id)
        storage = get_storage_provider()
        return sec.get_metadata(storage.read(file.storage_key))

    def delete_pages(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, page_numbers: list[int]) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.DELETE_PAGES, input_params={"file_id": str(file_id), "page_numbers": page_numbers})
        return self._dispatch(job, delete_pages_task, str(job.id), str(owner_id), str(file_id), page_numbers)

    def insert_blank_page(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, position: int) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.INSERT_BLANK_PAGE, input_params={"file_id": str(file_id), "position": position})
        return self._dispatch(job, insert_blank_page_task, str(job.id), str(owner_id), str(file_id), position)

    def duplicate_page(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, page_number: int) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.DUPLICATE_PAGE, input_params={"file_id": str(file_id), "page_number": page_number})
        return self._dispatch(job, duplicate_page_task, str(job.id), str(owner_id), str(file_id), page_number)

    def reorder_pages(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, new_order: list[int]) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.REORDER_PAGES, input_params={"file_id": str(file_id), "new_order": new_order})
        return self._dispatch(job, reorder_pages_task, str(job.id), str(owner_id), str(file_id), new_order)

    def add_page_numbers(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, position: str, start_at: int, fmt: str) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.PAGE_NUMBERS, input_params={"file_id": str(file_id)})
        return self._dispatch(job, page_numbers_task, str(job.id), str(owner_id), str(file_id), position, start_at, fmt)

    def add_header_footer(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, header_text: str | None, footer_text: str | None) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.HEADER_FOOTER, input_params={"file_id": str(file_id)})
        return self._dispatch(job, header_footer_task, str(job.id), str(owner_id), str(file_id), header_text, footer_text)

    def sign(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, signer_name: str, page: int,
             x: float, y: float, reason: str | None) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.SIGN, input_params={"file_id": str(file_id), "signer_name": signer_name})
        return self._dispatch(job, sign_task, str(job.id), str(owner_id), str(file_id), signer_name, page, x, y, reason)

    def verify_signature(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> dict:
        """Synchronous — a metadata read, same rationale as get_metadata."""
        from app.models.file_share import SharePermission
        self._assert_owns_all(owner_id, [file_id], required_permission=SharePermission.VIEW)
        file = self.files.get_by_id(file_id)
        storage = get_storage_provider()
        return sec.verify_signature(storage.read(file.storage_key))

    def set_permissions(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, allow_printing: bool,
                         allow_copying: bool, allow_editing: bool, allow_annotations: bool) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.PERMISSIONS, input_params={"file_id": str(file_id)})
        return self._dispatch(job, set_permissions_task, str(job.id), str(owner_id), str(file_id), allow_printing, allow_copying, allow_editing, allow_annotations)

    def rotate(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, page_numbers: list[int], degrees: int) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.ROTATE, input_params={"file_id": str(file_id)})
        return self._dispatch(job, rotate_task, str(job.id), str(owner_id), str(file_id), page_numbers, degrees)

    def extract(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, page_numbers: list[int]) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.EXTRACT, input_params={"file_id": str(file_id)})
        return self._dispatch(job, extract_task, str(job.id), str(owner_id), str(file_id), page_numbers)

    def crop(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, margins: dict, page_numbers: list[int] | None) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.CROP, input_params={"file_id": str(file_id)})
        return self._dispatch(job, crop_task, str(job.id), str(owner_id), str(file_id), margins, page_numbers)

    def replace_pages(self, *, owner_id: uuid.UUID, file_id: uuid.UUID,
                       replacement_file_id: uuid.UUID, page_numbers: list[int]) -> Job:
        self._assert_owns_all(owner_id, [file_id, replacement_file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.REPLACE_PAGES, input_params={"file_id": str(file_id)})
        return self._dispatch(job, replace_pages_task, str(job.id), str(owner_id), str(file_id), str(replacement_file_id), page_numbers)

    def remove_watermark(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, text: str) -> Job:
        self._assert_owns_all(owner_id, [file_id])
        job = self.jobs.create(owner_id=owner_id, job_type=JobType.REMOVE_WATERMARK, input_params={"file_id": str(file_id)})
        return self._dispatch(job, remove_watermark_task, str(job.id), str(owner_id), str(file_id), text)

    def get_bookmarks(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> list[dict]:
        """Synchronous — same rationale as get_metadata: a fast metadata read."""
        from app.models.file_share import SharePermission
        self._assert_owns_all(owner_id, [file_id], required_permission=SharePermission.VIEW)
        file = self.files.get_by_id(file_id)
        storage = get_storage_provider()
        return pdf_engine.get_bookmarks(storage.read(file.storage_key))

    def set_bookmarks(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, bookmarks: list[dict]) -> File:
        """Synchronous, returning the new File directly (like the editor
        endpoints) — setting a table of contents is a single fast
        in-memory rewrite, not multi-minute batch work."""
        self._assert_owns_all(owner_id, [file_id])
        source = self.files.get_by_id(file_id)
        storage = get_storage_provider()
        new_bytes = pdf_engine.set_bookmarks(storage.read(source.storage_key), bookmarks)
        filename = f"{Path(source.original_filename).stem}_bookmarked.pdf"
        key = storage.build_key(str(owner_id), filename)
        size = storage.save(key, io.BytesIO(new_bytes))
        return self.files.create(
            owner_id=owner_id, original_filename=filename,
            storage_key=key, mime_type="application/pdf", size_bytes=size,
        )
