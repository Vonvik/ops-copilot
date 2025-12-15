# app/routes/processed.py
from __future__ import annotations

from hashlib import sha256
from typing import Literal, List, Optional
from datetime import datetime, timezone, date
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.nlp_rules import apply_nlp_rules
from app.db.base import get_db
from app.db.models import Processed as ProcessedModel

router = APIRouter(tags=["processed"])


# --------- Schemas de I/O ---------
class CreateProcessed(BaseModel):
  item: Optional[str] = None
  amount: Optional[float] = None
  date_str: Optional[str] = None  # en API siempre devolvemos 'date_str'
  source_file: Optional[str] = None
  # 🔹 NUEVO: confianza global del NLP (puede venir o no)
  nlp_overall_confidence: Optional[float] = None


class ProcessedOut(CreateProcessed):
  id: int
  created_at: str  # ISO
  # 🔹 NUEVO: que el cliente pueda ver cómo ha quedado
  needs_review: Optional[bool] = None
  review_status: Optional[str] = None


class ProcessedPage(BaseModel):
  items: List[ProcessedOut]
  total: int
  page: int
  page_size: int
  sort_by: Optional[
    Literal["id", "amount", "date", "created_at", "source_file", "item"]
  ] = None
  sort_dir: Optional[Literal["asc", "desc"]] = None


# --------- Helpers ---------
def _to_datestr(v) -> Optional[str]:
  """Devuelve str ISO si v es date/datetime, o str(v) si no es str. None si no hay valor."""
  if v is None:
    return None
  if isinstance(v, (datetime, date)):
    return v.isoformat()
  if isinstance(v, str):
    return v
  return str(v)


def _read_date_field(row: ProcessedModel) -> Optional[str]:
  """Lee 'date_str' o, si no existe, 'date', y lo devuelve como string."""
  v = getattr(row, "date_str", None)
  if v is None:
    v = getattr(row, "date", None)
  return _to_datestr(v)


def _coerce_date_input(s: Optional[str]):
  """
  Convierte el string ISO 'YYYY-MM-DD' a datetime.date si el modelo usa columna 'date'.
  Si no es parseable, devuelve el valor original (podría ser None).
  """
  if s is None:
    return None
  try:
    return date.fromisoformat(s)
  except Exception:
    return s


def _coerce_amount(v) -> Optional[float]:
  if v is None:
    return None
  if isinstance(v, Decimal):
    return float(v)
  return v  # ya es float


def _created_iso(row: ProcessedModel) -> str:
  ca = getattr(row, "created_at", None)
  return ca.isoformat() if ca is not None else datetime.now(timezone.utc).isoformat()


def _make_line_hash(
  item: Optional[str],
  amount: Optional[float],
  date_iso: Optional[str],
  source_file: Optional[str],
) -> str:
  """
  Hash determinista de los campos “clave” para deduplicar.
  Ajusta los campos si en tu pipeline usas otros.
  """
  raw = (
    f"{(item or '').strip()}|"
    f"{'' if amount is None else amount}|"
    f"{(date_iso or '').strip()}|"
    f"{(source_file or '').strip()}"
  )
  return sha256(raw.encode("utf-8")).hexdigest()


# --------- GET /api/v1/processed ---------
@router.get("/processed", response_model=List[ProcessedOut], name="list_processed")
def list_processed(limit: int = 50, db: Session = Depends(get_db)):
  try:
    rows = (
      db.query(ProcessedModel)
      .order_by(ProcessedModel.id.desc())
      .limit(limit)
      .all()
    )
    out: List[ProcessedOut] = []
    for r in rows:
      out.append(
        ProcessedOut(
          id=r.id,
          item=getattr(r, "item", None),
          amount=_coerce_amount(getattr(r, "amount", None)),
          date_str=_read_date_field(r),  # <- SIEMPRE devolvemos 'date_str'
          source_file=getattr(r, "source_file", None),
          created_at=_created_iso(r),
          nlp_overall_confidence=getattr(r, "nlp_overall_confidence", None),
          needs_review=getattr(r, "needs_review", None),
          review_status=getattr(r, "review_status", None),
        )
      )
    return out
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"processed.list: {e.__class__.__name__}: {e}",
    )


