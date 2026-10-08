# RAG Query Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant W as Web App
    participant API as Chat Orchestrator
    participant ED as Emergency Detector
    participant RAG as RAG Engine
    participant VDB as Vector DB
    participant LLM as LLM Provider

    U->>W: Sends health question
    W->>API: POST /chat/message (JWT auth)
    API->>ED: classify_intent(message)
    alt Emergency detected
        ED-->>API: EMERGENCY flag
        API-->>W: Return emergency response + helpline numbers
    else Normal query
        API->>RAG: retrieve_and_generate(message, history)
        RAG->>VDB: semantic_search(embedding)
        VDB-->>RAG: top_k verified chunks + sources
        RAG->>RAG: rerank(chunks)
        RAG->>LLM: generate(context=chunks, query, guardrail_prompt)
        LLM-->>RAG: draft answer
        RAG->>RAG: citation_check() + confidence_score()
        alt confidence < threshold OR no supporting chunk
            RAG-->>API: fallback_response("insufficient verified info")
        else
            RAG-->>API: answer + citations + confidence
        end
        API-->>W: Response with sources
    end
    W-->>U: Render answer + "Educational info only" disclaimer
```

## Design rationale
- Emergency detection runs **before** RAG retrieval — cheaper, faster, and ensures no emergency query ever gets a "let me look that up" delay.
- If the RAG engine can't ground an answer in retrieved chunks above a confidence threshold, it **must** return a fallback rather than let the LLM improvise. This is the core hallucination-prevention mechanism.
