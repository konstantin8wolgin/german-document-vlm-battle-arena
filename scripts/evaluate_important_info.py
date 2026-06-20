from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


STOPWORDS = {
    "aber",
    "alle",
    "auch",
    "auf",
    "aus",
    "bei",
    "bis",
    "das",
    "dem",
    "den",
    "der",
    "des",
    "die",
    "dies",
    "diese",
    "dieser",
    "dieses",
    "eine",
    "einem",
    "einen",
    "einer",
    "eines",
    "für",
    "haben",
    "hier",
    "ihre",
    "ihrer",
    "ist",
    "mit",
    "nach",
    "nicht",
    "oder",
    "seite",
    "sich",
    "sie",
    "und",
    "vom",
    "von",
    "wenn",
    "werden",
    "wie",
    "wir",
    "zur",
    "zum",
}

CATEGORY_TERMS = {
    "rechnungen": {"rechnung", "rechnungsnummer", "steuernummer", "betrag", "mehrwertsteuer", "zahlungsfrist", "iban"},
    "vertraege": {"vertrag", "vertragsparteien", "auftragnehmer", "auftraggeber", "leistung", "laufzeit", "kündigung"},
    "behoerdenpost": {"bescheid", "behörde", "aktenzeichen", "frist", "antrag", "widerspruch", "datum"},
    "versicherung": {"versicherung", "versicherungsnummer", "police", "schaden", "beitrag", "leistung", "kündigung"},
    "bank_finanzen": {"konto", "iban", "betrag", "saldo", "zins", "darlehen", "kundennummer"},
    "steuer": {"steuer", "finanzamt", "steuernummer", "betrag", "bescheid", "frist", "einkommen"},
    "medizin": {"patient", "diagnose", "arzt", "befund", "datum", "medikation", "untersuchung"},
    "formulare": {"formular", "antrag", "name", "datum", "unterschrift", "adresse", "angaben"},
}

DOC_TYPE_HINTS = {
    "rechnungen": {"rechnung"},
    "vertraege": {"vertrag"},
    "behoerdenpost": {"bescheid", "schreiben", "behörde", "behoerde"},
    "versicherung": {"versicherung", "police", "schaden"},
    "bank_finanzen": {"bank", "konto", "finanz", "darlehen"},
    "steuer": {"steuer", "finanzamt", "bescheid"},
    "medizin": {"medizin", "arzt", "befund", "patient"},
    "formulare": {"formular", "antrag"},
}


def _norm(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def _tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9_-]{3,}", text)
        if token.lower() not in STOPWORDS
    ]


def _numbers_and_dates(text: str) -> list[str]:
    patterns = [
        r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b",
        r"\btt\.mm\.jjj+\b",
        r"\b\d[\d .,:/-]{1,}\d\b",
        r"\b\d+,\d{2}\b",
        r"\bX{4,}\b",
    ]
    found: list[str] = []
    for pattern in patterns:
        found.extend(match.group(0) for match in re.finditer(pattern, text, flags=re.IGNORECASE))
    return sorted({_norm_number(item) for item in found if len(_norm_number(item)) >= 3})


def _norm_number(value: str) -> str:
    return re.sub(r"\s+", "", value.lower())


def _selected_page_text(pdf_path: Path, pages: list[int]) -> str:
    chunks = []
    for page in pages:
        completed = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), str(pdf_path), "-"],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            chunks.append(completed.stdout)
    return "\n".join(chunks)


def build_references(manifest_path: Path) -> dict[str, dict]:
    docs = json.loads(manifest_path.read_text(encoding="utf-8"))["documents"]
    refs = {}
    for doc in docs:
        text = _selected_page_text(Path(doc["local_pdf_path"]), doc.get("selected_pages", [1]))
        tokens = _tokenize(text)
        counts = Counter(tokens)
        category = doc["category"]
        important_terms = set(CATEGORY_TERMS.get(category, set()))
        for token, _count in counts.most_common(50):
            if len(token) >= 5:
                important_terms.add(token)
        refs[doc["doc_id"]] = {
            "doc_id": doc["doc_id"],
            "category": category,
            "pages": doc.get("selected_pages", []),
            "important_terms": sorted(important_terms),
            "numbers_dates": _numbers_and_dates(text),
            "text_chars": len(text),
        }
    return refs


def _serialized_prediction(row: dict) -> str:
    parsed = row.get("parsed_json")
    if parsed is None:
        parsed = row.get("raw_response")
    return _norm(json.dumps(parsed, ensure_ascii=False, sort_keys=True))


def _term_recall(reference_terms: list[str], prediction_text: str) -> float:
    if not reference_terms:
        return 0.0
    hits = sum(1 for term in reference_terms if _norm(term) in prediction_text)
    return hits / len(reference_terms)


def _number_recall(reference_numbers: list[str], prediction_text: str) -> float:
    if not reference_numbers:
        return 0.0
    compact_prediction = _norm_number(prediction_text)
    hits = sum(1 for number in reference_numbers if number in compact_prediction)
    return hits / len(reference_numbers)


def _doc_type_score(category: str, prediction_text: str) -> float:
    hints = DOC_TYPE_HINTS.get(category, set())
    return 1.0 if any(hint in prediction_text for hint in hints) else 0.0


def _field_presence(parsed: object) -> float:
    if not isinstance(parsed, dict):
        return 0.0
    expected = ["document_type", "involved_names", "dates", "numbers", "required_fields", "full_document_summary"]
    return sum(1 for key in expected if parsed.get(key)) / len(expected)


