terraform {
  required_version = ">= 1.6.0"

  required_providers {
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 2.17"
    }
  }
}

provider "snowflake" {
  organization_name        = var.snowflake_organization_name
  account_name             = var.snowflake_account_name
  user                     = var.snowflake_user
  password                 = var.snowflake_password
  role                     = var.snowflake_role
  preview_features_enabled = ["snowflake_table_resource"]
}
