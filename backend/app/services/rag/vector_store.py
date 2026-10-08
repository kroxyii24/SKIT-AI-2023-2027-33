"""
Qdrant vector store wrapper.

Keeps all Qdrant-specific API calls in one place so the rest of the RAG
pipeline depends only on this module's interface — makes it possible to swap
to ChromaDB later (as the spec allows) by reimplementing just this file.
"""
import uuid
from functools import lru_cache
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings

VECTOR_SIZE = 768  # matches paraphrase-multilingual-mpnet-base-v2 output dim


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL)


def ensure_collection() -> None:
    client = get_client()
    collections = [c.name for c in client.get_collections().collections]
    if settings.QDRANT_COLLECTION not in collections:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list[dict]) -> int:
    """
    chunks: list of dicts with keys: text, embedding, source_id, chunk_index,
    publisher, source_url, language
    """
    ensure_collection()
    client = get_client()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=c["embedding"],
            payload={
                "text": c["text"],
                "source_id": c["source_id"],
                "chunk_index": c["chunk_index"],
                "publisher": c.get("publisher"),
                "source_url": c.get("source_url"),
                "language": c.get("language", "en"),
            },
        )
        for c in chunks
    ]
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)
    return len(points)


def semantic_search(query_embedding: list[float], top_k: int = 5, language: str | None = None) -> list[dict]:
    client = get_client()
    query_filter = None
    if language:
        query_filter = Filter(must=[FieldCondition(key="language", match=MatchValue(value=language))])

    results = client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=query_filter,
    )
    return [
        {
            "text": r.payload["text"],
            "publisher": r.payload.get("publisher"),
            "source_url": r.payload.get("source_url"),
            "score": r.score,
        }
        for r in results
    ]
