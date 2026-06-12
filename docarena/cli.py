from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from .manifest import ManifestError, validate_manifest, write_default_manifest
from .openrouter import CONTESTANT_MODELS, CostLimitError, enforce_cost_limit, estimate_run_cost
from .prompts import PROMPT_VARIANTS
from .render import render_pdf, write_rendered_manifest
from .report import build_leaderboard_rows, write_leaderboard
from .runner import run_tournament
from .scoring import score_prediction
from .utils import ensure_parent, sha256_file


DEFAULT_MANIFEST = Path("dataset_manifest.json")


def _add_manifest_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to dataset manifest JSON.")


def _cmd_manifest_validate(args: argparse.Namespace) -> int:
    try:
        manifest = validate_manifest(args.manifest)
    except (ManifestError, OSError, json.JSONDecodeError) as exc:
        print(f"manifest invalid: {exc}", file=sys.stderr)
        return 2
    print(f"manifest valid: {len(manifest.documents)} documents")
    return 0


def _cmd_sources_check(args: argparse.Namespace) -> int:
    manifest = validate_manifest(args.manifest)
    failures = 0
    for doc in manifest.documents:
        request = urllib.request.Request(doc.source_url, method="HEAD")
        try:
            with urllib.request.urlopen(request, timeout=args.timeout_s) as response:
                print(f"{doc.doc_id}: {response.status} {doc.source_url}")
        except Exception as exc:
            failures += 1
            print(f"{doc.doc_id}: failed {doc.source_url} ({exc})", file=sys.stderr)
    return 1 if failures else 0


def _cmd_fetch(args: argparse.Namespace) -> int:
    manifest = validate_manifest(args.manifest)
    if args.dry_run or not args.allow_download:
        for doc in manifest.documents:
            print(f"dry run: would download {doc.source_url} -> {doc.local_pdf_path}")
        return 0
    for doc in manifest.documents:
        ensure_parent(doc.local_pdf_path)
        with urllib.request.urlopen(doc.source_url, timeout=args.timeout_s) as response:
            doc.local_pdf_path.write_bytes(response.read())
        print(f"downloaded {doc.doc_id}: {sha256_file(doc.local_pdf_path)}")
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    manifest = validate_manifest(args.manifest)
    rendered = []
    for doc in manifest.documents:
        if args.active_only and doc.split != "active":
            continue
        if not doc.local_pdf_path.exists():
            print(f"missing PDF for {doc.doc_id}: {doc.local_pdf_path}", file=sys.stderr)
            continue
        rendered.append(render_pdf(doc.local_pdf_path, Path(args.output_dir) / doc.doc_id, doc.selected_pages, args.dpi, doc.doc_id))
    target = write_rendered_manifest(rendered, args.output)
    print(f"wrote {target}")
    return 0


