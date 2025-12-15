# app/tasks/csv_tasks.py
from __future__ import annotations

from datetime import datetime

from app.celery_app import celery
from app.db.base import get_session
from app.db.models import Job, JobStatus, Processed
from app.services.csv_parser import parse_csv_bytes


@celery.task(
    bind=True,  # ← Celery inyecta self (Task)
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    name="app.tasks.csv_tasks.process_csv",  # ← nombre estable de la tarea
)
def process_csv(_self, task_id: str, filename: str, file_bytes: bytes) -> dict:
    """
    Procesa un CSV subido: normaliza, inserta en processed con idempotencia por line_hash
    y actualiza métricas en jobs.
    """
    session = get_session()
    rows_ok = 0
    rows_bad = 0
    try:
        # marca job running
        job = session.get(Job, task_id)
        if job:
            job.status = JobStatus.running
            session.commit()

        for rec in parse_csv_bytes(file_bytes, filename):
            try:
                # idempotencia por hash
                exists = session.query(Processed).filter_by(line_hash=rec["line_hash"]).first()
                if exists:
                    continue
                session.add(Processed(**rec))
                rows_ok += 1
                if rows_ok % 500 == 0:
                    session.commit()
            except Exception:
                rows_bad += 1
                session.rollback()

        session.commit()

        if job:
            job.status = JobStatus.done
            job.rows_ok = rows_ok
            job.rows_bad = rows_bad
            job.finished_at = datetime.utcnow()
            session.commit()

        return {"rows_ok": rows_ok, "rows_bad": rows_bad}
    except Exception as e:
        session.rollback()
        if (job := session.get(Job, task_id)) is not None:
            job.status = JobStatus.failed
            job.error = str(e)
            job.finished_at = datetime.utcnow()
            session.commit()
        raise
    finally:
        session.close()
