# app/models/processed.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, text, Column, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

class ProcessedRow(Base):
    __tablename__ = "processed_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item: Mapped[str | None] = mapped_column(String(255), index=True)
    amount: Mapped[float | None] = mapped_column(Float)
    date_str: Mapped[str | None] = mapped_column(String(50))
    source_file: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    # Confianza global de la extracción NLP para este registro
    nlp_overall_confidence = Column(Float, nullable=True)

    # ¿Este registro necesita revisión manual?
    needs_review = Column(Boolean, nullable=False, server_default="false", index=True)

    # Estado de revisión: 'pending', 'approved', 'rejected'...
    review_status = Column(String(length=20), nullable=True, index=True)

    # Usuario revisor (FK a users.id), opcional
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Cuándo se revisó
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relación opcional al usuario revisor
    reviewer = relationship("User", foreign_keys=[reviewed_by_id])
    