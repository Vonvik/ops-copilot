from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NLPExtractionBase(BaseModel):
    raw_text: str
    item: Optional[str] = None
    amount: Optional[float] = None
    date_str: Optional[str] = None
    item_conf: float
    amount_conf: float
    date_conf: float


class NLPExtractionCreate(NLPExtractionBase):
    """Schema para crear una extracción desde el backend (no desde el cliente)."""
    pass


class NLPExtraction(NLPExtractionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # para que funcione con objetos SQLAlchemy
