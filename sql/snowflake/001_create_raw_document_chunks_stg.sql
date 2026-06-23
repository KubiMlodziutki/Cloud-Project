USE DATABASE EKP_DB;
USE SCHEMA RAG;

CREATE OR REPLACE TABLE raw_document_chunks_stg (
    document_id STRING NOT NULL,
    source_uri STRING,
    chunk_index NUMBER(38, 0) NOT NULL,
    chunk_text STRING NOT NULL,
    metadata VARIANT,
    embedding ARRAY NOT NULL,
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
