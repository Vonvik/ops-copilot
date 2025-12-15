from __future__ import annotations

import re
from typing import Any, Dict, Optional

import spacy

# Cargamos el modelo de spaCy en español UNA sola vez al importar el módulo.
# Esto es mejor que cargarlo en cada petición.
nlp_es = spacy.load("es_core_news_md")

# Expresión regular para encontrar importes tipo "23,45 €", "23.45€", "23 €", etc.
_AMOUNT_PATTERN = re.compile(
    r"(\d+[.,]\d{1,2})\s*€?|\b(\d+)\s*€",
    re.UNICODE,
)

# Expresión regular simple para fechas tipo "12/10/2025" o "12-10-25"
_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
    re.UNICODE,
)


def _normalize_amount(raw: str) -> Optional[float]:
    """
    Normaliza un importe en formato europeo/español (coma o punto) a float.
    Ejemplos:
      "23,45" -> 23.45
      "23.45" -> 23.45
      "1.234,56" -> 1234.56 (approx)
    """
    if not raw:
        return None

    # Quitamos espacios
    raw = raw.strip()

    # Caso clásico europeo "1.234,56" -> "1234.56"
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        # Sólo coma -> reemplazamos por punto
        raw = raw.replace(",", ".")

    try:
        return float(raw)
    except ValueError:
        return None


def extract_fields_from_text(text: str) -> Dict[str, Any]:
    """
    Recibe un texto libre (por ejemplo, línea de gasto) y devuelve:
    - item: parte "descriptiva" (tienda, concepto...)
    - amount: importe numérico (float) si lo encuentra
    - date_str: fecha en formato string (si detecta un patrón)
    - confidences: diccionario con las puntuaciones (0.0 a 1.0)

    Esta versión combina:
    - spaCy para tener procesado del texto (podemos usarlo más adelante)
    - Reglas/regex sencillas para amount y date.
    """
    doc = nlp_es(text)

    amount: Optional[float] = None
    amount_conf = 0.0
    date_str: Optional[str] = None
    date_conf = 0.0

    # --- 1) Detectar importe con regex ---
    amount_match = _AMOUNT_PATTERN.search(text)
    if amount_match:
        raw_amount = amount_match.group(1) or amount_match.group(2)
        amount = _normalize_amount(raw_amount)
        if amount is not None:
            amount_conf = 0.9  # Alta confianza porque el patrón es claro

    # --- 2) Detectar fecha con regex ---
    date_match = _DATE_PATTERN.search(text)
    if date_match:
        date_str = date_match.group(1)
        date_conf = 0.9

    # (Opcional) Podríamos intentar usar spaCy para fechas si las detecta:
    # for ent in doc.ents:
    #     if ent.label_ == "DATE" and not date_str:
    #         date_str = ent.text
    #         date_conf = max(date_conf, 0.7)

    # --- 3) Intentar sacar el "item" ---
    # Estrategia simple: quitamos del texto original el trozo de importe
    # y el trozo de fecha, y lo que quede lo consideramos item.
    item_candidate = text

    if amount_match:
        item_candidate = item_candidate.replace(amount_match.group(0), "")

    if date_match:
        item_candidate = item_candidate.replace(date_match.group(0), "")

    # Limpiamos espacios y signos sueltos
    item_candidate = item_candidate.strip(" -–,;:·\t\n")

    if item_candidate:
        item = item_candidate
        item_conf = 0.7  # Confianza media, es una heurística
    else:
        item = None
        item_conf = 0.0

    confidences = {
        "item": item_conf,
        "amount": amount_conf,
        "date_str": date_conf,
    }

    non_zero_values = [v for v in confidences.values() if v > 0]
    if non_zero_values:
        overall_confidence = sum(non_zero_values) / len(non_zero_values)
    else:
        overall_confidence = 0.0

    # Esto por ahora casi siempre será "es", pero lo dejamos por si
    # más adelante usamos otros modelos.
    result: Dict[str, Any] = {
        "item": item,
        "amount": amount,
        "date_str": date_str,
        "confidences": confidences,
        "overall_confidence": overall_confidence,
        "language": getattr(doc, "lang_", "es"),
        "raw_text": text,
    }

    return result


if __name__ == "__main__":
    # Pequeña prueba manual si ejecutas:
    #   python -m app.services.nlp
    sample = "Supermercado DIA 23,45 € 12/10/2025"
    print(extract_fields_from_text(sample))
