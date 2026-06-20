from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "eu-central-1"
    s3_bucket_name: str

    snowflake_account: str
    snowflake_user: str
    snowflake_password: str
    snowflake_role: str = "EKP_ROLE"
    snowflake_warehouse: str = "EKP_WH"
    snowflake_database: str = "EKP_DB"
    snowflake_schema: str = "RAG"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    class Config:
        env_file = ".env"


settings = Settings()