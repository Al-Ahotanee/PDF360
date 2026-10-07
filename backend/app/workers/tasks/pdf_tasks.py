"""
Celery tasks for merge/split/compress. Each task:
  1. Opens its own DB session (workers are separate processes from the API,
     so they can't reuse FastAPI's request-scoped `get_db`).
  2. Loads the Job + input files.
  3. Runs the pure pdf_engine function.
  4. Writes result file(s) to storage, creates File rows for them.
  5. Marks the job done/failed.

Routes never call pdf_engine directly — they create a Job and call
`.delay()` on one of these, so the API responds immediately with a job_id.
"""
import io
import uuid

from app.db.session import SessionLocal
from app.models.job import JobStatus
from app.repositories.file_repository import FileRepository
from app.repositories.job_repository import JobRepository
from app.services.pdf_engine import core as pdf_engine
from app.services.pdf_engine.core import PDFEngineError
from app.services.storage.factory import get_storage_provider
from app.workers.celery_app import celery_app


def _save_result_file(storage, files_repo, *, owner_id: uuid.UUID, filename: str, data: bytes):
    key = storage.build_key(str(owner_id), filename)
    size = storage.save(key, io.BytesIO(data))
    return files_repo.create(
        owner_id=owner_id,
        original_filename=filename,
        storage_key=key,
        mime_type="application/pdf",
        size_bytes=size,
    )


@celery_app.task(bind=True, name="pdf.merge")
def merge_task(self, job_id: str, owner_id: str, file_ids: list[str]):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source_files = files.get_many_by_ids([uuid.UUID(fid) for fid in file_ids])
            if len(source_files) != len(file_ids):
                raise PDFEngineError("One or more source files were not found.")
            # Preserve the order the client requested, not DB return order.
            by_id = {str(f.id): f for f in source_files}
            ordered = [by_id[fid] for fid in file_ids]

            byte_contents = [storage.read(f.storage_key) for f in ordered]
            merged_bytes = pdf_engine.merge_pdfs(byte_contents)

            result_file = _save_result_file(
                storage, files, owner_id=uuid.UUID(owner_id), filename="merged.pdf", data=merged_bytes
            )
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001 — job failure must never crash the worker
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.split")
def split_task(self, job_id: str, owner_id: str, file_id: str, page_ranges: list[list[int]]):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            ranges = [(r[0], r[1]) for r in page_ranges]
            parts = pdf_engine.split_pdf(storage.read(source.storage_key), ranges)

            result_ids = []
            for i, part_bytes in enumerate(parts, start=1):
                f = _save_result_file(
                    storage, files, owner_id=uuid.UUID(owner_id),
                    filename=f"split_part_{i}.pdf", data=part_bytes,
                )
                result_ids.append(str(f.id))
            jobs.mark_done(job, result={"file_ids": result_ids})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.compress")
def compress_task(self, job_id: str, owner_id: str, file_id: str, quality: str,
                   custom_dpi_target: int | None = None, custom_quality: int | None = None):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            compressed = pdf_engine.compress_pdf(
                storage.read(source.storage_key), quality,
                custom_dpi_target=custom_dpi_target, custom_quality=custom_quality,
            )

            result_file = _save_result_file(
                storage, files, owner_id=uuid.UUID(owner_id),
                filename=f"compressed_{source.original_filename}", data=compressed,
            )
            jobs.mark_done(job, result={
                "file_id": str(result_file.id),
                "original_size": source.size_bytes,
                "compressed_size": result_file.size_bytes,
            })
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()
