import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, struct, to_json


def add_project_src_to_path() -> None:
    for parent in Path(__file__).resolve().parents:
        src_dir = parent / "src"
        if src_dir.exists():
            sys.path.insert(0, str(src_dir))
            return


add_project_src_to_path()

from ekp.config import settings  # noqa: E402
from ekp.storage.snowflake import (  # noqa: E402
    insert_document_vectors_from_staging,
    load_document_chunks_staging,
)


DEFAULT_EMBEDDINGS_PREFIX = "gold/embeddings/"
DEFAULT_SNOWFLAKE_READY_PREFIX = "snowflake/document_chunks_stg/"
DEFAULT_TARGET_TABLE = "raw_document_chunks_stg"


def build_s3_path(bucket_name: str, prefix: str) -> str:
    normalized_prefix = prefix.strip("/")
    return f"s3://{bucket_name}/{normalized_prefix}/"


def default_bucket_name() -> str:
    return os.getenv("S3_BUCKET_NAME") or settings.s3_bucket_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare gold embeddings for Snowflake as parquet and load them into "
            "the Snowflake staging table."
        )
    )
    parser.add_argument(
        "--input-path",
        default=None,
        help="Input S3 path with embeddings. Defaults to s3://<bucket>/gold/embeddings/.",
    )
    parser.add_argument(
        "--output-path",
        default=None,
        help=(
            "Output S3 path for Snowflake-ready parquet. Defaults to "
            "s3://<bucket>/snowflake/document_chunks_stg/."
        ),
    )
    parser.add_argument(
        "--target-table",
        default=DEFAULT_TARGET_TABLE,
        help="Snowflake table receiving rows with ARRAY embeddings.",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate the Snowflake target table before inserting rows.",
    )
    parser.add_argument(
        "--insert-vectors",
        action="store_true",
        help="Also insert rows into document_chunks with embedding cast to VECTOR(FLOAT, 384).",
    )
    parser.add_argument(
        "--mode",
        choices=("overwrite", "append"),
        default="overwrite",
        help="Spark write mode for the Snowflake-ready parquet layer.",
    )
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[str, str]:
    if args.input_path and args.output_path:
        return args.input_path, args.output_path

    bucket_name = default_bucket_name()
    input_path = args.input_path or build_s3_path(bucket_name, DEFAULT_EMBEDDINGS_PREFIX)
    output_path = args.output_path or build_s3_path(
        bucket_name,
        DEFAULT_SNOWFLAKE_READY_PREFIX,
    )
    return input_path, output_path


def prepare_snowflake_ready_parquet(
    spark: SparkSession,
    input_path: str,
    output_path: str,
    mode: str,
):
    embeddings_df = spark.read.parquet(input_path)
    loaded_at = datetime.now(timezone.utc).isoformat()

    metadata = to_json(
        struct(
            col("chunk_id"),
            col("document_type"),
            col("page_number"),
            col("parsed_at"),
            col("chunked_at"),
            col("embedded_at"),
        )
    )

    final_df = embeddings_df.select(
        col("document_name").alias("document_id"),
        col("source_path").alias("source_uri"),
        col("chunk_index"),
        col("chunk_text"),
        metadata.alias("metadata"),
        col("embedding"),
    ).withColumn("loaded_at", lit(loaded_at))

    if not final_df.take(1):
        raise ValueError(f"No Snowflake-ready rows were prepared from {input_path}")

    final_df.write.parquet(output_path, mode=mode)
    return final_df


def main() -> None:
    args = parse_args()
    input_path, output_path = resolve_paths(args)

    spark = SparkSession.builder.appName("ekp-load-to-snowflake").getOrCreate()
    final_df = prepare_snowflake_ready_parquet(
        spark=spark,
        input_path=input_path,
        output_path=output_path,
        mode=args.mode,
    )
    rows = [row.asDict() for row in final_df.collect()]

    load_document_chunks_staging(
        rows=rows,
        target_table=args.target_table,
        truncate=args.truncate,
    )
    if args.insert_vectors:
        insert_document_vectors_from_staging(source_table=args.target_table)

    print(
        f"Wrote {len(rows)} Snowflake-ready row(s) from {input_path} to {output_path} "
        f"as parquet and loaded them into {settings.snowflake_database}."
        f"{settings.snowflake_schema}.{args.target_table}."
    )


if __name__ == "__main__":
    main()
