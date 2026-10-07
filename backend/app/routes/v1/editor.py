import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.editor import (
    CheckboxFormFieldRequest,
    FillFormRequest,
    FormFieldOut,
    FreehandRequest,
    HighlightRequest,
    StrikethroughRequest,
    UnderlineRequest,
    WhiteoutRequest,
    StickyNoteRequest,
    TextBoxRequest,
    TextFormFieldRequest,
)
from app.schemas.pdf import FileOut
from app.services.editor_service import EditorService

router = APIRouter(prefix="/editor", tags=["Editor"])


@router.post("/highlight", response_model=FileOut, status_code=201)
def add_highlight(data: HighlightRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_highlight(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1, color=data.color,
    )


@router.post("/text-box", response_model=FileOut, status_code=201)
def add_text_box(data: TextBoxRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_text_box(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1,
        text=data.text, font_size=data.font_size, color=data.color,
    )


@router.post("/sticky-note", response_model=FileOut, status_code=201)
def add_sticky_note(data: StickyNoteRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_sticky_note(
        owner_id=user.id, file_id=data.file_id, page=data.page, x=data.x, y=data.y, note=data.note,
    )


@router.post("/freehand", response_model=FileOut, status_code=201)
def add_freehand(data: FreehandRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_freehand_drawing(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        strokes=data.strokes, color=data.color, width=data.width,
    )


@router.post("/form-fields/text", response_model=FileOut, status_code=201)
def add_text_form_field(data: TextFormFieldRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_text_form_field(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1,
        field_name=data.field_name, default_value=data.default_value,
    )


@router.post("/form-fields/checkbox", response_model=FileOut, status_code=201)
def add_checkbox_form_field(data: CheckboxFormFieldRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_checkbox_form_field(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1,
        field_name=data.field_name, checked=data.checked,
    )


@router.post("/form-fields/fill", response_model=FileOut, status_code=201)
def fill_form(data: FillFormRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).fill_form(owner_id=user.id, file_id=data.file_id, values=data.values)


@router.get("/form-fields/{file_id}", response_model=list[FormFieldOut])
def list_form_fields(file_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).list_form_fields(owner_id=user.id, file_id=file_id)


@router.post("/underline", response_model=FileOut, status_code=201)
def add_underline(data: UnderlineRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_underline(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1, color=data.color,
    )


@router.post("/strikethrough", response_model=FileOut, status_code=201)
def add_strikethrough(data: StrikethroughRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_strikethrough(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1, color=data.color,
    )


@router.post("/whiteout", response_model=FileOut, status_code=201)
def add_whiteout(data: WhiteoutRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return EditorService(db).add_whiteout(
        owner_id=user.id, file_id=data.file_id, page=data.page,
        x0=data.x0, y0=data.y0, x1=data.x1, y1=data.y1,
    )
