import json

from docarena.runner import run_tournament


def test_run_tournament_persists_predictions_with_mocked_model_call(tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"png")
    rendered_manifest = tmp_path / "rendered_manifest.json"
    rendered_manifest.write_text(
        json.dumps(
            [
                {
                    "doc_id": "rechnungen_001",
                    "category": "rechnungen",
                    "pages": [{"image_path": str(image), "page_number": 1}],
                }
            ]
        ),
        encoding="utf-8",
    )

    def fake_call(payload):
        return {
            "raw_response": {"choices": []},
            "parsed_json": {"document_type": "rechnung"},
            "usage": {"total_tokens": 1},
            "latency_s": 0.1,
            "status": "ok",
        }

    output = tmp_path / "predictions" / "run.json"
    run_tournament(
        rendered_manifest_path=rendered_manifest,
        output_path=output,
        models=["test/model"],
        prompts=["strict_schema"],
        call_model=fake_call,
    )

    rows = json.loads(output.read_text(encoding="utf-8"))
    assert rows[0]["model"] == "test/model"
    assert rows[0]["doc_id"] == "rechnungen_001"
    assert rows[0]["parsed_json"] == {"document_type": "rechnung"}


def test_runner_payload_uses_universal_image_only_prompt_rule(tmp_path):
    image = tmp_path / "page.png"
    image.write_bytes(b"png")
    rendered_manifest = tmp_path / "rendered_manifest.json"
    rendered_manifest.write_text(
        json.dumps(
            [
                {
                    "doc_id": "formulare_001",
                    "category": "formulare",
                    "pages": [{"image_path": str(image), "page_number": 1}],
                }
            ]
        ),
        encoding="utf-8",
    )
    prompts = []

    def fake_call(payload):
        prompts.append(payload["messages"][0]["content"][0]["text"])
        return {"raw_response": {}, "parsed_json": {}, "usage": {}, "latency_s": 0.1, "status": "ok"}

    run_tournament(
        rendered_manifest_path=rendered_manifest,
        output_path=tmp_path / "predictions.json",
        models=["test/model"],
        prompts=["strict_schema", "evidence_first", "role_specialist"],
        call_model=fake_call,
    )

    assert len(prompts) == 3
    assert all("only the rendered page images" in prompt for prompt in prompts)
    assert all("Do not use OCR" in prompt for prompt in prompts)
