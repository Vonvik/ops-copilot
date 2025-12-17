from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, Optional

import spacy
from spacy.language import Language

logger = logging.getLogger(__name__)

_MODEL_NAME = os.getenv("SPACY_ES_MODEL", "es_core_news_md")
_nlp_es: Optional[Language] = None


def get_nlp_es() -> Language:
    """
    Carga el modelo UNA sola vez (lazy).
    Si no está disponible, hace fallback a spacy.blank("es") para que la API no caiga.
    """
    global _nlp_es
    if _nlp_es is not None:
        return _nlp_es

    try:
        _nlp_es = spacy.load(_MODEL_NAME)
        logger.info("spaCy model loaded: %s", _MODEL_NAME)
    except Exception:
        logger.exception(
            "Failed to load spaCy model '%s'. Falling back to spacy.blank('es').",
            _MODEL_NAME,
        )
        _nlp_es = spacy.blank("es")

    return _nlp_es


_AMOUNT_PATTERN = re.compile(
    r"(\d+[.,]\d{1,2})\s*€?|\b(\d+)\s*€",
    re.UNICODE,
)

_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
    re.UNICODE,
)


def _normalize_amount(raw: str) -> Optional[float]:
    if not raw:
        return None

    raw = raw.strip()

    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(",", ".")

    try:
        return float(raw)
    except ValueError:
        return None


def extract_fields_from_text(text: str) -> Dict[str, Any]:
    nlp = get_nlp_es()
    doc = nlp(text)

    amount: Optional[float] = None
    amount_conf = 0.0
    date_str: Optional[str] = None
    date_conf = 0.0

    amount_match = _AMOUNT_PATTERN.search(text)
    if amount_match:
        raw_amount = amount_match.group(1) or amount_match.group(2)
        amount = _normalize_amount(raw_amount)
        if amount is not None:
            amount_conf = 0.9

    date_match = _DATE_PATTERN.search(text)
    if date_match:
        date_str = date_match.group(1)
        date_conf = 0.9

    item_candidate = text
    if amount_match:
        item_candidate = item_candidate.replace(amount_match.group(0), "")
    if date_match:
        item_candidate = item_candidate.replace(date_match.group(0), "")

    item_candidate = item_candidate.strip(" -–,;:·\t\n")

    if item_candidate:
        item = item_candidate
        item_conf = 0.7
    else:
        item = None
        item_conf = 0.0

    confidences = {"item": item_conf, "amount": amount_conf, "date_str": date_conf}

    non_zero_values = [v for v in confidences.values() if v > 0]
    overall_confidence = sum(non_zero_values) / len(non_zero_values) if non_zero_values else 0.0

    return {
        "item": item,
        "amount": amount,
        "date_str": date_str,
        "confidences": confidences,
        "overall_confidence": overall_confidence,
        "language": getattr(doc, "lang_", "es"),
        "raw_text": text,
    }
