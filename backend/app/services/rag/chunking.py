"""
Chunking strategy for the verified health knowledge base.

Why sentence-aware sliding-window chunking instead of naive fixed-size split:
health guidance often has tightly-coupled clauses ("take X unless Y") — cutting
mid-sentence risks a retrieved chunk asserting something out of context, which
is exactly the kind of subtle error this platform cannot afford.
"""
import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    source_id: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)


def split_into_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return re.split(r"(?<=[.!?])\s+", text)


def chunk_document(
    text: str,
    source_id: str,
    max_chunk_chars: int = 800,
    overlap_sentences: int = 1,
    metadata: dict | None = None,
) -> list[Chunk]:
    sentences = split_into_sentences(text)
    chunks: list[Chunk] = []
    current: list[str] = []
    current_len = 0
    idx = 0

    for sentence in sentences:
        if current_len + len(sentence) > max_chunk_chars and current:
            chunks.append(Chunk(text=" ".join(current), source_id=source_id, chunk_index=idx, metadata=metadata or {}))
            idx += 1
            # keep overlap for context continuity across chunk boundaries
            current = current[-overlap_sentences:] if overlap_sentences else []
            current_len = sum(len(s) for s in current)

        current.append(sentence)
        current_len += len(sentence)

    if current:
        chunks.append(Chunk(text=" ".join(current), source_id=source_id, chunk_index=idx, metadata=metadata or {}))

    return chunks
