import argparse
import os
import sys
import tempfile
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

from ekp.parsing.parsers import parse_document  # noqa: E402


SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm", ".md", ".markdown"}
DEFAULT_RAW_PREFIX = "raw/documents/"
DEFAULT_PARSED_PREFIX = "bronze/parsed/"


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
        description="Parse raw documents from S3 and write parsed pages to bronze."
    )
    parser.add_argument(
        "--input-path",
        default=None,
        help="Input S3 path with raw documents. Defaults to s3://<bucket>/raw/documents/.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help="Output S3 path for parsed pages. Defaults to s3://<bucket>/bronze/parsed/.",
    )
    parser.add_argument(
        "--output-format",
        choices=("parquet", "delta"),
        default="parquet",
        help="Output storage format.",
    )
    parser.add_argument(
        "--mode",
        choices=("overwrite", "append"),
        default="overwrite",
        help="Spark write mode for the parsed layer.",
    )
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[str, str]:
    if args.input_path and args.output_path:
        return args.input_path, args.output_path

    bucket_name = default_bucket_name()
    input_path = args.input_path or build_s3_path(bucket_name, DEFAULT_RAW_PREFIX)
    output_path = args.output_path or build_s3_path(bucket_name, DEFAULT_PARSED_PREFIX)
    return input_path, output_path


def parsed_pages_from_binary_files(spark: SparkSession, input_path: str) -> list[dict]:
    rows = (
        spark.read.format("binaryFile")
        .option("recursiveFileLookup", "true")
        .load(input_path)
        .select("path", "content")
        .collect()
    )

    parsed_at = datetime.now(timezone.utc).isoformat()
    parsed_rows: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="ekp_parse_") as temp_dir:
        temp_root = Path(temp_dir)

        for row in rows:
            source_path = row["path"]
            suffix = Path(source_path).suffix.lower()
            if suffix not in SUPPORTED_SUFFIXES:
                print(f"Skipping unsupported document: {source_path}")
                continue

            local_path = temp_root / Path(source_path).name
            local_path.write_bytes(bytes(row["content"]))

            for page in parse_document(local_path):
                parsed_row = asdict(page)
                parsed_row["source_path"] = source_path
                parsed_row["parsed_at"] = parsed_at
                parsed_rows.append(parsed_row)

    return parsed_rows


def parsed_pages_schema() -> StructType:
    return StructType(
        [
            StructField("document_name", StringType(), nullable=False),
            StructField("document_type", StringType(), nullable=False),
            StructField("page_number", IntegerType(), nullable=False),
            StructField("text", StringType(), nullable=False),
            StructField("source_path", StringType(), nullable=False),
            StructField("parsed_at", StringType(), nullable=False),
        ]
    )


def main() -> None:
    args = parse_args()
    input_path, output_path = resolve_paths(args)

    spark = SparkSession.builder.appName("ekp-parse-documents").getOrCreate()
    parsed_rows = parsed_pages_from_binary_files(spark, input_path)

    if not parsed_rows:
        raise ValueError(f"No supported documents were parsed from {input_path}")

    parsed_df = spark.createDataFrame(parsed_rows, schema=parsed_pages_schema())
    (
        parsed_df.write.format(args.output_format)
        .mode(args.mode)
        .save(output_path)
    )

    print(
        f"Wrote {parsed_df.count()} parsed page(s) from {input_path} "
        f"to {output_path} as {args.output_format}."
    )


if __name__ == "__main__":
    main()
