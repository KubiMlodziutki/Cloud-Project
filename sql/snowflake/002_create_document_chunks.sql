USE DATABASE EKP_DB;
USE SCHEMA RAG;

CREATE OR REPLACE TABLE document_chunks (
    chunk_id STRING NOT NULL,
    document_id STRING NOT NULL,
    source_uri STRING,
    chunk_index NUMBER(38, 0) NOT NULL,
    chunk_text STRING NOT NULL,
    metadata VARIANT,
    embedding VECTOR(FLOAT, 384) NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
