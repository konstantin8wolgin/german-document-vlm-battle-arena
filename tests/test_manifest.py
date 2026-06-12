import json

import pytest

from docarena.manifest import ACTIVE_CATEGORIES, ManifestError, validate_manifest


def _entry(doc_id="rechnung_001", category="rechnungen", active=True):
    return {
        "doc_id": doc_id,
        "category": category,
        "source_url": "https://example.org/sample.pdf",
        "source_license_note": "public sample",
        "selected_pages": [1, 2],
        "split": "active" if active else "reserve",
        "local_pdf_path": "data/pdfs/rechnung_001.pdf",
        "sha256": None,
    }


def test_validate_manifest_accepts_expected_categories_and_active_split(tmp_path):
    path = tmp_path / "dataset_manifest.json"
    docs = [_entry()]
    path.write_text(json.dumps({"documents": docs}), encoding="utf-8")

    result = validate_manifest(path)

    assert result.documents[0].doc_id == "rechnung_001"
    assert result.active_counts["rechnungen"] == 1
    assert set(ACTIVE_CATEGORIES) >= {"rechnungen", "vertraege", "medizin"}


def test_validate_manifest_rejects_unknown_category(tmp_path):
    path = tmp_path / "dataset_manifest.json"
    path.write_text(json.dumps({"documents": [_entry(category="misc")]}), encoding="utf-8")

    with pytest.raises(ManifestError, match="unknown category"):
        validate_manifest(path)


def test_validate_manifest_rejects_duplicate_doc_ids(tmp_path):
    path = tmp_path / "dataset_manifest.json"
    path.write_text(
        json.dumps({"documents": [_entry(), _entry(doc_id="rechnung_001")]}),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="duplicate doc_id"):
        validate_manifest(path)
