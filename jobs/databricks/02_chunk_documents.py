import argparse
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType


def add_project_src_to_path() -> None:
    for parent in Path(__file__).resolve().parents:
        src_dir = parent / "src"
        if src_dir.exists():
            sys.path.insert(0, str(src_dir))
            return


add_project_src_to_path()

from ekp.processing.chunking import chunk_text  # noqa: E402


DEFAULT_PARSED_PREFIX = "bronze/parsed/"
DEFAULT_CHUNKS_PREFIX = "silver/chunks/"


def build_s3_path(bucket_name: str, prefix: str) -> str:
    normalized_prefix = prefix.strip("/")
    return f"s3://{bucket_name}/{normalized_prefix}/"


def default_bucket_name() -> str:
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if bucket_name:
        return bucket_name

    from ekp.config import settings

    return settings.s3_bucket_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chunk parsed document pages from bronze and write chunks to silver."
    )
    parser.add_argument(
        "--input-path",
        default=None,
        help="Input S3 path with parsed pages. Defaults to s3://<bucket>/bronze/parsed/.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Output S3 path for chunks. Defaults to s3://<bucket>/silver/chunks/.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Maximum chunk size passed to ekp.processing.chunking.chunk_text.",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=50,
        help="Chunk overlap passed to ekp.processing.chunking.chunk_text.",
    )
    parser.add_argument(
        "--mode",
        choices=("overwrite", "append"),
        default="overwrite",
        help="Spark write mode for the chunks layer.",
    )
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[str, str]:
    if args.input_path and args.output_path:
        return args.input_path, args.output_path

    bucket_name = default_bucket_name()
    input_path = args.input_path or build_s3_path(bucket_name, DEFAULT_PARSED_PREFIX)
    output_path = args.output_path or build_s3_path(bucket_name, DEFAULT_CHUNKS_PREFIX)
    return input_path, output_path


def chunks_schema() -> StructType:
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
        ]
    )


def chunk_rows_from_parsed_pages(
    spark: SparkSession,
    input_path: str,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    parsed_rows = spark.read.parquet(input_path).collect()
    chunked_at = datetime.now(timezone.utc).isoformat()
    output_rows: list[dict] = []

    for row in parsed_rows:
        for chunk in chunk_text(
            document_name=row["document_name"],
            page_number=row["page_number"],
            text=row["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        ):
            chunk_row = asdict(chunk)
            chunk_row["document_type"] = row["document_type"]
            chunk_row["source_path"] = row["source_path"]
            chunk_row["parsed_at"] = row["parsed_at"]
            chunk_row["chunked_at"] = chunked_at
            output_rows.append(chunk_row)

    return output_rows


def main() -> None:
    args = parse_args()
    input_path, output_path = resolve_paths(args)

    spark = SparkSession.builder.appName("ekp-chunk-documents").getOrCreate()
    chunk_rows = chunk_rows_from_parsed_pages(
        spark=spark,
        input_path=input_path,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    if not chunk_rows:
        raise ValueError(f"No chunks were generated from {input_path}")

    chunks_df = spark.createDataFrame(chunk_rows, schema=chunks_schema())
    chunks_df.write.parquet(output_path, mode=args.mode)

    print(
        f"Wrote {chunks_df.count()} chunk(s) from {input_path} "
        f"to {output_path} as parquet."
    )


if __name__ == "__main__":
    main()
