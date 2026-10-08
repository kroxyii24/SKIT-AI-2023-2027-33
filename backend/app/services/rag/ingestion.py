"""
Ingestion pipeline: raw verified document -> chunks -> embeddings -> Qdrant.

Called from the Admin Portal's "Upload Government PDF / Add Source" flow
(Milestone 33+), and from a standalone CLI/script for bulk-loading the
initial WHO/ICMR/MoHFW corpus during knowledge-base bootstrapping.
"""
from app.services.rag.chunking import chunk_document
from app.services.rag.embeddings import embed_batch
from app.services.rag.vector_store import upsert_chunks


def ingest_document(
    text: str,
    source_id: str,
    publisher: str,
    source_url: str | None = None,
    language: str = "en",
) -> int:
    chunks = chunk_document(text=text, source_id=source_id, metadata={"publisher": publisher})
    if not chunks:
        return 0

    embeddings = embed_batch([c.text for c in chunks])

    payload = [
        {
            "text": chunk.text,
            "embedding": embedding,
            "source_id": chunk.source_id,
            "chunk_index": chunk.chunk_index,
            "publisher": publisher,
            "source_url": source_url,
            "language": language,
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]

    return upsert_chunks(payload)
