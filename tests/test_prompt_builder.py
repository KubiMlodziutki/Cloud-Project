from dataclasses import dataclass

from ekp.llm.prompt_builder import build_rag_prompt


@dataclass
class ChunkObject:
    chunk_text: str
    document_name: str
    chunk_index: int


def test_build_rag_prompt_numbers_context_and_sources() -> None:
    prompt = build_rag_prompt(
        question="  What secures the bucket?  ",
        chunks=[
            {
                "chunk_text": "Use least privilege IAM policies.",
                "source_uri": "s3://docs/security.md",
                "chunk_index": 3,
            },
            ChunkObject(
                chunk_text="Enable server-side encryption.",
                document_name="storage.md",
                chunk_index=4,
            ),
            {"chunk_text": "   "},
        ],
    )

    assert "[1] Source: s3://docs/security.md, chunk: 3" in prompt
    assert "[2] Source: storage.md, chunk: 4" in prompt
    assert "Use least privilege IAM policies." in prompt
    assert "Question:\nWhat secures the bucket?" in prompt
    assert "Use only facts present in the context below." in prompt


def test_build_rag_prompt_handles_empty_context() -> None:
    prompt = build_rag_prompt("What is available?", [])

    assert "No context provided." in prompt


def test_build_rag_prompt_skips_blank_and_none_chunks_without_numbering_gaps() -> None:
    prompt = build_rag_prompt(
        "What is available?",
        [
            {"chunk_text": None, "source_uri": "ignored-none.md"},
            {"chunk_text": "   ", "source_uri": "ignored-blank.md"},
            {"chunk_text": "Useful context.", "document_id": "doc-123"},
        ],
    )

    assert "[1] Source: doc-123" in prompt
    assert "\n[2] Source:" not in prompt
    assert "ignored-none.md" not in prompt
    assert "ignored-blank.md" not in prompt


def test_build_rag_prompt_uses_getattr_defaults_for_partial_objects() -> None:
    @dataclass
    class PartialChunk:
        chunk_text: str

    prompt = build_rag_prompt("What is available?", [PartialChunk("Object context.")])

    assert "[1] Source: unknown source" in prompt
    assert "chunk:" not in prompt
    assert "Object context." in prompt


def test_build_rag_prompt_prefers_source_uri_over_other_identifiers() -> None:
    prompt = build_rag_prompt(
        "What is available?",
        [
            {
                "chunk_text": "Mapped context.",
                "source_uri": "s3://bucket/source.md",
                "document_name": "fallback-name.md",
                "document_id": "fallback-id",
                "chunk_index": 0,
            }
        ],
    )

    assert "Source: s3://bucket/source.md, chunk: 0" in prompt
    assert "fallback-name.md" not in prompt
    assert "fallback-id" not in prompt
