import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    ArrayType,
    FloatType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


def add_project_src_to_path() -> None:
    for parent in Path(__file__).resolve().parents:
        src_dir = parent / "src"
        if src_dir.exists():
            sys.path.insert(0, str(src_dir))
            return


add_project_src_to_path()

from ekp.embeddings.embedder import EmbeddingModel  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate embeddings for silver chunks and write gold parquet."
    )
    parser.add_argument(
        "--input-path",
        required=True,
        help="Input chunks directory.",
    )
    parser.add_argument(
        "--output-path",
        required=True,
        help="Output embeddings directory.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Sentence Transformers model name.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Number of chunk texts encoded in one local model batch.",
    )
    parser.add_argument(
        "--mode",
        choices=("overwrite", "append"),
        default="overwrite",
        help="Spark write mode for the embeddings layer.",
    )
    return parser.parse_args()


def embeddings_schema() -> StructType:
    return StructType(
        [
            StructField("chunk_id", StringType(), nullable=False),
            StructField("document_name", StringType(), nullable=False),
            StructField("document_type", StringType(), nullable=False),
            StructField("page_number", IntegerType(), nullable=False),
            StructField("chunk_index", IntegerType(), nullable=False),
            StructField("chunk_text", StringType(), nullable=False),
            StructField("source_path", StringType(), nullable=False),
            StructField("parsed_at", StringType(), nullable=False),
            StructField("chunked_at", StringType(), nullable=False),
            StructField("embedded_at", StringType(), nullable=False),
            StructField("embedding", ArrayType(FloatType()), nullable=False),
        ]
    )


def batched(values: list, batch_size: int) -> list[list]:
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")
    return [values[index : index + batch_size] for index in range(0, len(values), batch_size)]


def embedding_rows_from_chunks(
    spark: SparkSession,
    input_path: str,
    batch_size: int,
    model_name: str | None = None,
) -> list[dict]:
    chunk_rows = [row.asDict() for row in spark.read.parquet(input_path).collect()]
    if not chunk_rows:
        return []

    model = EmbeddingModel(model_name=model_name)
    embedded_at = datetime.now(timezone.utc).isoformat()
    output_rows: list[dict] = []

    for batch in batched(chunk_rows, batch_size):
        texts = [row["chunk_text"] for row in batch]
        embeddings = model.encode_texts(texts)

        for row, embedding in zip(batch, embeddings, strict=True):
            row["embedded_at"] = embedded_at
            row["embedding"] = [float(value) for value in embedding]
            output_rows.append(row)

    return output_rows


def main() -> None:
    args = parse_args()
    input_path, output_path = args.input_path, args.output_path

    spark = SparkSession.builder.appName("ekp-generate-embeddings").getOrCreate()
    embedding_rows = embedding_rows_from_chunks(
        spark=spark,
        input_path=input_path,
        batch_size=args.batch_size,
        model_name=args.model,
    )

    if not embedding_rows:
        raise ValueError(f"No embeddings were generated from {input_path}")

    embeddings_df = spark.createDataFrame(embedding_rows, schema=embeddings_schema())
    embeddings_df.write.parquet(output_path, mode=args.mode)

    print(
        f"Wrote {embeddings_df.count()} embedded chunk(s) from {input_path} "
        f"to {output_path} as parquet."
    )


if __name__ == "__main__":
    main()
