from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Cloud credentials are not used locally, but Settings validates them at import time.
os.environ.setdefault("S3_BUCKET_NAME", "local-unused")
os.environ.setdefault("SNOWFLAKE_ACCOUNT", "local-unused")
os.environ.setdefault("SNOWFLAKE_USER", "local-unused")
os.environ.setdefault("SNOWFLAKE_PASSWORD", "local-unused")

from ekp.embeddings.embedder import EmbeddingModel  # noqa: E402
from ekp.llm.prompt_builder import build_rag_prompt  # noqa: E402
from ekp.local.pipeline import LocalSemanticSearch, load_local_chunks  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the complete RAG retrieval pipeline locally.")
    parser.add_argument("question", nargs="?", help="Question to search for")
    parser.add_argument("--docs", type=Path, default=ROOT / "data" / "sample_docs")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    parser.add_argument("--model", help="Sentence Transformers model name")
    parser.add_argument("--ollama", action="store_true", help="Also generate an answer with local Ollama")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    question = args.question or input("Pytanie: ").strip()

    print(f"Wczytywanie dokumentow z: {args.docs}")
    chunks = load_local_chunks(args.docs, args.chunk_size, args.overlap)
    print(f"Utworzono {len(chunks)} fragmentow. Generowanie embeddingow...")

    embedder = EmbeddingModel(model_name=args.model)
    search = LocalSemanticSearch(chunks, embedder)
    results = search.search(question, args.top_k)

    print("\nNajlepiej dopasowane fragmenty:")
    for number, result in enumerate(results, start=1):
        preview = result["chunk_text"].replace("\n", " ")[:300]
        print(
            f"\n[{number}] {result['document_name']}, strona {result['page_number']}, "
            f"podobienstwo {result['similarity']:.4f}\n{preview}"
        )

    if args.ollama:
        print("\nOdpowiedz Ollama:\n")
        print(_ask_ollama(build_rag_prompt(question, results)))


def _ask_ollama(prompt: str) -> str:
    import requests

    from ekp.config import settings

    try:
        response = requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Start Ollama and download the model "
            f"with the command: ollama pull {settings.ollama_model}"
        ) from error
    return str(response.json()["response"]).strip()


if __name__ == "__main__":
    main()

