resource "snowflake_account_role" "ekp" {
  name    = var.ekp_role_name
  comment = "Role used by the EKP application"
}

# Make EKP_ROLE manageable by the standard administrative role hierarchy.
resource "snowflake_grant_account_role" "ekp_to_sysadmin" {
  role_name        = snowflake_account_role.ekp.name
  parent_role_name = "SYSADMIN"
}

resource "snowflake_grant_privileges_to_account_role" "warehouse" {
  account_role_name = snowflake_account_role.ekp.name
  privileges        = ["USAGE", "OPERATE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.ekp.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "database" {
  account_role_name = snowflake_account_role.ekp.name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.ekp.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "schema" {
  account_role_name = snowflake_account_role.ekp.name
  privileges        = ["USAGE", "CREATE TABLE", "CREATE STAGE"]

  on_schema {
    schema_name = "${snowflake_database.ekp.name}.${snowflake_schema.rag.name}"
  }
}

resource "snowflake_grant_privileges_to_account_role" "future_tables" {
  account_role_name = snowflake_account_role.ekp.name
  privileges        = ["SELECT"]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = "${snowflake_database.ekp.name}.${snowflake_schema.rag.name}"
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "staging_table" {
  account_role_name = snowflake_account_role.ekp.name
  privileges        = ["SELECT", "INSERT", "TRUNCATE"]

  on_schema_object {
    object_type = "TABLE"
    object_name = snowflake_table.raw_document_chunks_stg.fully_qualified_name
  }
}

resource "snowflake_grant_privileges_to_account_role" "document_chunks_table" {
  account_role_name = snowflake_account_role.ekp.name
  privileges        = ["SELECT", "INSERT", "TRUNCATE"]

  on_schema_object {
    object_type = "TABLE"
    object_name = snowflake_table.document_chunks.fully_qualified_name
  }
}
