import uuid
from pathlib import Path

from app.db.session import SessionLocal
from app.repositories.file_repository import FileRepository
from app.repositories.job_repository import JobRepository
from app.services.pdf_engine import core as pdf_engine
from app.services.pdf_engine import security as sec
from app.services.pdf_engine.core import PDFEngineError
from app.services.storage.factory import get_storage_provider
from app.workers.celery_app import celery_app
from app.workers.tasks.conversion_tasks import _save_bytes


def _run(self, job_id: str, owner_id: str, file_id: str, filename_suffix: str, op):
    """Shared plumbing for the single-file-in/single-file-out page ops below.
    `op` takes the source bytes and returns the result bytes."""
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            result_bytes = op(storage.read(source.storage_key))
            stem = Path(source.original_filename).stem
            result_file = _save_bytes(
                storage, files, owner_id=uuid.UUID(owner_id),
                filename=f"{stem}_{filename_suffix}.pdf", data=result_bytes,
            )
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.delete_pages")
def delete_pages_task(self, job_id: str, owner_id: str, file_id: str, page_numbers: list[int]):
    _run(self, job_id, owner_id, file_id, "edited", lambda b: pdf_engine.delete_pages(b, page_numbers))


@celery_app.task(bind=True, name="pdf.insert_blank_page")
def insert_blank_page_task(self, job_id: str, owner_id: str, file_id: str, position: int):
    _run(self, job_id, owner_id, file_id, "edited", lambda b: pdf_engine.insert_blank_page(b, position))


@celery_app.task(bind=True, name="pdf.duplicate_page")
def duplicate_page_task(self, job_id: str, owner_id: str, file_id: str, page_number: int):
    _run(self, job_id, owner_id, file_id, "edited", lambda b: pdf_engine.duplicate_page(b, page_number))


@celery_app.task(bind=True, name="pdf.reorder_pages")
def reorder_pages_task(self, job_id: str, owner_id: str, file_id: str, new_order: list[int]):
    _run(self, job_id, owner_id, file_id, "reordered", lambda b: pdf_engine.reorder_pages(b, new_order))


@celery_app.task(bind=True, name="pdf.page_numbers")
def page_numbers_task(self, job_id: str, owner_id: str, file_id: str, position: str, start_at: int, fmt: str):
    _run(self, job_id, owner_id, file_id, "numbered",
         lambda b: pdf_engine.add_page_numbers(b, position=position, start_at=start_at, fmt=fmt))


@celery_app.task(bind=True, name="pdf.header_footer")
def header_footer_task(self, job_id: str, owner_id: str, file_id: str, header_text: str | None, footer_text: str | None):
    _run(self, job_id, owner_id, file_id, "annotated",
         lambda b: pdf_engine.add_header_footer(b, header_text=header_text, footer_text=footer_text))


@celery_app.task(bind=True, name="pdf.sign")
def sign_task(self, job_id: str, owner_id: str, file_id: str, signer_name: str, page: int,
              x: float, y: float, reason: str | None):
    _run(self, job_id, owner_id, file_id, "signed",
         lambda b: sec.sign_pdf(b, signer_name=signer_name, page=page, x=x, y=y, reason=reason))


@celery_app.task(bind=True, name="pdf.set_permissions")
def set_permissions_task(self, job_id: str, owner_id: str, file_id: str, allow_printing: bool,
                          allow_copying: bool, allow_editing: bool, allow_annotations: bool):
    _run(self, job_id, owner_id, file_id, "restricted",
         lambda b: sec.set_permissions(b, allow_printing=allow_printing, allow_copying=allow_copying,
                                        allow_editing=allow_editing, allow_annotations=allow_annotations))


@celery_app.task(bind=True, name="pdf.rotate")
def rotate_task(self, job_id: str, owner_id: str, file_id: str, page_numbers: list[int], degrees: int):
    _run(self, job_id, owner_id, file_id, "rotated", lambda b: pdf_engine.rotate_pages(b, page_numbers, degrees))


@celery_app.task(bind=True, name="pdf.extract")
def extract_task(self, job_id: str, owner_id: str, file_id: str, page_numbers: list[int]):
    _run(self, job_id, owner_id, file_id, "extracted", lambda b: pdf_engine.extract_pages(b, page_numbers))


@celery_app.task(bind=True, name="pdf.crop")
def crop_task(self, job_id: str, owner_id: str, file_id: str, margins: dict, page_numbers: list[int] | None):
    _run(self, job_id, owner_id, file_id, "cropped", lambda b: pdf_engine.crop_pages(b, margins, page_numbers))


@celery_app.task(bind=True, name="pdf.remove_watermark")
def remove_watermark_task(self, job_id: str, owner_id: str, file_id: str, text: str):
    _run(self, job_id, owner_id, file_id, "unwatermarked", lambda b: sec.remove_watermark(b, text))


@celery_app.task(bind=True, name="pdf.replace_pages")
def replace_pages_task(self, job_id: str, owner_id: str, file_id: str, replacement_file_id: str, page_numbers: list[int]):
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            replacement = files.get_by_id(uuid.UUID(replacement_file_id))
            if source is None or replacement is None:
                raise PDFEngineError("Source or replacement file not found.")
            result_bytes = pdf_engine.replace_pages(
                storage.read(source.storage_key), storage.read(replacement.storage_key), page_numbers,
            )
            stem = Path(source.original_filename).stem
            result_file = _save_bytes(
                storage, files, owner_id=uuid.UUID(owner_id),
                filename=f"{stem}_replaced.pdf", data=result_bytes,
            )
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()
