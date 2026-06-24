data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

data "databricks_node_type" "smallest" {
  local_disk = true
}

resource "databricks_cluster" "dev_single_node" {
  cluster_name            = var.cluster_name
  spark_version           = coalesce(var.spark_version, data.databricks_spark_version.latest_lts.id)
  node_type_id            = coalesce(var.node_type_id, data.databricks_node_type.smallest.id)
  autotermination_minutes = 20
  is_single_node          = true
  kind                    = "CLASSIC_PREVIEW"

  custom_tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
