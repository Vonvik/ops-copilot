"""
Script sencillo para poblar la tabla nlp_confidence_rules
con unas reglas por defecto.

Uso:
  uvicorn parado, activa el .venv y ejecuta:

  cd OpsCopilot_backend
  python -m scripts.seed_nlp_rules
"""

from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.nlp_rules import NLPConfidenceRule


DEFAULT_RULES = [
    # Confianza baja: solo sugerir / revisar mucho
    {
        "min_confidence": 0.0,
        "max_confidence": 0.4,
        "action": "IGNORE_OR_SUGGEST",
    },
    # Confianza media: mandar a revisión humana
    {
        "min_confidence": 0.4,
        "max_confidence": 0.8,
        "action": "REVIEW",
    },
    # Confianza alta: aceptar automáticamente
    {
        "min_confidence": 0.8,
        "max_confidence": 1.01,  # por si llega 1.0 exacto
        "action": "AUTO_ACCEPT",
    },
]


def main() -> None:
    db: Session = SessionLocal()
    try:
        existing = db.query(NLPConfidenceRule).count()
        if existing > 0:
            print("Ya hay reglas en nlp_confidence_rules; no se hace nada.")
            return

        for rule_data in DEFAULT_RULES:
            rule = NLPConfidenceRule(
                min_confidence=rule_data["min_confidence"],
                max_confidence=rule_data["max_confidence"],
                action=rule_data["action"],
                is_active=True,
            )
            db.add(rule)

        db.commit()
        print("Reglas de NLP creadas correctamente.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
