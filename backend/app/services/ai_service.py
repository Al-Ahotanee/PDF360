import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.file_repository import FileRepository
from app.services.ai.provider import AIProviderNotConfiguredError, get_ai_provider
from app.services.pdf_engine.conversion import pdf_to_txt
from app.services.storage.factory import get_storage_provider


class AIService:
    """
    Synchronous for now (no job/Celery wrapping) since these are single
    LLM calls, not multi-minute PDF processing — matches how a chat-style
    "ask questions about this PDF" feature is actually used (the user is
    waiting for the answer in the UI, not checking back later).
    """

    def __init__(self, db: Session):
        self.db = db
        self.files = FileRepository(db)
        self.storage = get_storage_provider()
        self.provider = get_ai_provider()

    def _get_text(self, owner_id: uuid.UUID, file_id: uuid.UUID) -> str:
        file = self.files.get_by_id(file_id)
        if file is None or file.owner_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
        try:
            return pdf_to_txt(self.storage.read(file.storage_key))
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Could not extract text: {exc}") from exc

    def _call(self, fn, *args):
        try:
            return fn(*args)
        except AIProviderNotConfiguredError as exc:
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc)) from exc

    def summarize(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> str:
        text = self._get_text(owner_id, file_id)
        return self._call(self.provider.summarize, text)

    def answer_question(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, question: str) -> str:
        text = self._get_text(owner_id, file_id)
        return self._call(self.provider.answer_question, text, question)

    def translate(self, *, owner_id: uuid.UUID, file_id: uuid.UUID, target_language: str) -> str:
        text = self._get_text(owner_id, file_id)
        return self._call(self.provider.translate, text, target_language)

    def extract_keywords(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> list[str]:
        text = self._get_text(owner_id, file_id)
        return self._call(self.provider.extract_keywords, text)

    def suggest_title(self, *, owner_id: uuid.UUID, file_id: uuid.UUID) -> str:
        text = self._get_text(owner_id, file_id)
        return self._call(self.provider.suggest_title, text)
