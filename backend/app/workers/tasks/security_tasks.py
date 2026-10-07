import uuid
from pathlib import Path

from app.db.session import SessionLocal
from app.repositories.file_repository import FileRepository
from app.repositories.job_repository import JobRepository
from app.services.pdf_engine import security as sec
from app.services.pdf_engine.core import PDFEngineError
from app.services.storage.factory import get_storage_provider
from app.workers.celery_app import celery_app
from app.workers.tasks.conversion_tasks import _save_bytes


@celery_app.task(bind=True, name="pdf.encrypt")
def encrypt_task(self, job_id: str, owner_id: str, file_id: str, user_password: str,
                  owner_password: str | None, allow_printing: bool, allow_copying: bool):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            result_bytes = sec.encrypt_pdf(
                storage.read(source.storage_key), user_password, owner_password, allow_printing, allow_copying
            )
            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_encrypted.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.decrypt")
def decrypt_task(self, job_id: str, owner_id: str, file_id: str, password: str):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            result_bytes = sec.decrypt_pdf(storage.read(source.storage_key), password)
            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_decrypted.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.watermark")
def watermark_task(self, job_id: str, owner_id: str, file_id: str, text: str, opacity: float):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            result_bytes = sec.add_watermark(storage.read(source.storage_key), text, opacity)
            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_watermarked.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.redact")
def redact_task(self, job_id: str, owner_id: str, file_id: str, redactions: list[dict]):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            result_bytes = sec.redact_areas(storage.read(source.storage_key), redactions)
            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_redacted.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.metadata")
def metadata_task(self, job_id: str, owner_id: str, file_id: str, action: str, metadata: dict | None):
    """action: 'set' or 'remove'."""
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            data = storage.read(source.storage_key)
            if action == "set":
                result_bytes = sec.set_metadata(data, metadata or {})
            elif action == "remove":
                result_bytes = sec.remove_metadata(data)
            else:
                raise PDFEngineError(f"Unknown metadata action: {action}")

            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_meta.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()
