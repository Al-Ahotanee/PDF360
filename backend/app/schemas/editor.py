import uuid

from pydantic import BaseModel


class HighlightRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    color: str | None = None


class TextBoxRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    font_size: float = 12
    color: str | None = None


class StickyNoteRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x: float
    y: float
    note: str


class FreehandRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    strokes: list[list[tuple[float, float]]]
    color: str | None = None
    width: float = 2.0


class TextFormFieldRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    field_name: str
    default_value: str = ""


class CheckboxFormFieldRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    field_name: str
    checked: bool = False


class FillFormRequest(BaseModel):
    file_id: uuid.UUID
    values: dict[str, str | bool]


class FormFieldOut(BaseModel):
    page: int
    field_name: str
    field_type: str
    field_value: str | bool | None


class UnderlineRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    color: str | None = None


class StrikethroughRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    color: str | None = None


class WhiteoutRequest(BaseModel):
    file_id: uuid.UUID
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
