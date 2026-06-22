variable "snowflake_account" {
  description = "Snowflake account identifier (for example orgname-account_name)."
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake user used by Terraform."
  type        = string
}

variable "snowflake_password" {
  description = "Password for the Snowflake Terraform user. Prefer TF_VAR_snowflake_password."
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "Administrative role used to provision objects and grants."
  type        = string
  default     = "ACCOUNTADMIN"
}

variable "warehouse_name" {
  description = "Name of the EKP warehouse."
  type        = string
  default     = "EKP_WH"
}

variable "database_name" {
  description = "Name of the EKP database."
  type        = string
  default     = "EKP_DB"
}

variable "schema_name" {
  description = "Name of the RAG schema."
  type        = string
  default     = "RAG"
}

variable "ekp_role_name" {
  description = "Name of the application account role."
  type        = string
  default     = "EKP_ROLE"
}
