resource "snowflake_resource_monitor" "ekp" {
  name                      = "${var.warehouse_name}_MONTHLY_LIMIT"
  credit_quota              = var.warehouse_monthly_credit_quota
  frequency                 = "MONTHLY"
  start_timestamp           = "IMMEDIATELY"
  notify_triggers           = var.warehouse_credit_notify_triggers
  suspend_immediate_trigger = var.warehouse_credit_suspend_immediate_trigger
}

resource "snowflake_warehouse" "ekp" {
  name                = var.warehouse_name
  warehouse_size      = "XSMALL"
  auto_suspend        = 60
  auto_resume         = true
  initially_suspended = true
  resource_monitor    = snowflake_resource_monitor.ekp.fully_qualified_name
}
