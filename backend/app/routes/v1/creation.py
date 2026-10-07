from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.creation import (
    CreateBlankRequest,
    CreateCertificateRequest,
    CreateFromTextRequest,
    CreateInvoiceRequest,
    CreateReportRequest,
)
from app.schemas.pdf import FileOut
from app.services.creation_service import CreationService

router = APIRouter(prefix="/create", tags=["Creation"])


@router.post("/blank", response_model=FileOut, status_code=201)
def create_blank(data: CreateBlankRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CreationService(db).create_blank(owner_id=user.id, pages=data.pages, page_size=data.page_size)


@router.post("/from-text", response_model=FileOut, status_code=201)
def create_from_text(data: CreateFromTextRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CreationService(db).create_from_text(
        owner_id=user.id, text=data.text, page_size=data.page_size, font_size=data.font_size,
    )


@router.post("/invoice", response_model=FileOut, status_code=201)
def create_invoice(data: CreateInvoiceRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CreationService(db).create_invoice(owner_id=user.id, invoice_data=data.model_dump(by_alias=True))


@router.post("/certificate", response_model=FileOut, status_code=201)
def create_certificate(data: CreateCertificateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CreationService(db).create_certificate(owner_id=user.id, certificate_data=data.model_dump())


@router.post("/report", response_model=FileOut, status_code=201)
def create_report(data: CreateReportRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CreationService(db).create_report(owner_id=user.id, report_data=data.model_dump())
