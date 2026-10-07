import io
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.services.pdf_engine import editor
from app.services.pdf_engine.core import PDFEngineError
from app.services.storage.factory import get_storage_provider


class EditorService:
    """
    Annotation/form operations are synchronous (unlike merge/compress/OCR/
    etc.) — they're near-instant single-page edits in an interactive
    editor, not multi-minute batch work, so wrapping them in the job/
    Celery pattern would add polling latency to the UI for no benefit.
    This mirrors the same reasoning already applied to AIService.

    Each successful edit creates a new File (not a new DocumentVersion of
    the same File) so the original stays untouched and every edit step is
    independently downloadable — matches how the rest of the app treats
    "any PDF operation produces a new file" (see merge/split/compress).
    """

    def __init__(self, db: Session):
        self.db = db
        self.files = FileRepository(db)
        self.storage = get_storage_provider()

    def _get_owned_file(self, owner_id: uuid.UUID, file_id: uuid.UUID) -> File:
        file = self.files.get_by_id(file_id)
        if file is None or file.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        return file

    def _save_new_version(self, owner_id: uuid.UUID, source: File, data: bytes, suffix: str) -> File:
        stem = source.original_filename.rsplit(".", 1)[0]
        filename = f"{stem}_{suffix}.pdf"
        key = self.storage.build_key(str(owner_id), filename)
        size = self.storage.save(key, io.BytesIO(data))
        return self.files.create(
            owner_id=owner_id, original_filename=filename,
            storage_key=key, mime_type="application/pdf", size_bytes=size,
        )

    def _run(self, owner_id, file_id, suffix, engine_fn, *args, **kwargs) -> File:
        source = self._get_owned_file(owner_id, file_id)
        try:
            data = engine_fn(self.storage.read(source.storage_key), *args, **kwargs)
        except PDFEngineError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
        return self._save_new_version(owner_id, source, data, suffix)

    def add_highlight(self, *, owner_id, file_id, page, x0, y0, x1, y1, color) -> File:
        return self._run(owner_id, file_id, "highlight", editor.add_highlight, page, x0, y0, x1, y1, color)

    def add_text_box(self, *, owner_id, file_id, page, x0, y0, x1, y1, text, font_size, color) -> File:
        return self._run(owner_id, file_id, "text", editor.add_text_box, page, x0, y0, x1, y1, text, font_size, color)

    def add_sticky_note(self, *, owner_id, file_id, page, x, y, note) -> File:
        return self._run(owner_id, file_id, "note", editor.add_sticky_note, page, x, y, note)

    def add_freehand_drawing(self, *, owner_id, file_id, page, strokes, color, width) -> File:
        return self._run(owner_id, file_id, "drawing", editor.add_freehand_drawing, page, strokes, color, width)

    def add_underline(self, *, owner_id, file_id, page, x0, y0, x1, y1, color) -> File:
        return self._run(owner_id, file_id, "underline", editor.add_underline, page, x0, y0, x1, y1, color)

    def add_strikethrough(self, *, owner_id, file_id, page, x0, y0, x1, y1, color) -> File:
        return self._run(owner_id, file_id, "strikethrough", editor.add_strikethrough, page, x0, y0, x1, y1, color)

    def add_whiteout(self, *, owner_id, file_id, page, x0, y0, x1, y1) -> File:
        return self._run(owner_id, file_id, "whiteout", editor.add_whiteout, page, x0, y0, x1, y1)

    def add_text_form_field(self, *, owner_id, file_id, page, x0, y0, x1, y1, field_name, default_value) -> File:
        return self._run(owner_id, file_id, "form", editor.add_text_form_field, page, x0, y0, x1, y1, field_name, default_value)

    def add_checkbox_form_field(self, *, owner_id, file_id, page, x0, y0, x1, y1, field_name, checked) -> File:
        return self._run(owner_id, file_id, "form", editor.add_checkbox_form_field, page, x0, y0, x1, y1, field_name, checked)

    def fill_form(self, *, owner_id, file_id, values) -> File:
        return self._run(owner_id, file_id, "filled", editor.fill_form_fields, values)

    def list_form_fields(self, *, owner_id, file_id) -> list[dict]:
        source = self._get_owned_file(owner_id, file_id)
        try:
            return editor.list_form_fields(self.storage.read(source.storage_key))
        except PDFEngineError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