def _cmd_gold_export_pack(args: argparse.Namespace) -> int:
    manifest = validate_manifest(args.manifest)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    pack_path = out / "gold_label_pack.json"
    docs = [
        {
            "doc_id": doc.doc_id,
            "category": doc.category,
            "source_url": doc.source_url,
            "selected_pages": doc.selected_pages,
            "local_pdf_path": str(doc.local_pdf_path),
            "gold_output_path": f"gold/{doc.doc_id}.gold.json",
            "schema": {
                "document_type": "string",
                "involved_names": "list with context",
                "dates": "list",
                "numbers": "list",
                "required_fields": "object",
                "optional_fields": "object",
                "full_document_summary": "string",
                "evidence_notes": "list",
                "locked": True,
            },
        }
        for doc in manifest.documents
        if not args.active_only or doc.split == "active"
    ]
    pack_path.write_text(json.dumps({"documents": docs}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {pack_path}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    models = args.models or list(CONTESTANT_MODELS)
    prompts = args.prompts or list(PROMPT_VARIANTS)
    if args.dry_run:
        print(f"dry run: {len(models)} models x {len(prompts)} prompts; no API key required")
        return 0
    rendered_docs = json.loads(Path(args.rendered_manifest).read_text(encoding="utf-8"))
    page_counts = [len(doc.get("pages", [])) for doc in rendered_docs]
    pages_per_document = sum(page_counts) / len(page_counts) if page_counts else 0
    computed_estimate = estimate_run_cost(len(models), len(prompts), len(rendered_docs), pages_per_document)
    estimate = max(args.estimated_cost_usd, computed_estimate)
    try:
        enforce_cost_limit(estimate, args.max_cost_usd, args.spend)
    except CostLimitError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is required for --spend runs", file=sys.stderr)
        return 2
    output = run_tournament(args.rendered_manifest, args.output, models, prompts)
    print(f"wrote {output}")
    return 0


def _cmd_score(args: argparse.Namespace) -> int:
    predictions_path = Path(args.predictions)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    scored = []
    for item in predictions:
        gold_path = Path(args.gold_dir) / f"{item['doc_id']}.gold.json"
        gold = json.loads(gold_path.read_text(encoding="utf-8"))
        score = score_prediction(item.get("parsed_json"), gold).to_dict()
        scored.append({**item, **score})
    out.write_text(json.dumps(scored, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    paths = list(Path(args.scores_dir).glob("*.score.json"))
    rows = build_leaderboard_rows(paths)
    md, csv_path = write_leaderboard(rows, args.output_dir)
    runs_path = Path(args.output_dir) / "runs.jsonl"
    with runs_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"timestamp": time.time(), "score_files": [str(path) for path in paths], "rows": len(rows)}) + "\n")
    print(f"wrote {md} and {csv_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docarena")
    sub = parser.add_subparsers(dest="command", required=True)

    manifest = sub.add_parser("manifest")
    manifest_sub = manifest.add_subparsers(dest="manifest_command", required=True)
    validate = manifest_sub.add_parser("validate")
    _add_manifest_arg(validate)
    validate.set_defaults(func=_cmd_manifest_validate)

    sources = sub.add_parser("sources")
    sources_sub = sources.add_subparsers(dest="sources_command", required=True)
    check = sources_sub.add_parser("check")
    _add_manifest_arg(check)
    check.add_argument("--timeout-s", type=int, default=15)
    check.set_defaults(func=_cmd_sources_check)

    fetch = sub.add_parser("fetch")
    _add_manifest_arg(fetch)
    fetch.add_argument("--dry-run", action="store_true")
    fetch.add_argument("--allow-download", action="store_true")
    fetch.add_argument("--timeout-s", type=int, default=60)
    fetch.set_defaults(func=_cmd_fetch)

    render = sub.add_parser("render")
    _add_manifest_arg(render)
    render.add_argument("--output", default="rendered_manifest.json")
    render.add_argument("--output-dir", default="data/rendered")
    render.add_argument("--dpi", type=int, default=200)
    render.add_argument("--active-only", action="store_true")
    render.set_defaults(func=_cmd_render)

    gold = sub.add_parser("gold")
    gold_sub = gold.add_subparsers(dest="gold_command", required=True)
    export = gold_sub.add_parser("export-pack")
    _add_manifest_arg(export)
    export.add_argument("--output", default="gold_pack")
    export.add_argument("--active-only", action="store_true")
    export.set_defaults(func=_cmd_gold_export_pack)

    run = sub.add_parser("run")
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("--spend", action="store_true")
    run.add_argument("--max-cost-usd", type=float)
    run.add_argument("--estimated-cost-usd", type=float, default=0.0)
    run.add_argument("--models", nargs="*")
    run.add_argument("--prompts", nargs="*")
    run.add_argument("--rendered-manifest", default="rendered_manifest.json")
    run.add_argument("--output", default="predictions/latest.json")
    run.set_defaults(func=_cmd_run)

    score = sub.add_parser("score")
    score.add_argument("--predictions", default="predictions/latest.json")
    score.add_argument("--gold-dir", default="gold")
    score.add_argument("--output", default="scores/latest.score.json")
    score.set_defaults(func=_cmd_score)

    report = sub.add_parser("report")
    report.add_argument("--scores-dir", default="scores")
    report.add_argument("--output-dir", default="reports")
    report.set_defaults(func=_cmd_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    if not DEFAULT_MANIFEST.exists():
        write_default_manifest(DEFAULT_MANIFEST)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def console() -> None:
    raise SystemExit(main())
