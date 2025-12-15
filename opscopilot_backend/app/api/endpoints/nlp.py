# app/api/endpoints/nlp.py
from __future__ import annotations

from typing import List, Literal, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.nlp import NLPExtractRequest, NLPExtractResponse
from app.services.nlp import extract_fields_from_text
from app.models.nlp_extraction import NLPExtraction
from app.schemas.nlp_extraction import NLPExtraction as NLPExtractionSchema
from app.models.nlp_rules import NLPConfidenceRule  # 🔹 modelo de reglas

from fastapi import HTTPException, status
from pydantic import BaseModel

# ⛔️ IMPORTANTE: SIN prefix aquí
router = APIRouter()

# ============================================================
#  NLP EXTRACT + HISTÓRICO
# ============================================================

@router.post("/extract", response_model=NLPExtractResponse)
def extract_nlp(
    payload: NLPExtractRequest,
    db: Session = Depends(deps.get_db),
) -> NLPExtractResponse:
    """
    Endpoint que recibe un texto libre, extrae campos con la lógica de NLP
    y guarda el resultado en la base de datos junto con las puntuaciones
    de confianza.
    De momento NO requiere autenticación.
    """
    # 1) Ejecutamos la lógica de extracción (spaCy + reglas)
    result_dict = extract_fields_from_text(payload.text)
    # result_dict:
    # {
    #   "item": ...,
    #   "amount": ...,
    #   "date_str": ...,
    #   "confidences": {"item": 0.7, "amount": 0.9, "date_str": 0.9},
    #   "language": "es",
    #   "raw_text": "...",
    # }

    conf = result_dict.get("confidences", {}) or {}

    item_conf = float(conf.get("item") or 0.0)
    amount_conf = float(conf.get("amount") or 0.0)
    date_conf = float(conf.get("date_str") or 0.0)

    # 2) Creamos el objeto SQLAlchemy para guardar en BD
    db_obj = NLPExtraction(
        raw_text=result_dict.get("raw_text", payload.text),
        item=result_dict.get("item"),
        amount=result_dict.get("amount"),
        date_str=result_dict.get("date_str"),
        item_conf=item_conf,
        amount_conf=amount_conf,
        date_conf=date_conf,
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # 3) Calculamos confianza global y si requiere revisión
    vals = [item_conf, amount_conf, date_conf]
    non_zero = [v for v in vals if v > 0]
    overall_confidence = sum(non_zero) / len(non_zero) if non_zero else 0.0
    needs_review = overall_confidence < 0.8

    # 4) Devolvemos respuesta alineada con el schema NLPExtractResponse
    return NLPExtractResponse(
        # campos "core" de la extracción
        item=result_dict.get("item"),
        amount=result_dict.get("amount"),
        date_str=result_dict.get("date_str"),

        # si tu schema tiene también 'concept', lo rellenamos con lo mismo
        concept=result_dict.get("item"),

        # campos que Pydantic marca como required en el error
        confidences=conf,
        language=result_dict.get("language") or "es",
        raw_text=result_dict.get("raw_text") or payload.text,

        # campos de control de calidad / revisión
        overall_confidence=overall_confidence,
        needs_review=needs_review,
        review_status="pending",
    )



@router.get("/extractions", response_model=List[NLPExtractionSchema])
def list_nlp_extractions(
    db: Session = Depends(deps.get_db),
    limit: int = 50,
    min_conf: Optional[float] = None,
) -> List[NLPExtractionSchema]:
    """
    Devuelve las últimas extracciones NLP guardadas en la base de datos.
    De momento NO requiere autenticación.
    Si se pasa min_conf, solo devuelve las que tengan una confianza media
    (item_conf, amount_conf, date_conf) mayor o igual a ese valor.
    """
    q = (
        db.query(NLPExtraction)
        .order_by(NLPExtraction.created_at.desc())
        .limit(limit)
    )
    results = q.all()

    if min_conf is None:
        return results

    filtered: list[NLPExtraction] = []
    for r in results:
        vals = [r.item_conf, r.amount_conf, r.date_conf]
        non_zero = [v for v in vals if v > 0]
        if not non_zero:
            avg_conf = 0.0
        else:
            avg_conf = sum(non_zero) / len(non_zero)

        if avg_conf >= min_conf:
            filtered.append(r)

    return filtered

# ============================================================
#  CONFIGURACIÓN DE REGLAS DE CONFIANZA (Opción C, sin description)
# ============================================================

RuleAction = Literal["AUTO_ACCEPT", "REVIEW", "IGNORE_OR_SUGGEST"]


class NLPRuleBase(BaseModel):
    min_confidence: float
    max_confidence: float
    action: RuleAction
    is_active: bool = True


class NLPRuleCreate(NLPRuleBase):
    pass


class NLPRuleUpdate(BaseModel):
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    action: Optional[RuleAction] = None
    is_active: Optional[bool] = None


class NLPRuleOut(NLPRuleBase):
    id: int

    class Config:
        from_attributes = True



def _validate_range(min_conf: float, max_conf: float) -> None:
    if not (0.0 <= min_conf <= 1.0 and 0.0 <= max_conf <= 1.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_confidence y max_confidence deben estar entre 0.0 y 1.0",
        )
    if min_conf >= max_conf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_confidence debe ser menor que max_confidence",
        )


@router.get("/rules", response_model=List[NLPRuleOut])
def list_rules(
    db: Session = Depends(deps.get_db),
    only_active: bool = False,
) -> List[NLPRuleOut]:
    """
    Lista las reglas de confianza NLP.

    - if only_active = True → solo reglas activas (is_active = True)
    - si no → todas
    """
    q = db.query(NLPConfidenceRule)
    if only_active:
        q = q.filter(NLPConfidenceRule.is_active.is_(True))
    rules = q.order_by(NLPConfidenceRule.min_confidence.asc()).all()
    return rules


@router.post(
    "/rules",
    response_model=NLPRuleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(
    payload: NLPRuleCreate,
    db: Session = Depends(deps.get_db),
) -> NLPRuleOut:
    """Crea una nueva regla de confianza NLP."""
    _validate_range(payload.min_confidence, payload.max_confidence)

    db_rule = NLPConfidenceRule(
        min_confidence=payload.min_confidence,
        max_confidence=payload.max_confidence,
        action=payload.action,
        is_active=payload.is_active,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/rules/{rule_id}", response_model=NLPRuleOut)
def update_rule(
    rule_id: int,
    payload: NLPRuleUpdate,
    db: Session = Depends(deps.get_db),
) -> NLPRuleOut:
    """Actualiza una regla existente."""
    rule = db.query(NLPConfidenceRule).filter(NLPConfidenceRule.id == rule_id).first()
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regla id={rule_id} no encontrada",
        )

    # Calculamos los nuevos valores (o reutilizamos los actuales)
    new_min = payload.min_confidence if payload.min_confidence is not None else rule.min_confidence
    new_max = payload.max_confidence if payload.max_confidence is not None else rule.max_confidence

    _validate_range(new_min, new_max)

    rule.min_confidence = new_min
    rule.max_confidence = new_max

    if payload.action is not None:
        rule.action = payload.action
    if payload.is_active is not None:
        rule.is_active = payload.is_active

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    rule_id: int,
    db: Session = Depends(deps.get_db),
) -> None:
    """Elimina una regla (borrado duro)."""
    rule = db.query(NLPConfidenceRule).filter(NLPConfidenceRule.id == rule_id).first()
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Regla id={rule_id} no encontrada",
        )

    db.delete(rule)
    db.commit()
    return None
