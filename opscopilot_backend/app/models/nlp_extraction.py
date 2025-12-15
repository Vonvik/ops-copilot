from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class NLPExtraction(Base):
    __tablename__ = "nlp_extractions"

    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text, nullable=False)

    item = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    date_str = Column(String, nullable=True)

    item_conf = Column(Float, nullable=False, default=0.0)
    amount_conf = Column(Float, nullable=False, default=0.0)
    date_conf = Column(Float, nullable=False, default=0.0)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
