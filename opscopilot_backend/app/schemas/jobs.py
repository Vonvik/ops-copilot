# app/schemas/jobs.py
from datetime import datetime

from pydantic import BaseModel

from app.db.models import JobStatus


class JobOut(BaseModel):
    id: str
    filename: str | None
    status: JobStatus
    rows_ok: int
    rows_bad: int
    error: str | None
    created_at: datetime
    finished_at: datetime | None
    model_config = {"from_attributes": True}