# --------- POST /api/v1/processed ---------
@router.post(
  "/processed",
  response_model=ProcessedOut,
  status_code=status.HTTP_201_CREATED,
  name="create_processed",
)
def create_processed(
  payload: CreateProcessed,
  db: Session = Depends(get_db),
):
  # Volcamos todo el payload a dict para evitar sorpresas con Pydantic
  data = payload.model_dump()

  # 1) Confianza global que pueda venir del NLP
  overall_confidence = data.get("nlp_overall_confidence")

  # 2) Calculamos decisión de reglas (si hay confianza)
  needs_review: bool = False
  review_status: Optional[str] = None

  if overall_confidence is not None:
    decision = apply_nlp_rules(db, overall_confidence)
    needs_review = decision.needs_review
    review_status = decision.review_status

  # Fecha: si tu modelo usa columna 'date' (date), convertimos desde string ISO
  date_str = data.get("date_str")
  if hasattr(ProcessedModel, "date"):
    date_for_model = _coerce_date_input(date_str)
  else:
    date_for_model = None

  # Fecha en string ISO para el hash (si viene None, quedará "")
  date_for_hash = date_str

  # Construimos kwargs compatibles con el modelo real
  kwargs = dict(
    item=data.get("item"),
    amount=data.get("amount"),
    source_file=data.get("source_file"),
    created_at=datetime.now(timezone.utc),
    # IA / revisión
    nlp_overall_confidence=overall_confidence,
    needs_review=needs_review,
    review_status=review_status,
  )

  # El modelo puede tener 'date_str' (texto) o 'date' (date)
  if hasattr(ProcessedModel, "date_str"):
    kwargs["date_str"] = date_str
  elif hasattr(ProcessedModel, "date") and date_for_model is not None:
    kwargs["date"] = date_for_model

  # 🔑 line_hash obligatorio (NOT NULL)
  computed_hash = None
  if hasattr(ProcessedModel, "line_hash"):
    computed_hash = _make_line_hash(
      data.get("item"),
      data.get("amount"),
      date_for_hash,
      data.get("source_file"),
    )
    kwargs["line_hash"] = computed_hash

  # Crear y persistir
  row = ProcessedModel(**kwargs)  # type: ignore[arg-type]
  try:
    db.add(row)
    db.commit()
    db.refresh(row)
  except IntegrityError as e:
    db.rollback()
    # Intenta detectar el nombre de la restricción que falló (Postgres)
    constraint = getattr(getattr(e, "orig", None), "diag", None)
    constraint_name = getattr(constraint, "constraint_name", None)
    msg = f"IntegrityError (constraint={constraint_name or 'unknown'})"

    # Si sabemos que es el índice/constraint de line_hash → 409
    if constraint_name and "line_hash" in constraint_name:
      raise HTTPException(
        status_code=409,
        detail=f"Registro duplicado (line_hash). hash={computed_hash}",
      )
    # Si no sabemos, pero tienes columna line_hash y te interesa debug, también 409
    if computed_hash is not None and "line_hash" in (
      str(e.orig) if getattr(e, "orig", None) else ""
    ):
      raise HTTPException(
        status_code=409,
        detail=f"Registro duplicado (line_hash). hash={computed_hash}",
      )

    # Cualquier otro caso: 400 con detalle
    raise HTTPException(status_code=400, detail=msg)

  return ProcessedOut(
    id=row.id,
    item=getattr(row, "item", None),
    amount=_coerce_amount(getattr(row, "amount", None)),
    date_str=_read_date_field(row),  # <- normalizado
    source_file=getattr(row, "source_file", None),
    created_at=_created_iso(row),
    nlp_overall_confidence=getattr(row, "nlp_overall_confidence", None),
    needs_review=getattr(row, "needs_review", None),
    review_status=getattr(row, "review_status", None),
  )


@router.get("/processed/page", response_model=ProcessedPage, name="list_processed_page")
def list_processed_page(
  page: int = 1,
  page_size: int = 10,
  sort_by: Optional[str] = None,
  sort_dir: Optional[str] = "desc",
  db: Session = Depends(get_db),
):
  q = db.query(ProcessedModel)

  # total
  total = q.count()

  # sort
  valid_cols = {
    "id": ProcessedModel.id,
    "amount": ProcessedModel.amount,
    "date": getattr(ProcessedModel, "date", None)
    or getattr(ProcessedModel, "date_str", None),
    "created_at": ProcessedModel.created_at,
    "source_file": ProcessedModel.source_file,
    "item": ProcessedModel.item,
  }
  col = valid_cols.get(sort_by or "id", ProcessedModel.id)
  if sort_dir == "asc":
    q = q.order_by(col.asc())
  else:
    q = q.order_by(col.desc())

  # page
  page = max(1, page)
  page_size = max(1, min(page_size, 100))
  rows = q.offset((page - 1) * page_size).limit(page_size).all()

  items: List[ProcessedOut] = []
  for r in rows:
    items.append(
      ProcessedOut(
        id=r.id,
        item=getattr(r, "item", None),
        amount=_coerce_amount(getattr(r, "amount", None)),
        date_str=_read_date_field(r),
        source_file=getattr(r, "source_file", None),
        created_at=_created_iso(r),
        nlp_overall_confidence=getattr(r, "nlp_overall_confidence", None),
        needs_review=getattr(r, "needs_review", None),
        review_status=getattr(r, "review_status", None),
      )
    )

  return ProcessedPage(
    items=items,
    total=total,
    page=page,
    page_size=page_size,
    sort_by=sort_by,
    sort_dir=sort_dir,
  )


