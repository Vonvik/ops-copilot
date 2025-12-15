from typing import Optional, Literal

from sqlalchemy.orm import Session

from app.models.nlp_rules import NLPConfidenceRule

ReviewAction = Literal["AUTO_ACCEPT", "REVIEW", "IGNORE_OR_SUGGEST"]


class ReviewDecision:
    """
    Resultado de aplicar las reglas de confianza NLP:
    - action: qué dice la regla que deberíamos hacer
    - needs_review: si debe ir a cola de revisión
    - review_status: estado inicial de revisión en BD
    """

    def __init__(
        self,
        action: Optional[ReviewAction],
        needs_review: bool,
        review_status: Optional[str],
    ) -> None:
        self.action = action
        self.needs_review = needs_review
        self.review_status = review_status


def _fallback_decision(overall_confidence: float) -> ReviewDecision:
    """
    Fallback por defecto si no hay reglas en BD.
    Usa los umbrales que definimos:

      < 0.4    → IGNORE_OR_SUGGEST   (needs_review = True, pending)
      0.4–0.8  → REVIEW              (needs_review = True, pending)
      ≥ 0.8    → AUTO_ACCEPT         (needs_review = False, approved)
    """
    if overall_confidence >= 0.8:
        return ReviewDecision(
            action="AUTO_ACCEPT",
            needs_review=False,
            review_status="approved",
        )
    elif overall_confidence >= 0.4:
        return ReviewDecision(
            action="REVIEW",
            needs_review=True,
            review_status="pending",
        )
    else:
        return ReviewDecision(
            action="IGNORE_OR_SUGGEST",
            needs_review=True,
            review_status="pending",
        )


def apply_nlp_rules(
    db: Session,
    overall_confidence: Optional[float],
) -> ReviewDecision:
    """
    Aplica las reglas de nlp_confidence_rules al valor de overall_confidence.

    Si no hay confianza o no hay reglas activas, devolvemos
    un resultado por defecto con _fallback_decision.
    """
    if overall_confidence is None:
        # No hay info de IA → no forzamos nada
        return ReviewDecision(action=None, needs_review=False, review_status=None)

    # Intentamos leer reglas desde BD
    rules = (
        db.query(NLPConfidenceRule)
        .filter(NLPConfidenceRule.is_active.is_(True))
        .order_by(NLPConfidenceRule.min_confidence.asc())
        .all()
    )

    # Si no hay reglas activas → usamos fallback en código
    if not rules:
        return _fallback_decision(overall_confidence)

    matched_rule: Optional[NLPConfidenceRule] = None

    for rule in rules:
        if rule.min_confidence <= overall_confidence < rule.max_confidence:
            matched_rule = rule
            break

    # Si ninguna regla ha coincidido, también usamos fallback
    if matched_rule is None:
        return _fallback_decision(overall_confidence)

    action = matched_rule.action

    if action == "AUTO_ACCEPT":
        # Confianza alta → aprobado directamente, sin revisión
        return ReviewDecision(
            action="AUTO_ACCEPT",
            needs_review=False,
            review_status="approved",
        )

    if action == "REVIEW":
        # Confianza media → va a cola de revisión
        return ReviewDecision(
            action="REVIEW",
            needs_review=True,
            review_status="pending",
        )

    if action == "IGNORE_OR_SUGGEST":
        # Confianza muy baja → lo trataremos como "sólo sugerencia"
        # pero a efectos de BD, lo marcamos como pendiente
        return ReviewDecision(
            action="IGNORE_OR_SUGGEST",
            needs_review=True,
            review_status="pending",
        )

    # Acción rara/no esperada
    return ReviewDecision(action=None, needs_review=False, review_status=None)
