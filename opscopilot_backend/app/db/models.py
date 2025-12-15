# app/db/models.py
from __future__ import annotations

from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
    text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class JobStatus(str, PyEnum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # task_id Celery
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.queued,
        index=True,
    )
    rows_ok: Mapped[int] = mapped_column(Integer, default=0)
    rows_bad: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    finished_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # opcional


class Processed(Base):
    __tablename__ = "processed_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_file: Mapped[str] = mapped_column(String(255))
    item: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Usamos date_str (texto) como en el resto del proyecto
    date_str: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Hash de la línea para evitar duplicados
    line_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
        unique=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    finished_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # --- CAMPOS IA / REVISIÓN (Semana 10) ---
    nlp_overall_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    needs_review: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        index=True,
    )
    review_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )
    reviewed_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
