import json
import re
from collections.abc import Mapping, Sequence

import snowflake.connector

from ekp.config import settings


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*(\.[A-Za-z_][A-Za-z0-9_$]*)*$")


def snowflake_connection_options() -> dict:
    return {
        "account": settings.snowflake_account,
        "user": settings.snowflake_user,
        "password": settings.snowflake_password,
        "role": settings.snowflake_role,
        "warehouse": settings.snowflake_warehouse,
        "database": settings.snowflake_database,
        "schema": settings.snowflake_schema,
    }


def load_document_chunks_staging(
    rows: Sequence[Mapping],
    target_table: str = "raw_document_chunks_stg",
    truncate: bool = False,
) -> None:
    safe_target_table = _validate_identifier(target_table)
    insert_sql = f"""
        INSERT INTO {safe_target_table} (
            document_id,
            source_uri,
            chunk_index,
            chunk_text,
            metadata,
            embedding
        )
        SELECT
            %s,
            %s,
            %s,
            %s,
            PARSE_JSON(%s),
            PARSE_JSON(%s)
    """
    values = [
        (
            row["document_id"],
            row["source_uri"],
            row["chunk_index"],
            row["chunk_text"],
            row["metadata"],
            json.dumps(list(row["embedding"])),
        )
        for row in rows
    ]

    with snowflake.connector.connect(**snowflake_connection_options()) as connection:
        with connection.cursor() as cursor:
            if truncate:
                cursor.execute(f"TRUNCATE TABLE {safe_target_table}")
            cursor.executemany(insert_sql, values)


def insert_document_vectors_from_staging(
    source_table: str = "raw_document_chunks_stg",
    target_table: str = "document_chunks",
    embedding_dimensions: int = 384,
) -> None:
    safe_source_table = _validate_identifier(source_table)
    safe_target_table = _validate_identifier(target_table)
    sql = f"""
        INSERT INTO {safe_target_table} (
            chunk_id,
            document_id,
            source_uri,
            chunk_index,
            chunk_text,
            metadata,
            embedding
        )
        SELECT
            SHA2(CONCAT_WS('|', document_id, source_uri, chunk_index::STRING, chunk_text), 256),
            document_id,
            source_uri,
            chunk_index,
            chunk_text,
            metadata,
            embedding::VECTOR(FLOAT, {embedding_dimensions})
        FROM {safe_source_table}
        WHERE ARRAY_SIZE(embedding) = {embedding_dimensions}
    """

    with snowflake.connector.connect(**snowflake_connection_options()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)


def _validate_identifier(identifier: str) -> str:
    if not _IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"Invalid Snowflake identifier: {identifier}")
    return identifier
