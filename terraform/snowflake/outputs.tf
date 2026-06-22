output "warehouse_name" {
  value = snowflake_warehouse.ekp.name
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
