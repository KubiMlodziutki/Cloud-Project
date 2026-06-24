variable "databricks_host" {
  description = "Existing Databricks workspace URL, for example https://dbc-xxxxxxxx-xxxx.cloud.databricks.com."
  type        = string
}

variable "databricks_token" {
  description = "Databricks personal access token. Prefer TF_VAR_databricks_token."
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Project tag used on Databricks resources."
  type        = string
  default     = "enterprise-knowledge-platform"
}

variable "environment" {
  description = "Environment tag used on Databricks resources."
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the Databricks single-node development cluster."
  type        = string
  default     = "ekp-dev-single-node"
}

variable "spark_version" {
  description = "Optional Databricks Runtime version. When null, the latest LTS runtime is used."
  type        = string
  default     = null
}

variable "node_type_id" {
  description = "Optional Databricks node type. When null, the provider selects the smallest node type with a local disk."
  type        = string
  default     = null
}

variable "job_name" {
  description = "Name of the RAG ingestion Databricks job."
  type        = string
  default     = "ekp-rag-ingestion-pipeline"
}

variable "job_source_path" {
  description = "Workspace directory containing parse.py, chunk.py, embeddings.py and load_to_snowflake.py."
  type        = string
  default     = "/Workspace/Shared/ekp/jobs"
}

variable "parse_parameters" {
  description = "Parameters passed to parse.py."
  type        = list(string)
  default     = []
}

variable "chunk_parameters" {
  description = "Parameters passed to chunk.py."
  type        = list(string)
  default     = []
}

variable "embeddings_parameters" {
  description = "Parameters passed to embeddings.py."
  type        = list(string)
  default     = []
}

variable "load_to_snowflake_parameters" {
  description = "Parameters passed to load_to_snowflake.py."
  type        = list(string)
  default     = []
}
