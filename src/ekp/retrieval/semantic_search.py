import json
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

import snowflake.connector

from ekp.storage.snowflake import _validate_identifier, snowflake_connection_options

if TYPE_CHECKING:
    from ekp.embeddings.embedder import EmbeddingModel


class SemanticSearchService:
    def __init__(
        self,
        embedder: "EmbeddingModel | None" = None,
        table_name: str = "document_chunks",
        embedding_dimensions: int = 384,
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        if embedder is None:
            from ekp.embeddings.embedder import EmbeddingModel

            embedder = EmbeddingModel()

        self.embedder = embedder
        self.table_name = _validate_identifier(table_name)
        self.embedding_dimensions = embedding_dimensions
        self.connection_factory = connection_factory or snowflake.connector.connect

    def search(self, question: str, top_k: int = 10) -> list[dict[str, Any]]:
        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        query_embedding = self.embedder.encode_texts([question])[0]
        query_embedding_json = json.dumps(list(query_embedding))

        sql = f"""
            WITH query_vector AS (
                SELECT PARSE_JSON(%s)::VECTOR(FLOAT, {self.embedding_dimensions}) AS embedding
            )
            SELECT
                dc.chunk_id,
                dc.document_id,
                dc.source_uri,
                dc.chunk_index,
                dc.chunk_text,
                dc.metadata,
                VECTOR_COSINE_SIMILARITY(dc.embedding, q.embedding) AS similarity
            FROM {self.table_name} AS dc
            CROSS JOIN query_vector AS q
            ORDER BY similarity DESC
            LIMIT %s
        """

        with self.connection_factory(**snowflake_connection_options()) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (query_embedding_json, top_k))
                columns = [column[0].lower() for column in cursor.description]
                return [
                    self._normalize_row(dict(zip(columns, row, strict=True)))
                    for row in cursor.fetchall()
                ]

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        metadata = row.get("metadata")
        if isinstance(metadata, str):
            try:
                row["metadata"] = json.loads(metadata)
            except json.JSONDecodeError:
                pass
        elif metadata is None:
            row["metadata"] = {}
        elif not isinstance(metadata, Mapping):
            row["metadata"] = dict(metadata)

        return row
