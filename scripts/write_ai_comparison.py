from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _status_count(items: list[dict], status: str) -> int:
    return sum(1 for item in items if item.get("status") == status)


def build_rows(predictions: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in predictions:
        groups[str(item.get("model", "unknown"))].append(item)

    rows = []
    for model, items in sorted(groups.items()):
        total = len(items)
        ok = _status_count(items, "ok")
        malformed = _status_count(items, "malformed_json")
        error = _status_count(items, "error")
        parsed = sum(1 for item in items if item.get("parsed_json"))
        categories = len({item.get("category") for item in items})
        docs = len({item.get("doc_id") for item in items})
        rows.append(
            {
                "model": model,
                "calls": total,
                "docs": docs,
                "categories": categories,
                "ok": ok,
                "malformed_json": malformed,
                "error": error,
                "json_valid_rate": round(ok / total, 3) if total else 0,
                "parsed_outputs": parsed,
                "avg_latency_s": round(_mean([float(item.get("latency_s", 0) or 0) for item in items]), 2),
                "cost_usd": round(sum(float(item.get("cost_usd", 0) or 0) for item in items), 4),
            }
        )
    rows.sort(key=lambda row: (-row["json_valid_rate"], row["avg_latency_s"], row["model"]))
    return rows


def write_report(prediction_path: Path, output_dir: Path) -> tuple[Path, Path]:
    predictions = json.loads(prediction_path.read_text(encoding="utf-8"))
    rows = build_rows(predictions)
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "ai_comparison.md"
    csv_path = output_dir / "ai_comparison.csv"

    status_counts = Counter(item.get("status") for item in predictions)
    completed_docs = len({item.get("doc_id") for item in predictions})
    completed_categories = sorted({str(item.get("category")) for item in predictions})
    gold_count = len(list(Path("gold").glob("*.gold.json"))) if Path("gold").exists() else 0

    headers = [
        "model",
        "calls",
        "docs",
        "categories",
        "ok",
        "malformed_json",
        "error",
        "json_valid_rate",
        "parsed_outputs",
        "avg_latency_s",
        "cost_usd",
    ]
    lines = [
        "# AI Comparison",
        "",
        f"Predictions: `{prediction_path}`",
        f"Completed rows: {len(predictions)}",
        f"Completed docs: {completed_docs}",
        f"Completed categories: {', '.join(completed_categories) if completed_categories else 'none'}",
        f"Statuses: {dict(status_counts)}",
        "",
    ]
    if gold_count:
        lines.append(f"Gold labels detected: {gold_count}. Generate accuracy scores with `python3 -m docarena score` and `python3 -m docarena report`.")
    else:
        lines.append("Accuracy leaderboard unavailable: no `gold/*.gold.json` labels are present.")
    lines.extend(
        [
            "",
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
    )
    for row in rows:
        lines.append("| " + " | ".join(str(row[header]) for header in headers) + " |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return md_path, csv_path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: write_ai_comparison.py PREDICTIONS_JSON OUTPUT_DIR", file=sys.stderr)
        return 2
    md_path, csv_path = write_report(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"wrote {md_path} and {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
