from __future__ import annotations

import math
from dataclasses import asdict
from pathlib import Path
from typing import Protocol

from ekp.parsing.parsers import parse_document
from ekp.processing.chunking import DocumentChunk, chunk_text


SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm", ".md", ".markdown"}


class Embedder(Protocol):
    def encode_texts(self, texts: list[str]) -> list[list[float]]: ...


def load_local_chunks(
    documents_dir: str | Path,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[DocumentChunk]:
    documents_path = Path(documents_dir)
    if not documents_path.is_dir():
        raise FileNotFoundError(f"Documents directory does not exist: {documents_path}")

    chunks: list[DocumentChunk] = []
    for path in sorted(documents_path.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        for page in parse_document(path):
            chunks.extend(
                chunk_text(
                    document_name=page.document_name,
                    page_number=page.page_number,
                    text=page.text,
                    chunk_size=chunk_size,
                    overlap=overlap,
                )
            )

    if not chunks:
        raise ValueError(f"No text chunks were generated from {documents_path}")
    return chunks


class LocalSemanticSearch:
    def __init__(self, chunks: list[DocumentChunk], embedder: Embedder) -> None:
        if not chunks:
            raise ValueError("At least one chunk is required")
        self.chunks = chunks
        self.embedder = embedder
        self.embeddings = embedder.encode_texts([chunk.chunk_text for chunk in chunks])
        if len(self.embeddings) != len(chunks):
            raise ValueError("Embedder returned an unexpected number of embeddings")

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        if not question.strip():
            raise ValueError("Question must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        query_embedding = self.embedder.encode_texts([question])[0]
        scored = [
            (_cosine_similarity(query_embedding, embedding), chunk)
            for chunk, embedding in zip(self.chunks, self.embeddings, strict=True)
        ]
        scored.sort(key=lambda item: item[0], reverse=True)

        results = []
        for similarity, chunk in scored[:top_k]:
            result = asdict(chunk)
            result["similarity"] = similarity
            result["source_uri"] = chunk.document_name
            results.append(result)
        return results


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions do not match")
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)

