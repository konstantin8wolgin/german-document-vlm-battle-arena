import json

from docarena.report import build_leaderboard_rows, write_leaderboard
from docarena.scoring import score_prediction


def test_score_prediction_penalizes_missing_required_field_and_hallucination():
    gold = {
        "document_type": "rechnung",
        "required_fields": {
            "invoice_number": "R-100",
            "total_amount": "1.234,56 EUR",
            "invoice_date": "12.06.2026",
        },
        "entities": [{"name": "Muster GmbH", "context": "issuer"}],
        "summary": "Rechnung der Muster GmbH.",
        "locked": True,
    }
    prediction = {
        "document_type": "rechnung",
        "required_fields": {
            "invoice_number": "R-100",
            "total_amount": "1234.56",
        },
        "entities": [{"name": "Fantasie AG", "context": "issuer"}],
        "summary": "Rechnung.",
    }

    score = score_prediction(prediction, gold)

    assert score.json_valid is True
    assert score.required_field_accuracy == 2 / 3
    assert score.hallucination_penalty > 0
    assert 0 <= score.final_score <= 10


def test_write_leaderboard_aggregates_scores_cost_and_latency(tmp_path):
    score_path = tmp_path / "run.score.json"
    score_path.write_text(
        json.dumps(
            [
                {
                    "category": "rechnungen",
                    "model": "qwen/qwen3-vl-8b-instruct",
                    "prompt": "strict_schema",
                    "doc_id": "rechnung_001",
                    "final_score": 8.0,
                    "required_field_accuracy": 1.0,
                    "json_valid": True,
                    "numeric_date_accuracy": 0.5,
                    "hallucination_penalty": 0.0,
                    "cost_usd": 0.02,
                    "latency_s": 3.0,
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = build_leaderboard_rows([score_path])
    markdown, csv_path = write_leaderboard(rows, tmp_path)

    assert rows[0]["mean_score"] == 8.0
    assert "| rechnungen | qwen/qwen3-vl-8b-instruct | strict_schema | 1 | 8.00 |" in markdown.read_text(encoding="utf-8")
    assert "cost_usd" in csv_path.read_text(encoding="utf-8")
