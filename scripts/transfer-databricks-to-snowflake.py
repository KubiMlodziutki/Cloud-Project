from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ekp.storage.snowflake import (  # noqa: E402
    insert_document_vectors_from_staging,
    load_document_chunks_staging,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load a downloaded Databricks gold Parquet export into Snowflake."
    )
    parser.add_argument(
        "export_path",
        type=Path,
        help="Parquet file or directory downloaded from the Databricks gold volume path.",
    )
    parser.add_argument("--expected-document", help="Fail unless this document is present.")
    parser.add_argument("--append", action="store_true", help="Do not truncate target tables.")
    return parser.parse_args()


def load_export_rows(export_path: Path) -> list[dict]:
    if not export_path.exists():
        raise FileNotFoundError(f"Databricks export does not exist: {export_path}")

    frame = pd.read_parquet(export_path)
    required = {
        "chunk_id", "document_name", "document_type", "page_number", "chunk_index",
        "chunk_text", "source_path", "parsed_at", "chunked_at", "embedded_at", "embedding",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Databricks export is missing columns: {sorted(missing)}")

    rows: list[dict] = []
    for record in frame.to_dict(orient="records"):
        embedding = [float(value) for value in record["embedding"]]
        if len(embedding) != 384:
            raise ValueError(
                f"Chunk {record['chunk_id']} has {len(embedding)} dimensions; expected 384"
            )
        metadata = json.dumps(
            {
                "chunk_id": record["chunk_id"],
                "document_type": record["document_type"],
                "page_number": int(record["page_number"]),
                "parsed_at": record["parsed_at"],
                "chunked_at": record["chunked_at"],
                "embedded_at": record["embedded_at"],
            }
        )
        rows.append(
            {
                "document_id": record["document_name"],
                "source_uri": record["source_path"],
                "chunk_index": int(record["chunk_index"]),
                "chunk_text": record["chunk_text"],
                "metadata": metadata,
                "embedding": embedding,
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    rows = load_export_rows(args.export_path)
    if not rows:
        raise ValueError("Databricks export contains no chunks")
    if args.expected_document and not any(
        row["document_id"] == args.expected_document for row in rows
    ):
        raise ValueError(f"Expected document is absent: {args.expected_document}")

    load_document_chunks_staging(rows, truncate=not args.append)
    insert_document_vectors_from_staging(truncate=not args.append)
    print(f"Transferred {len(rows)} chunks from Databricks export to Snowflake.")


if __name__ == "__main__":
    main()
