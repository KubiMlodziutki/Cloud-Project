resource "snowflake_table" "raw_document_chunks_stg" {
  database                    = snowflake_database.ekp.name
  schema                      = snowflake_schema.rag.name
  name                        = "RAW_DOCUMENT_CHUNKS_STG"
  comment                     = "Local transfer staging table for Databricks embeddings"
  data_retention_time_in_days = 0

  column {
    name     = "DOCUMENT_ID"
    type     = "VARCHAR"
    nullable = false
  }
  column {
    name = "SOURCE_URI"
    type = "VARCHAR"
  }
  column {
    name     = "CHUNK_INDEX"
    type     = "NUMBER(38,0)"
    nullable = false
  }
  column {
    name     = "CHUNK_TEXT"
    type     = "VARCHAR"
    nullable = false
  }
  column {
    name = "METADATA"
    type = "VARIANT"
  }
  column {
    name     = "EMBEDDING"
    type     = "ARRAY"
    nullable = false
  }
  column {
    name = "LOADED_AT"
    type = "TIMESTAMP_NTZ"
  }
}

resource "snowflake_table" "document_chunks" {
  database                    = snowflake_database.ekp.name
  schema                      = snowflake_schema.rag.name
  name                        = "DOCUMENT_CHUNKS"
  comment                     = "Searchable document chunks with 384-dimensional embeddings"
  data_retention_time_in_days = 0

  column {
    name     = "CHUNK_ID"
    type     = "VARCHAR"
    nullable = false
  }
  column {
    name     = "DOCUMENT_ID"
    type     = "VARCHAR"
    nullable = false
  }
  column {
    name = "SOURCE_URI"
    type = "VARCHAR"
  }
  column {
    name     = "CHUNK_INDEX"
    type     = "NUMBER(38,0)"
    nullable = false
  }
  column {
    name     = "CHUNK_TEXT"
    type     = "VARCHAR"
    nullable = false
  }
  column {
    name = "METADATA"
    type = "VARIANT"
  }
  column {
    name     = "EMBEDDING"
    type     = "VECTOR(FLOAT,384)"
    nullable = false
  }
  column {
    name = "CREATED_AT"
    type = "TIMESTAMP_NTZ"
  }
}
