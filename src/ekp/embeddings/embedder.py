import os

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self, model_name: str | None = None) -> None:
        selected_model = model_name or os.getenv(
            "EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"
        )
        self.model = SentenceTransformer(selected_model)

    def encode_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
