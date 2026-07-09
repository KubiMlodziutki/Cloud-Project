import pytest

from ekp.processing.chunking import chunk_text, normalize_text


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("  alpha\n\n beta\tgamma  ") == "alpha beta gamma"


def test_chunk_text_creates_ordered_overlapping_chunks() -> None:
    chunks = chunk_text(
        document_name="guide.md",
        page_number=1,
        text="alpha beta gamma delta epsilon zeta eta theta",
        chunk_size=24,
        overlap=6,
    )

    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert chunks[0].document_name == "guide.md"
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_text == "alpha beta gamma delta"
    assert chunks[1].chunk_text.startswith("delta")
    assert all(chunk.chunk_id for chunk in chunks)


@pytest.mark.parametrize(
    ("chunk_size", "overlap", "message"),
    [
        (0, 0, "chunk_size must be greater than 0"),
        (10, -1, "overlap must be greater than or equal to 0"),
        (10, 10, "overlap must be smaller than chunk_size"),
    ],
)
def test_chunk_text_rejects_invalid_sizes(
    chunk_size: int,
    overlap: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        chunk_text("guide.md", 1, "hello world", chunk_size=chunk_size, overlap=overlap)
