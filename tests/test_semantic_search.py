import json

import pytest

from ekp.retrieval.semantic_search import SemanticSearchService
from ekp.storage.snowflake import _validate_identifier


class FakeEmbedder:
    def encode_texts(self, texts: list[str]) -> list[list[float]]:
        assert texts == ["How do I secure S3?"]
        return [[0.1, 0.2, 0.3]]


class FakeCursor:
    description = [
        ("CHUNK_ID",),
        ("DOCUMENT_ID",),
        ("SOURCE_URI",),
        ("CHUNK_INDEX",),
        ("CHUNK_TEXT",),
        ("METADATA",),
        ("SIMILARITY",),
    ]

    def __init__(self) -> None:
        self.executed_sql = ""
        self.executed_params = ()

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[str, int]) -> None:
        self.executed_sql = sql
        self.executed_params = params

    def fetchall(self) -> list[tuple[object, ...]]:
        return [
            (
                "chunk-1",
                "doc-1",
                "s3://docs/security.md",
                0,
                "Use IAM least privilege.",
                '{"topic": "security"}',
                0.98,
            )
        ]


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self._cursor = cursor

    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return self._cursor


def test_semantic_search_builds_query_and_normalizes_rows() -> None:
    cursor = FakeCursor()

    def connect(**_options: object) -> FakeConnection:
        return FakeConnection(cursor)

    service = SemanticSearchService(
        embedder=FakeEmbedder(),
        table_name="document_chunks",
        embedding_dimensions=3,
        connection_factory=connect,
    )

    results = service.search("How do I secure S3?", top_k=5)

    assert "VECTOR(FLOAT, 3)" in cursor.executed_sql
    assert "FROM document_chunks AS dc" in cursor.executed_sql
    assert json.loads(cursor.executed_params[0]) == [0.1, 0.2, 0.3]
    assert cursor.executed_params[1] == 5
    assert results == [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "source_uri": "s3://docs/security.md",
            "chunk_index": 0,
            "chunk_text": "Use IAM least privilege.",
            "metadata": {"topic": "security"},
            "similarity": 0.98,
        }
    ]


def test_semantic_search_rejects_invalid_top_k() -> None:
    service = SemanticSearchService(
        embedder=FakeEmbedder(),
        connection_factory=lambda **_options: FakeConnection(FakeCursor()),
    )

    with pytest.raises(ValueError, match="top_k must be greater than 0"):
        service.search("question", top_k=0)


@pytest.mark.parametrize(
    "identifier",
    ["document_chunks", "RAG.document_chunks", "EKP_DB.RAG.document_chunks"],
)
def test_validate_identifier_accepts_safe_snowflake_names(identifier: str) -> None:
    assert _validate_identifier(identifier) == identifier


@pytest.mark.parametrize(
    "identifier",
    ["document-chunks", "document_chunks; DROP TABLE x", "1document_chunks"],
)
def test_validate_identifier_rejects_unsafe_snowflake_names(identifier: str) -> None:
    with pytest.raises(ValueError, match="Invalid Snowflake identifier"):
        _validate_identifier(identifier)
