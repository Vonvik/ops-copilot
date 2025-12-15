from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base  # o el Base que uses en tus modelos


class NLPConfidenceRule(Base):
    __tablename__ = "nlp_confidence_rules"

    id = Column(Integer, primary_key=True, index=True)

    # Rango de confianza al que aplica esta regla
    min_confidence = Column(Float, nullable=False)
    max_confidence = Column(Float, nullable=False)

    # Acción que se tomará, por ejemplo:
    # - "AUTO_ACCEPT"
    # - "REVIEW"
    # - "IGNORE_OR_SUGGEST"
    action = Column(String(length=50), nullable=False)

    # Por si en el futuro tienes varias configuraciones y quieres activar/desactivar
    is_active = Column(Boolean, nullable=False, server_default="true")
