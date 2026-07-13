from pathlib import Path

import pytest

from ekp.local.pipeline import LocalSemanticSearch, load_local_chunks
from ekp.processing.chunking import DocumentChunk


class FakeEmbedder:
    def encode_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float("backup" in text.lower()), float("iam" in text.lower())] for text in texts]


def test_load_local_chunks_parses_supported_documents(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_text("# Backup\nKeep three backup copies.", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignored", encoding="utf-8")

    chunks = load_local_chunks(tmp_path, chunk_size=100, overlap=10)

    assert len(chunks) == 1
    assert chunks[0].document_name == "guide.md"
    assert "three backup copies" in chunks[0].chunk_text


def test_local_search_orders_chunks_by_cosine_similarity() -> None:
    chunks = [
        DocumentChunk("1", "iam.md", 1, 0, "Use IAM roles."),
        DocumentChunk("2", "backup.md", 1, 0, "Create a backup every day."),
    ]
    search = LocalSemanticSearch(chunks, FakeEmbedder())

    results = search.search("How should I make a backup?", top_k=1)

    assert results[0]["document_name"] == "backup.md"
    assert results[0]["similarity"] == pytest.approx(1.0)

