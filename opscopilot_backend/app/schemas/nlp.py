from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel


class NLPExtractRequest(BaseModel):
    text: str


class NLPExtractResponse(BaseModel):
    item: Optional[str]
    amount: Optional[float]
    date_str: Optional[str]
    confidences: Dict[str, float]
    overall_confidence: float  # 👈 nuevo campo
    language: str
    raw_text: str
