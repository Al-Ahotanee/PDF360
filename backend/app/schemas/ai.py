import uuid

from pydantic import BaseModel


class AIFileRequest(BaseModel):
    file_id: uuid.UUID


class AIQuestionRequest(BaseModel):
    file_id: uuid.UUID
    question: str


class AITranslateRequest(BaseModel):
    file_id: uuid.UUID
    target_language: str


class AITextResponse(BaseModel):
    result: str


class AIKeywordsResponse(BaseModel):
    keywords: list[str]
