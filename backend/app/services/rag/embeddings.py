"""
Embedding wrapper around sentence-transformers.

Uses a multilingual model (paraphrase-multilingual-mpnet-base-v2) rather than
an English-only one — critical since the knowledge base and queries span
English/Hindi/Hinglish at minimum, with more Indian languages planned.
Loaded once as a module-level singleton; embedding calls are CPU/GPU-bound
and re-instantiating the model per request would be wasteful.
"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()
