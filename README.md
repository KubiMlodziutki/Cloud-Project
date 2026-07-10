# Enterprise Knowledge Platform

## Problem
Companies have thousands of internal documents and employees waste time searching for answers manually.

## Solution
This project implements a RAG-based knowledge platform using AWS S3, Databricks, Snowflake, open-source embeddings and local LLMs.

## Architecture
Documents → S3 → Databricks → Parsing → Chunking → Embeddings → Snowflake → Semantic Search → LLM → Streamlit UI

## Tech Stack
- AWS S3
- Terraform
- Databricks
- Snowflake
- Python
- Sentence Transformers
- Ollama
- Streamlit

## Data Pipeline
Bronze: raw parsed documents
Silver: cleaned chunks
Gold: chunks with embeddings

## Infrastructure
All major cloud resources are provisioned with Terraform.

## Demo
Question: How do I secure access to S3?
Answer: ...
Sources: ...

## Future Improvements
- Snowflake Cortex Search
- Confluence connector
- DOCX parser
- Hybrid search
- Reranking
- CI/CD
- Evaluation dataset

## Local Tests
Install dependencies once:

```powershell
python -m pip install -r requirements.txt
```

Run the local unit tests:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-local.ps1
```

From `cmd.exe`, use:

```bat
scripts\test-local.cmd
```
