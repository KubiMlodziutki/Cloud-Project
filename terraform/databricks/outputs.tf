output "cluster_id" {
  value = databricks_cluster.dev_single_node.id
}

output "job_id" {
  value = databricks_job.ekp_rag_ingestion_pipeline.id
}
