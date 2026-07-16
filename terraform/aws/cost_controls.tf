resource "aws_budgets_budget" "monthly_cost" {
  name         = "${var.project_name}-${var.environment}-monthly-cost"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 10
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.billing_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 50
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.billing_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.billing_alert_email]
  }
}

resource "aws_sns_topic" "cost_alerts" {
  name = "${var.project_name}-${var.environment}-cost-alerts"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "cost_alert_email" {
  topic_arn = aws_sns_topic.cost_alerts.arn
  protocol  = "email"
  endpoint  = var.billing_alert_email
}

resource "aws_s3_bucket_metric" "documents_requests" {
  bucket = aws_s3_bucket.documents.id
  name   = "EntireBucket"
}

resource "aws_cloudwatch_metric_alarm" "excessive_s3_gets" {
  alarm_name          = "${var.project_name}-${var.environment}-excessive-s3-gets"
  alarm_description   = "S3 GET request volume exceeded the configured five-minute safety threshold. Investigate the caller immediately."
  namespace           = "AWS/S3"
  metric_name         = "GetRequests"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = var.s3_get_alarm_threshold
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.cost_alerts.arn]

  dimensions = {
    BucketName = aws_s3_bucket.documents.id
    FilterId   = aws_s3_bucket_metric.documents_requests.name
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}
