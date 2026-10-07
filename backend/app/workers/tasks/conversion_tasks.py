"""
Celery tasks for format conversion and OCR — mirrors pdf_tasks.py's
pattern (own DB session, load Job + files, run engine, save result, update
status). Split into a separate module because these tasks pull from two
different engine modules (conversion.py, ocr.py) rather than core.py.
"""
import uuid
from pathlib import Path

from app.db.session import SessionLocal
from app.repositories.file_repository import FileRepository
from app.repositories.job_repository import JobRepository
from app.services.pdf_engine import conversion as conv
from app.services.pdf_engine import ocr as ocr_engine
from app.services.pdf_engine.core import PDFEngineError
from app.services.storage.factory import get_storage_provider
from app.workers.celery_app import celery_app

_MIME_BY_EXT = {
    "pdf": "application/pdf", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "txt": "text/plain",
    "html": "text/html", "epub": "application/epub+zip",
}


def _save_bytes(storage, files_repo, *, owner_id: uuid.UUID, filename: str, data: bytes):
    import io
    key = storage.build_key(str(owner_id), filename)
    size = storage.save(key, io.BytesIO(data))
    ext = Path(filename).suffix.lstrip(".").lower()
    mime = _MIME_BY_EXT.get(ext, "application/octet-stream")
    return files_repo.create(owner_id=owner_id, original_filename=filename, storage_key=key, mime_type=mime, size_bytes=size)


@celery_app.task(bind=True, name="pdf.convert_to_pdf")
def convert_to_pdf_task(self, job_id: str, owner_id: str, file_id: str):
    """Office document or image -> PDF, auto-dispatched by source file extension."""
    db = SessionLocal()
    try:
        jobs, files, storage = JobRepository(db), FileRepository(db), get_storage_provider()
        job = jobs.get_by_id(uuid.UUID(job_id))
        jobs.mark_processing(job, celery_task_id=self.request.id)
        try:
            source = files.get_by_id(uuid.UUID(file_id))
            if source is None:
                raise PDFEngineError("Source file not found.")
            ext = Path(source.original_filename).suffix.lower()
            data = storage.read(source.storage_key)

            if ext in (".png", ".jpg", ".jpeg"):
                result_bytes = conv.images_to_pdf([data])
            elif ext in (".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"):
                result_bytes = conv.office_to_pdf(data, ext)
            else:
                raise PDFEngineError(f"Unsupported source format for PDF conversion: {ext}")

            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.convert_from_pdf")
def convert_from_pdf_task(self, job_id: str, owner_id: str, file_id: str, target_format: str):
    """PDF -> docx | pptx | xlsx | png | jpg | txt."""
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
            stem = Path(source.original_filename).stem

            if target_format == "docx":
                out_bytes, out_name = conv.pdf_to_docx(data), f"{stem}.docx"
                result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=out_name, data=out_bytes)
                jobs.mark_done(job, result={"file_id": str(result_file.id)})
            elif target_format == "pptx":
                out_bytes, out_name = conv.pdf_to_pptx(data), f"{stem}.pptx"
                result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=out_name, data=out_bytes)
                jobs.mark_done(job, result={"file_id": str(result_file.id)})
            elif target_format == "xlsx":
                out_bytes, out_name = conv.pdf_to_xlsx(data), f"{stem}.xlsx"
                result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=out_name, data=out_bytes)
                jobs.mark_done(job, result={"file_id": str(result_file.id)})
            elif target_format in ("png", "jpg"):
                images = conv.pdf_to_images(data, fmt=target_format)
                result_ids = []
                for i, img_bytes in enumerate(images, start=1):
                    f = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_page{i}.{target_format}", data=img_bytes)
                    result_ids.append(str(f.id))
                jobs.mark_done(job, result={"file_ids": result_ids})
            elif target_format == "txt":
                text = conv.pdf_to_txt(data)
                result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}.txt", data=text.encode("utf-8"))
                jobs.mark_done(job, result={"file_id": str(result_file.id)})
            elif target_format == "html":
                html = conv.pdf_to_html(data)
                result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}.html", data=html.encode("utf-8"))
                jobs.mark_done(job, result={"file_id": str(result_file.id)})
            elif target_format == "epub":
                out_bytes = conv.pdf_to_epub(data, title=stem)
                result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}.epub", data=out_bytes)
                jobs.mark_done(job, result={"file_id": str(result_file.id)})
            else:
                raise PDFEngineError(f"Unsupported target format: {target_format}")
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()


@celery_app.task(bind=True, name="pdf.ocr")
def ocr_task(self, job_id: str, owner_id: str, file_id: str, languages: list[str], force: bool):
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
            ext = Path(source.original_filename).suffix.lower()

            if ext in (".png", ".jpg", ".jpeg"):
                result_bytes = ocr_engine.ocr_image_to_pdf(data, languages=languages)
            else:
                result_bytes = ocr_engine.ocr_pdf(data, languages=languages, force=force)

            stem = Path(source.original_filename).stem
            result_file = _save_bytes(storage, files, owner_id=uuid.UUID(owner_id), filename=f"{stem}_ocr.pdf", data=result_bytes)
            jobs.mark_done(job, result={"file_id": str(result_file.id)})
        except PDFEngineError as exc:
            jobs.mark_failed(job, str(exc))
        except Exception as exc:  # noqa: BLE001
            jobs.mark_failed(job, f"Unexpected error: {exc}")
    finally:
        db.close()