# --------- GET /api/v1/processed/pending ---------
@router.get(
  "/processed/pending",
  response_model=List[ProcessedOut],
  name="list_pending_processed",
)
def list_pending_processed(
  limit: int = 50,
  db: Session = Depends(get_db),
):
  """
  Lista los registros que necesitan revisión y están en estado 'pending'.
  Esto es lo que usaremos como cola de revisión manual.
  """
  try:
    q = (
      db.query(ProcessedModel)
      .filter(
        ProcessedModel.needs_review.is_(True),
        ProcessedModel.review_status == "pending",
      )
      .order_by(ProcessedModel.id.desc())
      .limit(limit)
    )

    rows = q.all()
    out: List[ProcessedOut] = []
    for r in rows:
      out.append(
        ProcessedOut(
          id=r.id,
          item=getattr(r, "item", None),
          amount=_coerce_amount(getattr(r, "amount", None)),
          date_str=_read_date_field(r),
          source_file=getattr(r, "source_file", None),
          created_at=_created_iso(r),
          nlp_overall_confidence=getattr(r, "nlp_overall_confidence", None),
          needs_review=getattr(r, "needs_review", None),
          review_status=getattr(r, "review_status", None),
        )
      )
    return out
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"processed.pending: {e.__class__.__name__}: {e}",
    )


# --------- POST /api/v1/processed/{id}/approve ---------
@router.post(
  "/processed/{processed_id}/approve",
  response_model=ProcessedOut,
  name="approve_processed",
)
def approve_processed(
  processed_id: int,
  db: Session = Depends(get_db),
):
  """
  Marca un registro como aprobado (ya revisado).
  """
  row = (
    db.query(ProcessedModel)
    .filter(ProcessedModel.id == processed_id)
    .first()
  )
  if row is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Processed id={processed_id} no encontrado",
    )

  # Actualizamos flags de revisión
  row.needs_review = False
  row.review_status = "approved"
  if hasattr(row, "reviewed_at"):
    row.reviewed_at = datetime.now(timezone.utc)

  db.add(row)
  db.commit()
  db.refresh(row)

  return ProcessedOut(
    id=row.id,
    item=getattr(row, "item", None),
    amount=_coerce_amount(getattr(row, "amount", None)),
    date_str=_read_date_field(row),
    source_file=getattr(row, "source_file", None),
    created_at=_created_iso(row),
    nlp_overall_confidence=getattr(row, "nlp_overall_confidence", None),
    needs_review=getattr(row, "needs_review", None),
    review_status=getattr(row, "review_status", None),
  )


# --------- POST /api/v1/processed/{id}/reject ---------
@router.post(
  "/processed/{processed_id}/reject",
  response_model=ProcessedOut,
  name="reject_processed",
)
def reject_processed(
  processed_id: int,
  db: Session = Depends(get_db),
):
  """
  Marca un registro como rechazado.
  (Luego tú decidirás si lo borras, lo corriges, etc.)
  """
  row = (
    db.query(ProcessedModel)
    .filter(ProcessedModel.id == processed_id)
    .first()
  )
  if row is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Processed id={processed_id} no encontrado",
    )

  row.needs_review = False   # ya no está pendiente; ya se ha revisado (rechazada)
  row.review_status = "rejected"
  if hasattr(row, "reviewed_at"):
    row.reviewed_at = datetime.now(timezone.utc)

  db.add(row)
  db.commit()
  db.refresh(row)

  return ProcessedOut(
    id=row.id,
    item=getattr(row, "item", None),
    amount=_coerce_amount(getattr(row, "amount", None)),
    date_str=_read_date_field(row),
    source_file=getattr(row, "source_file", None),
    created_at=_created_iso(row),
    nlp_overall_confidence=getattr(row, "nlp_overall_confidence", None),
    needs_review=getattr(row, "needs_review", None),
    review_status=getattr(row, "review_status", None),
  )
class ProcessedStats(BaseModel):
    total_count: int
    ia_count: int
    pending_review: int
    approved_count: int
    rejected_count: int
    avg_confidence: float | None


@router.get("/processed/stats", response_model=ProcessedStats)
def get_processed_stats(db: Session = Depends(get_db)) -> ProcessedStats:
    """
    Estadísticas globales de los gastos y del motor IA.
    """
    try:
        total = db.query(ProcessedModel).count()

        ia_count = (
            db.query(ProcessedModel)
            .filter(ProcessedModel.nlp_overall_confidence.isnot(None))
            .count()
        )

        pending_review = (
            db.query(ProcessedModel)
            .filter(
                ProcessedModel.needs_review.is_(True),
                ProcessedModel.review_status == "pending",
            )
            .count()
        )

        approved_count = (
            db.query(ProcessedModel)
            .filter(ProcessedModel.review_status == "approved")
            .count()
        )

        rejected_count = (
            db.query(ProcessedModel)
            .filter(ProcessedModel.review_status == "rejected")
            .count()
        )

        avg_conf = (
            db.query(func.avg(ProcessedModel.nlp_overall_confidence))
            .scalar()
        )

        return ProcessedStats(
            total_count=total,
            ia_count=ia_count,
            pending_review=pending_review,
            approved_count=approved_count,
            rejected_count=rejected_count,
            avg_confidence=float(avg_conf) if avg_conf is not None else None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"processed.stats: {e.__class__.__name__}: {e}",
        )

