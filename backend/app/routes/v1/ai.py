from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import (
    AIFileRequest,
    AIKeywordsResponse,
    AIQuestionRequest,
    AITextResponse,
    AITranslateRequest,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Features"])


@router.post("/summarize", response_model=AITextResponse)
def summarize(data: AIFileRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return AITextResponse(result=AIService(db).summarize(owner_id=user.id, file_id=data.file_id))


@router.post("/ask", response_model=AITextResponse)
def ask(data: AIQuestionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return AITextResponse(result=AIService(db).answer_question(owner_id=user.id, file_id=data.file_id, question=data.question))


@router.post("/translate", response_model=AITextResponse)
def translate(data: AITranslateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return AITextResponse(result=AIService(db).translate(owner_id=user.id, file_id=data.file_id, target_language=data.target_language))


@router.post("/keywords", response_model=AIKeywordsResponse)
def keywords(data: AIFileRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return AIKeywordsResponse(keywords=AIService(db).extract_keywords(owner_id=user.id, file_id=data.file_id))


@router.post("/suggest-title", response_model=AITextResponse)
def suggest_title(data: AIFileRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return AITextResponse(result=AIService(db).suggest_title(owner_id=user.id, file_id=data.file_id))
