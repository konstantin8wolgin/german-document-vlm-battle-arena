from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from write_ai_comparison import write_report


def _all_gold_present(predictions: list[dict], gold_dir: Path) -> bool:
    doc_ids = {str(item.get("doc_id")) for item in predictions if item.get("doc_id")}
    return bool(doc_ids) and all((gold_dir / f"{doc_id}.gold.json").exists() for doc_id in doc_ids)


def _run(cmd: list[str]) -> int:
    completed = subprocess.run(cmd, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: postprocess_overnight.py PREDICTIONS_JSON REPORT_DIR STATUS_PATH", file=sys.stderr)
        return 2

    predictions_path = Path(sys.argv[1])
    report_dir = Path(sys.argv[2])
    status_path = Path(sys.argv[3])
    status_path.parent.mkdir(parents=True, exist_ok=True)

    if not predictions_path.exists():
        status_path.write_text(f"no predictions found at {predictions_path}\n", encoding="utf-8")
        return 1

    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    md_path, csv_path = write_report(predictions_path, report_dir)
    lines = [
        f"timestamp: {time.time()}",
        f"predictions: {predictions_path}",
        f"rows: {len(predictions)}",
        f"ai_comparison_md: {md_path}",
        f"ai_comparison_csv: {csv_path}",
    ]

    gold_dir = Path("gold")
    if _all_gold_present(predictions, gold_dir):
        score_path = Path("scores/strict_schema_all_models_overnight.score.json")
        score_path.parent.mkdir(parents=True, exist_ok=True)
        score_rc = _run(
            [
                sys.executable,
                "-m",
                "docarena",
                "score",
                "--predictions",
                str(predictions_path),
                "--gold-dir",
                str(gold_dir),
                "--output",
                str(score_path),
            ]
        )
        report_rc = _run([sys.executable, "-m", "docarena", "report", "--scores-dir", "scores", "--output-dir", "reports"]) if score_rc == 0 else 1
        lines.extend([f"score_exit: {score_rc}", f"report_exit: {report_rc}", f"score_path: {score_path}"])
    else:
        lines.append("accuracy_leaderboard: unavailable; missing gold labels for completed docs")

    status_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
