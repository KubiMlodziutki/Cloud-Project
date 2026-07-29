output "warehouse_name" {
  value = snowflake_warehouse.ekp.name
}

output "warehouse_resource_monitor_name" {
  value = snowflake_resource_monitor.ekp.name
}

output "database_name" {
  value = snowflake_database.ekp.name
}

output "schema_name" {
  value = snowflake_schema.rag.name
}

output "role_name" {
  value = snowflake_account_role.ekp.name
}

output "staging_table_name" {
  value = snowflake_table.raw_document_chunks_stg.fully_qualified_name
}

output "document_chunks_table_name" {
  value = snowflake_table.document_chunks.fully_qualified_name
}