def score_predictions(predictions: list[dict], refs: dict[str, dict]) -> list[dict]:
    scored = []
    for row in predictions:
        ref = refs[row["doc_id"]]
        prediction_text = _serialized_prediction(row)
        term_recall = _term_recall(ref["important_terms"], prediction_text)
        number_recall = _number_recall(ref["numbers_dates"], prediction_text)
        doc_type = _doc_type_score(ref["category"], prediction_text)
        field_presence = _field_presence(row.get("parsed_json"))
        json_valid = 1.0 if row.get("status") == "ok" and isinstance(row.get("parsed_json"), dict) else 0.0
        if json_valid:
            final_score = (
                0.35 * term_recall
                + 0.35 * number_recall
                + 0.10 * doc_type
                + 0.10 * field_presence
                + 0.10 * json_valid
            )
        else:
            final_score = 0.0
        scored.append(
            {
                "category": ref["category"],
                "doc_id": row["doc_id"],
                "model": row["model"],
                "prompt": row["prompt"],
                "status": row.get("status"),
                "json_valid": bool(json_valid),
                "important_term_recall": round(term_recall, 4),
                "number_date_recall": round(number_recall, 4),
                "doc_type_score": round(doc_type, 4),
                "field_presence": round(field_presence, 4),
                "final_score": round(final_score, 4),
                "latency_s": round(float(row.get("latency_s", 0) or 0), 2),
                "cost_usd": round(float(row.get("cost_usd", 0) or 0), 4),
            }
        )
    return scored


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def aggregate(scored: list[dict], keys: tuple[str, ...]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in scored:
        groups[tuple(row[key] for key in keys)].append(row)
    rows = []
    for key_values, items in groups.items():
        row = {key: value for key, value in zip(keys, key_values)}
        row.update(
            {
                "rows": len(items),
                "docs": len({item["doc_id"] for item in items}),
                "ok": sum(1 for item in items if item["status"] == "ok"),
                "malformed_json": sum(1 for item in items if item["status"] == "malformed_json"),
                "error": sum(1 for item in items if item["status"] == "error"),
                "final_score": round(_mean([item["final_score"] for item in items]), 4),
                "important_term_recall": round(_mean([item["important_term_recall"] for item in items]), 4),
                "number_date_recall": round(_mean([item["number_date_recall"] for item in items]), 4),
                "field_presence": round(_mean([item["field_presence"] for item in items]), 4),
                "avg_latency_s": round(_mean([item["latency_s"] for item in items]), 2),
                "cost_usd": round(sum(item["cost_usd"] for item in items), 4),
            }
        )
        rows.append(row)
    rows.sort(key=lambda row: (-row["final_score"], -row["ok"], row["avg_latency_s"], row.get("model", "")))
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, overall: list[dict], by_category: list[dict], scored_path: Path) -> None:
    headers = [
        "rank",
        "model",
        "final_score",
        "ok",
        "malformed_json",
        "error",
        "important_term_recall",
        "number_date_recall",
        "field_presence",
        "avg_latency_s",
    ]
    lines = [
        "# Important-Information Leaderboard",
        "",
        "This evaluator compares each parsed model output with locally extracted reference terms from the selected PDF pages. Contestant model calls used rendered page images only; this report is post-run local evaluation.",
        "",
        "Invalid or missing parsed JSON is gated to a zero final score. For valid rows, scoring weights are: important terms 35%, numbers/dates 35%, document type 10%, required output-field presence 10%, valid parsed JSON 10%. Treat this as a practical no-gold-label leaderboard, not a certified accuracy benchmark.",
        "",
        f"Detailed scored rows: `{scored_path}`",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for index, row in enumerate(overall, start=1):
        values = {**row, "rank": index}
        lines.append("| " + " | ".join(str(values.get(header, "")) for header in headers) + " |")

    lines.extend(["", "## Category Winners", ""])
    category_headers = ["category", "model", "final_score", "ok", "malformed_json", "error", "avg_latency_s"]
    lines.extend(
        [
            "| " + " | ".join(category_headers) + " |",
            "| " + " | ".join(["---"] * len(category_headers)) + " |",
        ]
    )
    winners = {}
    for row in by_category:
        winners.setdefault(row["category"], row)
    for category in sorted(winners):
        row = winners[category]
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in category_headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: evaluate_important_info.py PREDICTIONS_JSON MANIFEST_JSON OUTPUT_DIR", file=sys.stderr)
        return 2
    predictions_path = Path(sys.argv[1])
    manifest_path = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    refs = build_references(manifest_path)
    scored = score_predictions(predictions, refs)
    overall = aggregate(scored, ("model",))
    by_category = aggregate(scored, ("category", "model"))

    output_dir.mkdir(parents=True, exist_ok=True)
    refs_path = output_dir / "important_info_references.json"
    scored_path = output_dir / "important_info_scored_rows.csv"
    overall_csv = output_dir / "important_info_leaderboard.csv"
    category_csv = output_dir / "important_info_by_category.csv"
    md_path = output_dir / "important_info_leaderboard.md"

    refs_path.write_text(json.dumps(refs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(scored_path, scored)
    write_csv(overall_csv, overall)
    write_csv(category_csv, by_category)
    write_markdown(md_path, overall, by_category, scored_path)
    print(f"wrote {md_path}, {overall_csv}, {category_csv}, {scored_path}, {refs_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
