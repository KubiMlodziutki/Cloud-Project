resource "snowflake_database" "ekp" {
  name = var.database_name
}

resource "snowflake_schema" "rag" {
  database = snowflake_database.ekp.name
  name     = var.schema_name
}