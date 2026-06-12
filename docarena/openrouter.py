from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


CONTESTANT_MODELS = (
    "qwen/qwen3-vl-235b-a22b-instruct",
    "qwen/qwen3-vl-32b-instruct",
    "qwen/qwen3-vl-8b-instruct",
    "z-ai/glm-4.6v",
    "mistralai/mistral-medium-3-5",
    "mistralai/mistral-small-2603",
    "qwen/qwen2.5-vl-72b-instruct",
    "meta-llama/llama-3.2-11b-vision-instruct",
)


class CostLimitError(ValueError):
    pass


@dataclass(frozen=True)
class ModelCallResult:
    model: str
    raw_response: dict
    parsed_json: dict | None
    latency_s: float
    usage: dict
    status: str


def _mime_for(path: Path) -> str:
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        return "image/jpeg"
    return "image/png"


def build_vision_payload(model: str, prompt: str, image_paths: list[str | Path], max_tokens: int = 1500) -> dict:
    content: list[dict] = [{"type": "text", "text": prompt}]
    for image_path in image_paths:
        path = Path(image_path)
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        content.append({"type": "image_url", "image_url": {"url": f"data:{_mime_for(path)};base64,{encoded}"}})
    return {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }


def parse_model_json(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError("response is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("response JSON must be an object")
    return parsed


def enforce_cost_limit(estimated_cost_usd: float, max_cost_usd: float | None, spend: bool) -> None:
    if not spend:
        raise CostLimitError("real model calls require --spend")
    if max_cost_usd is None:
        raise CostLimitError("--max-cost-usd is required with --spend")
    if estimated_cost_usd > max_cost_usd:
        raise CostLimitError(f"estimated cost {estimated_cost_usd:.2f} exceeds cap {max_cost_usd:.2f}")


def estimate_run_cost(
    models: int,
    prompts: int,
    documents: int,
    pages_per_document: float,
    estimated_cost_per_page_prompt_model_usd: float = 0.01,
) -> float:
    if min(models, prompts, documents) < 0 or pages_per_document < 0:
        raise ValueError("cost estimate inputs must be non-negative")
    return round(models * prompts * documents * pages_per_document * estimated_cost_per_page_prompt_model_usd, 4)


def call_openrouter(payload: dict, api_key: str | None = None, timeout_s: int = 120) -> ModelCallResult:
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is required for real runs")
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc
    latency = time.perf_counter() - started
    message = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
    try:
        parsed = parse_model_json(message)
        status = "ok"
    except ValueError:
        parsed = None
        status = "malformed_json"
    return ModelCallResult(
        model=payload["model"],
        raw_response=raw,
        parsed_json=parsed,
        latency_s=latency,
        usage=raw.get("usage", {}),
        status=status,
    )
