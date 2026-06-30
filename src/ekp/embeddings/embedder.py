from sentence_transformers import SentenceTransformer

from ekp.config import settings


class EmbeddingModel:
    def __init__(self) -> None:
        self.model = SentenceTransformer(settings.embedding_model)

    def encode_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
