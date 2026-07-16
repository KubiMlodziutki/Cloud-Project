variable "aws_region" {
  type    = string
  default = "eu-central-1"
}

variable "project_name" {
  type    = string
  default = "enterprise-knowledge-platform"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "bucket_name" {
  type = string
}

variable "billing_alert_email" {
  description = "Email address that receives AWS budget and S3 request-volume alerts. The SNS subscription must be confirmed."
  type        = string

  validation {
    condition     = can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.billing_alert_email))
    error_message = "billing_alert_email must be a valid email address."
  }
}

variable "monthly_budget_usd" {
  description = "Monthly account-level AWS cost budget in USD. This sends alerts; it is not a hard spending cap."
  type        = number
  default     = 4

  validation {
    condition     = var.monthly_budget_usd > 0
    error_message = "monthly_budget_usd must be greater than zero."
  }
}

variable "s3_get_alarm_threshold" {
  description = "Number of S3 GET requests in five minutes that triggers an alert."
  type        = number
  default     = 30

  validation {
    condition     = var.s3_get_alarm_threshold > 0
    error_message = "s3_get_alarm_threshold must be greater than zero."
  }
}
