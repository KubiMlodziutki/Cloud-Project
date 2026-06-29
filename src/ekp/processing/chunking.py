from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_name: str
    page_number: int
    chunk_index: int
    chunk_text: str


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def chunk_text(
    document_name: str,
    page_number: int,
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[DocumentChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized_text = normalize_text(text)
    if not normalized_text:
        return []

    chunks: list[DocumentChunk] = []
    start = 0

    while start < len(normalized_text):
        end = min(start + chunk_size, len(normalized_text))
        chunk = normalized_text[start:end]

        if end < len(normalized_text):
            split_at = chunk.rfind(" ")
            if split_at > overlap:
                end = start + split_at
                chunk = normalized_text[start:end]

        chunk = chunk.strip()
        if chunk:
            chunk_index = len(chunks)
            chunks.append(
                DocumentChunk(
                    chunk_id=_chunk_id(
                        document_name=document_name,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        text_start=chunk[:100],
                    ),
                    document_name=document_name,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    chunk_text=chunk,
                )
            )

        if end == len(normalized_text):
            break

        next_start = max(end - overlap, 0)
        if next_start <= start:
            next_start = min(start + chunk_size - overlap, len(normalized_text))

        start = next_start
        while start < len(normalized_text) and normalized_text[start].isspace():
            start += 1

    return chunks


def _chunk_id(
    document_name: str,
    page_number: int,
    chunk_index: int,
    text_start: str,
) -> str:
    raw_id = f"{document_name}|{page_number}|{chunk_index}|{text_start}"
    return sha256(raw_id.encode("utf-8")).hexdigest()
