# JanSwasthya AI — Research Documentation

*(Consolidated from Milestones 1–2; formatted for direct use in your B.Tech final report / IEEE-style paper)*

## 1. Problem Statement

India's public health information gap has two compounding failures: (1) low-income and rural populations often lack access to a trustworthy first point of contact for health questions, defaulting to unverified informal sources, and (2) even where government schemes like Ayushman Bharat or PM-JAY exist, awareness and navigational literacy remain low enough that eligible citizens underuse them. JanSwasthya AI addresses the *information and awareness* layer of this gap — explicitly not diagnosis or treatment — using a retrieval-grounded AI system that speaks only from verified sources and consistently routes users toward real healthcare access points.

## 2. Objectives

1. Build a multilingual RAG-based health education assistant grounded strictly in verified sources (WHO, ICMR, NHP, MoHFW).
2. Minimize hallucination via citation-forced generation, confidence thresholds, and a hard emergency-detection gate.
3. Build a scalable doctor-video content system so verified doctors can educate at scale.
4. Build a low-cost/free consultation booking layer connecting users to real doctors.
5. Surface government scheme information navigably for low-literacy users and community health workers.
6. Demonstrate production-grade engineering: authentication/RBAC, automated testing, CI/CD, and audit logging.

## 3. Literature Survey & Existing Systems

| System | Strength | Limitation JanSwasthya AI addresses |
|---|---|---|
| eSanjeevani | Free govt. teleconsultation | No AI education layer; requires prior scheme awareness |
| Practo / Apollo 24\|7 | Private doctor booking | Paid-first; symptom-checkers risk diagnosis-like framing |
| ASHA/NHM field apps | Structured worker tools | One-directional; not citizen-facing conversational AI |
| WHO/ICMR web content | Authoritative | Static, no localization, low rural discoverability |
| General-purpose LLM chatbots | Broad conversational ability | No source grounding; real hallucination risk on medical content |

Academic themes informing the design: retrieval-augmented generation measurably reduces hallucination versus pure generative answering in medical QA contexts; Indian-language NLP for health remains underserved outside Hindi/English, motivating the phased multilingual rollout; and digital-health-literacy research consistently finds that *trust and format* (local language, simple framing) matter as much as raw information availability — informing the emphasis on plain-language, non-alarming response tone throughout the system prompt design.

## 4. Research Gap

No existing platform combines (a) strictly source-grounded conversational AI for health education, (b) a scalable doctor-generated video education layer, (c) low-cost consultation booking, and (d) government scheme navigation, in one citizen-facing, multilingual system designed for India's low-income and rural demographic. The contribution is the *integration* of pieces that otherwise exist in fragmented form.

## 5. Proposed Methodology

1. Build a verified knowledge base → sentence-aware chunking → multilingual embeddings → Qdrant vector store.
2. RAG pipeline: retrieval → confidence gate (hard cutoff before any LLM call if top similarity is too low) → guarded generation → citation attachment.
3. Emergency detection as an independent hard gate running before retrieval, combining deterministic pattern matching with room for a future classifier layer.
4. Parallel doctor-verification / content-moderation / booking subsystem, each with its own admin-gated approval step, audit-logged.
5. Government scheme information served as structured data (not LLM-generated) for accuracy on eligibility-sensitive content.
6. Validation via a custom RAG evaluation harness measuring groundedness (context-answer overlap), refusal correctness on out-of-scope questions, and retrieval quality — not just qualitative "looks right" demo testing.

## 6. Innovation

- **Hard-gated emergency detection** that runs before, not alongside, generation — a deterministic safety layer rather than relying on LLM self-restraint.
- **Structured-data-first content** for disease info and government schemes, reserving generative RAG for open-ended conversational questions — reduces hallucination surface area on the highest-stakes factual content.
- **Dual verification gates** (doctor identity verification + per-video moderation) enforced at the API layer, not just UI convention.
- **Confidence-gated generation**: the system skips the LLM call entirely — not just the display — when retrieval confidence is too low, saving cost and guaranteeing the fallback path is taken.

## 7. Expected Results

A working multilingual (English/Hindi/Hinglish in v1) health education platform with measurably low hallucination rate on the evaluation golden set, a functioning doctor video/booking marketplace, and government scheme discoverability — deployed with CI/CD, automated tests, and audit logging suitable for a production-quality demonstration.

## 8. Future Scope

- Expand to the remaining 8 target languages once native-speaker-reviewed content and clinically-reviewed emergency copy exist for each.
- Voice input/output.
- Live video consultation integration (currently booking-only, video-ready architecture).
- Automated cross-referencing of doctor medical council registration numbers against the National Medical Register API.
- NLI-based (entailment) groundedness scoring to replace the current word-overlap heuristic for a more rigorous evaluation harness.

## 9. Reference Style Note

Format citations per your department's required style (commonly IEEE for CS/engineering B.Tech reports). Suggested reference categories to fill in with specific sources: WHO/ICMR/MoHFW official publications used in your knowledge base; 2–3 peer-reviewed papers on RAG-for-healthcare hallucination reduction; 1–2 papers on Indian-language low-resource NLP; government scheme official documentation (PM-JAY, Jan Aushadhi, eSanjeevani portals). I can help you search for and properly format specific citations once you've selected which papers to include — I don't fabricate citation details, so pull the actual papers via Google Scholar/IEEE Xplore and I'll help format them correctly.
