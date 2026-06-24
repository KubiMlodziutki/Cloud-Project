locals {
  ingestion_tasks = {
    parse = {
      python_file = "${var.job_source_path}/parse.py"
      parameters  = var.parse_parameters
    }
    chunk = {
      python_file = "${var.job_source_path}/chunk.py"
      parameters  = var.chunk_parameters
      depends_on  = "parse"
    }
    embeddings = {
      python_file = "${var.job_source_path}/embeddings.py"
      parameters  = var.embeddings_parameters
      depends_on  = "chunk"
    }
    load_to_snowflake = {
      python_file = "${var.job_source_path}/load_to_snowflake.py"
      parameters  = var.load_to_snowflake_parameters
      depends_on  = "embeddings"
    }
  }
}

resource "databricks_job" "ekp_rag_ingestion_pipeline" {
  name                = var.job_name
  max_concurrent_runs = 1

  task {
    task_key           = "parse"
    existing_cluster_id = databricks_cluster.dev_single_node.id

    spark_python_task {
      python_file = local.ingestion_tasks.parse.python_file
      parameters  = local.ingestion_tasks.parse.parameters
    }
  }

  task {
    task_key           = "chunk"
    existing_cluster_id = databricks_cluster.dev_single_node.id

    depends_on {
      task_key = local.ingestion_tasks.chunk.depends_on
    }

    spark_python_task {
      python_file = local.ingestion_tasks.chunk.python_file
      parameters  = local.ingestion_tasks.chunk.parameters
    }
  }

  task {
    task_key           = "embeddings"
    existing_cluster_id = databricks_cluster.dev_single_node.id

    depends_on {
      task_key = local.ingestion_tasks.embeddings.depends_on
    }

    spark_python_task {
      python_file = local.ingestion_tasks.embeddings.python_file
      parameters  = local.ingestion_tasks.embeddings.parameters
    }
  }

  task {
    task_key           = "load_to_snowflake"
    existing_cluster_id = databricks_cluster.dev_single_node.id

    depends_on {
      task_key = local.ingestion_tasks.load_to_snowflake.depends_on
    }

    spark_python_task {
      python_file = local.ingestion_tasks.load_to_snowflake.python_file
      parameters  = local.ingestion_tasks.load_to_snowflake.parameters
    }
  }
}
