# Enterprise Knowledge Platform (RAG)

Semantic search over company documents using RAG architecture.

## Architecture

```
Documents (PDF, DOCX, HTML, MD)
       ↓
    AWS S3
       ↓
 Databricks (Bronze → Silver → Gold)
       ↓
 Snowflake (metadata + vectors)
       ↓
 Semantic Search
       ↓
     LLM
       ↓
   Chat UI
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| IaC | Terraform |
| Storage | AWS S3 |
| ETL | Databricks (Medallion Architecture) |
| Vector DB | Snowflake |
| Embeddings | `BAAI/bge-small-en-v1.5` |
| LLM | Ollama (Llama/Mistral/Qwen) or OpenAI/Anthropic API |
| UI | Streamlit |

## Project Structure

```
terraform/       IaC — S3 bucket, IAM roles, Snowflake integrations, Databricks resources
  aws/
  snowflake/
  databricks/
notebooks/       Databricks notebooks for ETL pipeline
src/
  ingest/        Parsing (PDF/HTML/MD), chunking (500/50), embedding generation
  search/        VECTOR_COSINE_SIMILARITY / Cortex Search queries
  llm/           LLM integration (local via Ollama or API)
api/             FastAPI backend
ui/              Streamlit chat interface
```

## Getting Started

1. Provision infra:
   ```bash
   cd terraform/aws
   terraform init && terraform apply
   ```
2. Upload documents to S3.
3. Run Databricks notebooks (bronze → silver → gold).
4. Start API + UI:
   ```bash
   cd api && uvicorn main:app
   cd ui && streamlit run app.py
   ```

## Medallion Architecture

- **Bronze** — raw documents from S3
- **Silver** — cleaned, parsed text
- **Gold** — chunked text with vector embeddings

## Use Cases

- Security policy Q&A
- Employee onboarding procedures
- Technical documentation search
- Financial report analysis
