USE DATABASE EKP_DB;
USE SCHEMA RAG;

INSERT INTO document_chunks (
    chunk_id,
    document_id,
    source_uri,
    chunk_index,
    chunk_text,
    metadata,
    embedding
)
SELECT
    SHA2(CONCAT_WS('|', document_id, source_uri, chunk_index::STRING, chunk_text), 256) AS chunk_id,
    document_id,
    source_uri,
    chunk_index,
    chunk_text,
    metadata,
    embedding::VECTOR(FLOAT, 384) AS embedding
FROM raw_document_chunks_stg
WHERE ARRAY_SIZE(embedding) = 384;
