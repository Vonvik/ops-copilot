# app/schemas/processed.py
import re
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ProcessedBase(BaseModel):
    item: Optional[str] = None
    amount: Optional[float] = None
    date_str: Optional[str] = None
    source_file: Optional[str] = None

    # --- NUEVOS CAMPOS RELACIONADOS CON IA / REVISIÓN ---
    nlp_overall_confidence: Optional[float] = None
    needs_review: Optional[bool] = None
    review_status: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None


class ProcessedInDBBase(ProcessedBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True



class Processed(ProcessedInDBBase):
    pass


class ProcessedCreate(ProcessedBase):
    """Usa este si quieres crear Processed directamente desde API."""
    pass


class ProcessedUpdate(ProcessedBase):
    pass


class ProcessedOut(BaseModel):
    """
    Esquema de salida que usas en create_processed.
    Antes no incluía los campos de IA, ahora sí.
    """
    id: int
    source_file: str
    item: str
    amount: float
    date: date
    created_at: datetime

    # 🔹 añadimos los campos de IA/revisión también en la salida
    nlp_overall_confidence: Optional[float] = None
    needs_review: Optional[bool] = None
    review_status: Optional[str] = None

    model_config = {"from_attributes": True}


class ProcessedIn(BaseModel):
    """
    Entrada “cruda” para crear un Processed (por ejemplo, desde CSV o formulario).
    Es muy probable que en routes tengas algo como:

        from app.schemas.processed import ProcessedIn as CreateProcessed

    Así que aquí también añadimos nlp_overall_confidence.
    """
    source_file: str
    item: str
    amount: str | float
    date_str: str
    # 🔹 nuevo campo para que pueda llegar desde el body
    nlp_overall_confidence: Optional[float] = None

    @field_validator("item", mode="before")
    @classmethod
    def _trim_item(cls, v):
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("item vacío")
        return v

    @field_validator("amount", mode="before")
    @classmethod
    def _norm_amount(cls, v):
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        s = re.sub(r"[^\d,.\-]", "", s)  # quita símbolos
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            s = s.replace(",", ".")
        try:
            return float(s)
        except Exception as e:
            raise ValueError(f"amount inválido: {v}") from e
