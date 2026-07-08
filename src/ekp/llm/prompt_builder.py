from collections.abc import Iterable, Mapping
from typing import Any


def build_rag_prompt(question: str, chunks: Iterable[Mapping[str, Any] | Any]) -> str:
    """Build a RAG prompt that answers strictly from numbered context sources."""
    context = _build_context(chunks)

    return f"""You are an assistant answering questions using only the provided context.

Rules:
- Use only facts present in the context below.
- If the context does not contain enough information, say that you do not know based on the provided context.
- Do not use outside knowledge.
- Cite the numbered source(s) you used, for example [1] or [1], [2].

Context:
{context}

Question:
{question.strip()}

Answer:"""


def _build_context(chunks: Iterable[Mapping[str, Any] | Any]) -> str:
    context_parts: list[str] = []

    for chunk in chunks:
        text = str(_get_value(chunk, "chunk_text", "")).strip()
        if not text:
            continue

        source_number = len(context_parts) + 1
        source_label = _source_label(chunk)
        context_parts.append(f"[{source_number}] {source_label}\n{text}")

    if not context_parts:
        return "No context provided."

    return "\n\n".join(context_parts)


def _source_label(chunk: Mapping[str, Any] | Any) -> str:
    source_uri = _get_value(chunk, "source_uri")
    document_name = _get_value(chunk, "document_name")
    document_id = _get_value(chunk, "document_id")
    chunk_index = _get_value(chunk, "chunk_index")

    source = source_uri or document_name or document_id or "unknown source"
    if chunk_index is None:
        return f"Source: {source}"

    return f"Source: {source}, chunk: {chunk_index}"


def _get_value(
    chunk: Mapping[str, Any] | Any,
    key: str,
    default: Any = None,
) -> Any:
    if isinstance(chunk, Mapping):
        return chunk.get(key, default)

    return getattr(chunk, key, default)
