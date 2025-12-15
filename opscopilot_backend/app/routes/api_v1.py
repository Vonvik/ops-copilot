# app/routes/api_v1.py
import logging
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from app.api.endpoints import nlp
from app.db.base import get_session
from app.db.models import Job, JobStatus
from app.routes.auth_routes import router as auth_router
from app.routes.processed import router as processed_router
from app.schemas.jobs import JobOut
from app.tasks.csv_tasks import process_csv as process_csv_task

logger = logging.getLogger(__name__)

router = APIRouter()

# ✅ monta routers “hijos”
router.include_router(auth_router)       # /api/v1/auth/...
router.include_router(processed_router)  # /api/v1/processed (GET y POST)
router.include_router(nlp.router, prefix="/nlp", tags=["nlp"])  # /api/v1/nlp/...


@router.post("/upload-csv", status_code=status.HTTP_202_ACCEPTED)
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Sólo se aceptan archivos CSV")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande (máx 10MB)")

    task_id = uuid.uuid4().hex

    session = get_session()
    try:
        job = Job(id=task_id, filename=file.filename, status=JobStatus.queued)
        session.add(job)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception("DB error creating job")
        err_name = e.__class__.__name__
        detail = getattr(e, "orig", None)
        raise HTTPException(status_code=500, detail=f"Error creando job: {err_name} {detail}") from e
    finally:
        session.close()

    process_csv_task.delay(task_id, file.filename, content)
    return {"task_id": task_id}


@router.get("/tasks/{task_id}", response_model=JobOut)
def get_task(task_id: str):
    session = get_session()
    try:
        job = session.get(Job, task_id)
        if not job:
            raise HTTPException(status_code=404, detail="Task no encontrada")
        return job
    finally:
        session.close()
