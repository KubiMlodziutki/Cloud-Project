variable "snowflake_organization_name" {
  description = "Snowflake organization name returned by CURRENT_ORGANIZATION_NAME()."
  type        = string
}

variable "snowflake_account_name" {
  description = "Snowflake account name returned by CURRENT_ACCOUNT_NAME(); do not include the organization or hostname."
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

variable "warehouse_monthly_credit_quota" {
  description = "Monthly Snowflake credit quota for the EKP warehouse."
  type        = number
  default     = 1

  validation {
    condition     = var.warehouse_monthly_credit_quota > 0
    error_message = "warehouse_monthly_credit_quota must be greater than zero."
  }
}

variable "warehouse_credit_notify_triggers" {
  description = "Percentages of the monthly warehouse credit quota that send Snowflake notifications."
  type        = set(number)
  default     = [50, 80]

  validation {
    condition     = alltrue([for threshold in var.warehouse_credit_notify_triggers : threshold > 0 && threshold < 90])
    error_message = "Every warehouse credit notification threshold must be greater than 0 and lower than 90."
  }
}

variable "warehouse_credit_suspend_immediate_trigger" {
  description = "Percentage of the monthly credit quota that immediately suspends the warehouse and cancels active statements."
  type        = number
  default     = 90

  validation {
    condition     = var.warehouse_credit_suspend_immediate_trigger > 0 && var.warehouse_credit_suspend_immediate_trigger <= 100
    error_message = "warehouse_credit_suspend_immediate_trigger must be between 1 and 100."
  }
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
