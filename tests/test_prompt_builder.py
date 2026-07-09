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
