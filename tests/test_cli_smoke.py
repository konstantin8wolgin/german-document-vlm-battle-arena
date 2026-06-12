import json

from docarena.cli import main


def test_cli_manifest_validate_smoke(tmp_path, capsys):
    manifest = tmp_path / "dataset_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "doc_id": "rechnung_001",
                        "category": "rechnungen",
                        "source_url": "https://example.org/sample.pdf",
                        "source_license_note": "public sample",
                        "selected_pages": [1],
                        "split": "active",
                        "local_pdf_path": "data/pdfs/rechnung_001.pdf",
                        "sha256": None,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert main(["manifest", "validate", "--manifest", str(manifest)]) == 0
    assert "valid" in capsys.readouterr().out


def test_cli_run_dry_run_does_not_require_api_key(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    assert main(["run", "--dry-run"]) == 0
    assert "dry run" in capsys.readouterr().out.lower()
