import json

import pytest

from docarena.openrouter import (
    CONTESTANT_MODELS,
    CostLimitError,
    build_vision_payload,
    estimate_run_cost,
    parse_model_json,
)


def test_build_vision_payload_sends_only_prompt_and_images(tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"image")

    payload = build_vision_payload(
        model="qwen/qwen3-vl-8b-instruct",
        prompt="Return JSON.",
        image_paths=[image],
        max_tokens=800,
    )

    content = payload["messages"][0]["content"]
    assert payload["model"] == "qwen/qwen3-vl-8b-instruct"
    assert content[0] == {"type": "text", "text": "Return JSON."}
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert "pdf" not in json.dumps(payload).lower()


def test_parse_model_json_accepts_fenced_response():
    parsed = parse_model_json('```json\n{"document_type": "rechnung"}\n```')

    assert parsed == {"document_type": "rechnung"}


def test_parse_model_json_rejects_malformed_response():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_model_json("I refuse")


def test_contestant_models_exclude_deepseek_and_include_required_eight():
    assert len(CONTESTANT_MODELS) >= 8
    assert all("deepseek" not in model.lower() for model in CONTESTANT_MODELS)
    assert "meta-llama/llama-3.2-11b-vision-instruct" in CONTESTANT_MODELS


def test_cost_guard_blocks_when_estimate_exceeds_cap():
    from docarena.openrouter import enforce_cost_limit

    with pytest.raises(CostLimitError):
        enforce_cost_limit(estimated_cost_usd=2.50, max_cost_usd=2.00, spend=True)


def test_estimate_run_cost_scales_with_models_prompts_docs_and_pages():
    estimate = estimate_run_cost(models=2, prompts=3, documents=4, pages_per_document=2)

    assert estimate > 0
    assert estimate == estimate_run_cost(models=1, prompts=3, documents=4, pages_per_document=2) * 2
