"""
RAG generation: retrieval -> rerank-by-score -> guarded generation -> confidence gate.

Core guardrail: the LLM is instructed to answer ONLY from provided context and
to explicitly say so if the context is insufficient. This is enforced twice:
  1. Prompt-level instruction (soft guardrail)
  2. Post-hoc confidence check using retrieval scores (hard guardrail) — if the
     top retrieved chunk's similarity score is below RAG_MIN_CONFIDENCE, we
     never call the LLM at all and return the fallback directly. This also
     saves an LLM call on queries we already know we can't ground.
"""
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.services.rag.embeddings import embed_text
from app.services.rag.vector_store import semantic_search

SYSTEM_GUARDRAIL_PROMPT = """You are a public health education assistant for Indian citizens.

STRICT RULES:
- Answer ONLY using the information in the provided context below.
- Do NOT diagnose any condition. Do NOT recommend or name specific medicines or dosages.
- Do NOT replace professional medical advice.
- If the context does not contain enough information to answer, say so plainly
  instead of guessing.
- Always write in a clear, simple, non-alarming tone suitable for someone with
  no medical background.
- End every answer with: "This is educational information only, not a diagnosis
  or treatment recommendation. Please consult a doctor or visit a Primary
  Health Centre for personal medical advice."

CONTEXT:
{context}

USER QUESTION:
{question}
"""

FALLBACK_MESSAGE = (
    "I don't have verified information on this topic yet, so I don't want to guess. "
    "Please consult a doctor, ASHA worker, or your nearest Primary Health Centre for "
    "reliable guidance on this question."
)


@dataclass
class RAGResponse:
    answer: str
    sources: list[dict]
    confidence: float
    was_grounded: bool


def _call_llm(prompt: str) -> str:
    """Thin client for an OpenAI-compatible completion endpoint (self-hosted
    Mistral/Llama/Gemma or hosted provider — swappable via settings)."""
    response = httpx.post(
        f"{settings.LLM_API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"} if settings.LLM_API_KEY else {},
        json={
            "model": settings.LLM_MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,  # low temperature — factual health content, not creative writing
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate_answer(question: str, language: str = "en") -> RAGResponse:
    query_embedding = embed_text(question)
    retrieved = semantic_search(query_embedding, top_k=settings.RAG_TOP_K, language=language)

    if not retrieved or retrieved[0]["score"] < settings.RAG_MIN_CONFIDENCE:
        return RAGResponse(answer=FALLBACK_MESSAGE, sources=[], confidence=0.0, was_grounded=False)

    context = "\n\n".join(f"[{r['publisher']}] {r['text']}" for r in retrieved)
    prompt = SYSTEM_GUARDRAIL_PROMPT.format(context=context, question=question)

    answer = _call_llm(prompt)
    top_confidence = retrieved[0]["score"]

    sources = [
        {"publisher": r["publisher"], "source_url": r["source_url"]}
        for r in retrieved
        if r["score"] >= settings.RAG_MIN_CONFIDENCE
    ]

    return RAGResponse(answer=answer, sources=sources, confidence=top_confidence, was_grounded=True)
