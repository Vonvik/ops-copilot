import csv
import hashlib
from collections.abc import Iterable
from datetime import date
from io import StringIO

from dateutil import parser as dateparser

from app.schemas.processed import ProcessedIn

ALIASES = {
    "item": {"item", "concepto", "descripcion", "description", "detalle"},
    "amount": {"amount", "importe", "monto", "valor", "precio"},
    "date": {"date", "fecha", "date_str", "fecha_operacion"},
}


def _map_headers(headers: Iterable[str]) -> dict[str, int]:
    idx = {h.lower().strip(): i for i, h in enumerate(headers)}

    def find_one(target_set):
        for k, i in idx.items():
            if k in target_set:
                return i
        return None

    m = {
        "item": find_one(ALIASES["item"]),
        "amount": find_one(ALIASES["amount"]),
        "date": find_one(ALIASES["date"]),
    }
    if None in m.values():
        raise ValueError("Faltan columnas requeridas: item/amount/date")
    return m


def _parse_date(s: str) -> date:
    return dateparser.parse(s.strip(), dayfirst=True).date()


def line_hash(source_file: str, item: str, amount: float, d: date) -> str:
    return hashlib.sha256(f"{source_file}|{item}|{amount}|{d.isoformat()}".encode()).hexdigest()


def parse_csv_bytes(data: bytes, filename: str, encoding: str = "utf-8"):
    text = data.decode(encoding, errors="replace")
    f = StringIO(text)
    reader = csv.reader(f)
    headers = next(reader, None)
    if not headers:
        raise ValueError("CSV vacío")
    mapping = _map_headers(headers)
    for row in reader:
        if not row or all(not cell.strip() for cell in row):
            continue
        item = row[mapping["item"]].strip()
        amount_raw = row[mapping["amount"]]
        date_raw = row[mapping["date"]]
        p = ProcessedIn(source_file=filename, item=item, amount=amount_raw, date_str=date_raw)
        amount = p.amount
        d = _parse_date(p.date_str)
        yield {
            "source_file": filename,
            "item": item,
            "amount": amount,
            "date": d,
            "line_hash": line_hash(filename, item, amount, d),
        }
