from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


ACTIVE_CATEGORIES = (
    "rechnungen",
    "vertraege",
    "behoerdenpost",
    "versicherung",
    "bank_finanzen",
    "steuer",
    "medizin",
    "formulare",
)


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class DocumentEntry:
    doc_id: str
    category: str
    source_url: str
    source_license_note: str
    selected_pages: list[int]
    split: str
    local_pdf_path: Path
    sha256: str | None = None


@dataclass(frozen=True)
class DatasetManifest:
    path: Path
    documents: list[DocumentEntry]
    active_counts: dict[str, int]
    reserve_counts: dict[str, int]


def _require_string(raw: dict, key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{key} must be a non-empty string")
    return value


def load_manifest(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_manifest(path: str | Path) -> DatasetManifest:
    manifest_path = Path(path)
    raw = load_manifest(manifest_path)
    raw_documents = raw.get("documents")
    if not isinstance(raw_documents, list):
        raise ManifestError("manifest must contain a documents list")

    seen: set[str] = set()
    documents: list[DocumentEntry] = []
    active = Counter()
    reserve = Counter()

    for index, raw_doc in enumerate(raw_documents):
        if not isinstance(raw_doc, dict):
            raise ManifestError(f"document {index} must be an object")
        doc_id = _require_string(raw_doc, "doc_id")
        if doc_id in seen:
            raise ManifestError(f"duplicate doc_id: {doc_id}")
        seen.add(doc_id)

        category = _require_string(raw_doc, "category")
        if category not in ACTIVE_CATEGORIES:
            raise ManifestError(f"unknown category for {doc_id}: {category}")

        source_url = _require_string(raw_doc, "source_url")
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ManifestError(f"source_url for {doc_id} must be http(s)")

        pages = raw_doc.get("selected_pages")
        if not isinstance(pages, list) or not pages or not all(isinstance(page, int) and page > 0 for page in pages):
            raise ManifestError(f"selected_pages for {doc_id} must be positive integers")

        split = raw_doc.get("split", "reserve")
        if split not in {"active", "reserve"}:
            raise ManifestError(f"split for {doc_id} must be active or reserve")
        if split == "active":
            active[category] += 1
        else:
            reserve[category] += 1

        documents.append(
            DocumentEntry(
                doc_id=doc_id,
                category=category,
                source_url=source_url,
                source_license_note=_require_string(raw_doc, "source_license_note"),
                selected_pages=list(pages),
                split=split,
                local_pdf_path=Path(_require_string(raw_doc, "local_pdf_path")),
                sha256=raw_doc.get("sha256"),
            )
        )

    return DatasetManifest(
        path=manifest_path,
        documents=documents,
        active_counts=dict(active),
        reserve_counts=dict(reserve),
    )


def write_default_manifest(path: str | Path) -> None:
    target = Path(path)
    if target.exists():
        return
    from .sources import curated_documents

    docs = curated_documents()
    target.write_text(json.dumps({"documents": docs}, indent=2) + "\n", encoding="utf-8")
