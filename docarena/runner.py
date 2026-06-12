from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

from .openrouter import CONTESTANT_MODELS, build_vision_payload, call_openrouter
from .prompts import PROMPT_VARIANTS, prompt_for


def load_rendered_manifest(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("rendered manifest must be a list")
    return data


def _result_to_dict(result) -> dict:
    if isinstance(result, dict):
        return result
    return {
        "raw_response": result.raw_response,
        "parsed_json": result.parsed_json,
        "usage": result.usage,
        "latency_s": result.latency_s,
        "status": result.status,
    }


def run_tournament(
    rendered_manifest_path: str | Path,
    output_path: str | Path,
    models: list[str] | None = None,
    prompts: list[str] | None = None,
    call_model: Callable[[dict], object] | None = None,
    max_tokens: int = 1500,
) -> Path:
    rendered_docs = load_rendered_manifest(rendered_manifest_path)
    selected_models = models or list(CONTESTANT_MODELS)
    selected_prompts = prompts or list(PROMPT_VARIANTS)
    caller = call_model or call_openrouter
    rows: list[dict] = []

    for doc in rendered_docs:
        image_paths = [page["image_path"] for page in doc.get("pages", [])]
        for model in selected_models:
            for prompt_name in selected_prompts:
                started = time.perf_counter()
                payload = build_vision_payload(
                    model=model,
                    prompt=prompt_for(prompt_name, doc.get("category", "document")),
                    image_paths=[Path(path) for path in image_paths],
                    max_tokens=max_tokens,
                )
                try:
                    result = _result_to_dict(caller(payload))
                except Exception as exc:
                    result = {
                        "raw_response": {"error": str(exc)},
                        "parsed_json": None,
                        "usage": {},
                        "latency_s": time.perf_counter() - started,
                        "status": "error",
                    }
                rows.append(
                    {
                        "run_id": Path(output_path).stem,
                        "category": doc.get("category", "unknown"),
                        "model": model,
                        "prompt": prompt_name,
                        "doc_id": doc["doc_id"],
                        "input_image_paths": image_paths,
                        "raw_response": result.get("raw_response"),
                        "parsed_json": result.get("parsed_json"),
                        "usage": result.get("usage", {}),
                        "latency_s": result.get("latency_s", 0),
                        "status": result.get("status", "unknown"),
                        "cost_usd": float(result.get("cost_usd", 0) or 0),
                    }
                )

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return target
