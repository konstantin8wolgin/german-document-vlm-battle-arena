from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_leaderboard_rows(score_paths: list[str | Path]) -> list[dict]:
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for score_path in score_paths:
        data = json.loads(Path(score_path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("scores", [])
        for row in data:
            groups[(row["category"], row["model"], row["prompt"])].append(row)

    rows = []
    for (category, model, prompt), items in sorted(groups.items()):
        rows.append(
            {
                "category": category,
                "model": model,
                "prompt": prompt,
                "docs": len({item["doc_id"] for item in items}),
                "mean_score": round(_mean([float(item.get("final_score", 0)) for item in items]), 2),
                "required_field_accuracy": round(_mean([float(item.get("required_field_accuracy", 0)) for item in items]), 3),
                "json_valid_rate": round(_mean([1.0 if item.get("json_valid") else 0.0 for item in items]), 3),
                "numeric_date_accuracy": round(_mean([float(item.get("numeric_date_accuracy", 0)) for item in items]), 3),
                "hallucination_penalty": round(_mean([float(item.get("hallucination_penalty", 0)) for item in items]), 3),
                "cost_usd": round(sum(float(item.get("cost_usd", 0)) for item in items), 4),
                "latency_s": round(_mean([float(item.get("latency_s", 0)) for item in items]), 2),
            }
        )
    rows.sort(key=lambda row: (row["category"], -row["mean_score"], row["model"], row["prompt"]))
    return rows


def write_leaderboard(rows: list[dict], output_dir: str | Path) -> tuple[Path, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    md = out / "leaderboard.md"
    csv_path = out / "leaderboard.csv"
    headers = [
        "category",
        "model",
        "prompt",
        "docs",
        "mean_score",
        "required_field_accuracy",
        "json_valid_rate",
        "numeric_date_accuracy",
        "hallucination_penalty",
        "cost_usd",
        "latency_s",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[header]) if header != "mean_score" else f"{row[header]:.2f}" for header in headers) + " |")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return md, csv_path
