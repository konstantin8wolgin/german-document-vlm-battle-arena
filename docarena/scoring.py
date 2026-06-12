from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Score:
    json_valid: bool
    document_type_score: float
    required_field_accuracy: float
    numeric_date_accuracy: float
    entity_context_score: float
    summary_score: float
    hallucination_penalty: float
    final_score: float

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_value(value) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = text.replace("€", " eur")
    text = re.sub(r"\s+", " ", text)
    date_match = re.fullmatch(r"(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})", text)
    if date_match:
        day, month, year = date_match.groups()
        if len(year) == 2:
            year = "20" + year
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    amount_text = re.sub(r"[^0-9,.-]", "", text)
    if amount_text and any(char.isdigit() for char in amount_text):
        if "," in amount_text and "." in amount_text:
            amount_text = amount_text.replace(".", "").replace(",", ".")
        elif "," in amount_text:
            amount_text = amount_text.replace(",", ".")
        try:
            return str(Decimal(amount_text).quantize(Decimal("0.01")))
        except InvalidOperation:
            pass
    return text


def _field_accuracy(predicted: dict, expected: dict) -> tuple[float, float]:
    if not expected:
        return 1.0, 1.0
    correct = 0
    numeric_date_total = 0
    numeric_date_correct = 0
    for key, gold_value in expected.items():
        prediction_value = predicted.get(key)
        matches = normalize_value(prediction_value) == normalize_value(gold_value)
        correct += int(matches)
        if re.search(r"(date|datum|amount|betrag|summe|total)", key, re.I):
            numeric_date_total += 1
            numeric_date_correct += int(matches)
    return correct / len(expected), (numeric_date_correct / numeric_date_total if numeric_date_total else 1.0)


def _entity_score(prediction: dict, gold: dict) -> tuple[float, float]:
    gold_names = {normalize_value(item.get("name")) for item in gold.get("entities", []) if isinstance(item, dict)}
    pred_names = {normalize_value(item.get("name")) for item in prediction.get("entities", []) if isinstance(item, dict)}
    if not gold_names:
        base = 1.0
    else:
        base = len(gold_names & pred_names) / len(gold_names)
    hallucinated = len(pred_names - gold_names)
    penalty = min(2.0, hallucinated * 0.5)
    return base, penalty


def _summary_score(prediction: dict, gold: dict) -> float:
    pred = normalize_value(prediction.get("summary") or prediction.get("full_document_summary"))
    expected = normalize_value(gold.get("summary") or gold.get("full_document_summary"))
    if not expected:
        return 1.0
    if not pred:
        return 0.0
    expected_terms = {term for term in re.split(r"\W+", expected) if len(term) > 4}
    pred_terms = {term for term in re.split(r"\W+", pred) if len(term) > 4}
    if not expected_terms:
        return 1.0
    return min(1.0, len(expected_terms & pred_terms) / max(1, min(len(expected_terms), 8)))


def score_prediction(prediction: dict | None, gold: dict) -> Score:
    if not isinstance(prediction, dict):
        return Score(False, 0, 0, 0, 0, 0, 0, 0)
    document_type_score = float(normalize_value(prediction.get("document_type")) == normalize_value(gold.get("document_type")))
    required_accuracy, numeric_date_accuracy = _field_accuracy(
        prediction.get("required_fields", {}) if isinstance(prediction.get("required_fields"), dict) else {},
        gold.get("required_fields", {}) if isinstance(gold.get("required_fields"), dict) else {},
    )
    entity_score, hallucination_penalty = _entity_score(prediction, gold)
    summary_score = _summary_score(prediction, gold)
    weighted = (
        document_type_score * 2.0
        + required_accuracy * 3.0
        + numeric_date_accuracy * 1.5
        + entity_score * 1.5
        + summary_score * 2.0
    )
    final = max(0.0, min(10.0, weighted - hallucination_penalty))
    return Score(True, document_type_score, required_accuracy, numeric_date_accuracy, entity_score, summary_score, hallucination_penalty, final)
