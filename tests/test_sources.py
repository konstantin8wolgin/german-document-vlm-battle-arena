from docarena.sources import curated_documents
from docarena.manifest import ACTIVE_CATEGORIES


def test_curated_documents_have_direct_pdf_urls_and_active_reserve_split():
    docs = curated_documents()

    assert len(docs) >= 40
    for category in ACTIVE_CATEGORIES:
        category_docs = [doc for doc in docs if doc["category"] == category]
        assert len(category_docs) >= 5
        assert sum(doc["split"] == "active" for doc in category_docs) >= 5

    assert all(".pdf" in doc["source_url"].lower() for doc in docs)
    assert all(doc["local_pdf_path"].startswith("data/pdfs/") for doc in docs)
