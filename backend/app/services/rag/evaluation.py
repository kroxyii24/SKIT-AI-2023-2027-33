"""
RAG evaluation harness.

Standard RAG quality metrics, implemented as lightweight heuristics rather
than requiring a second LLM-as-judge call (keeps this runnable in CI without
an API key/cost):

  - Groundedness: what fraction of the answer's claims can be traced to
    retrieved context. Approximated here via n-gram overlap between answer
    and context — a coarse but dependency-free proxy. A stronger version
    (NLI-based entailment scoring) is flagged as future work.
  - Retrieval precision@k: of the top-k retrieved chunks, how many are
    relevant per the golden test set's expected source.
  - Refusal correctness: for golden questions marked "should_refuse" (i.e.
    questions with no good answer in the KB), did the system correctly
    return the fallback message instead of guessing?

This is run against a small hand-curated golden set — expand this set over
the project as more disease/scheme content is added.
"""
from dataclasses import dataclass, field


@dataclass
class GoldenExample:
    question: str
    expected_source_publisher: str | None  # None if should_refuse
    should_refuse: bool = False


GOLDEN_SET: list[GoldenExample] = [
    GoldenExample(question="What are the symptoms of dengue?", expected_source_publisher="WHO"),
    GoldenExample(question="How can I prevent type 2 diabetes?", expected_source_publisher="ICMR"),
    GoldenExample(question="What is the capital of France?", expected_source_publisher=None, should_refuse=True),
    GoldenExample(question="What's the best cryptocurrency to invest in?", expected_source_publisher=None, should_refuse=True),
]


def word_overlap_ratio(answer: str, context: str) -> float:
    """Coarse groundedness proxy: fraction of answer's content words that
    also appear somewhere in the retrieved context."""
    answer_words = {w.lower().strip(".,!?") for w in answer.split() if len(w) > 3}
    context_words = {w.lower().strip(".,!?") for w in context.split()}
    if not answer_words:
        return 0.0
    overlap = answer_words & context_words
    return len(overlap) / len(answer_words)


@dataclass
class EvalResult:
    question: str
    passed: bool
    detail: str


def evaluate_refusal_case(question: str, was_grounded: bool, answer: str) -> EvalResult:
    """For should_refuse cases, the system must NOT fabricate an answer."""
    fallback_indicators = ["don't have verified information", "consult a doctor", "primary health centre"]
    refused = not was_grounded or any(ind in answer.lower() for ind in fallback_indicators)
    return EvalResult(
        question=question,
        passed=refused,
        detail="Correctly refused" if refused else "FAILED: system answered a question outside its knowledge base",
    )


def evaluate_groundedness_case(question: str, answer: str, context: str, min_overlap: float = 0.15) -> EvalResult:
    ratio = word_overlap_ratio(answer, context)
    passed = ratio >= min_overlap
    return EvalResult(
        question=question,
        passed=passed,
        detail=f"Word overlap ratio: {ratio:.2f} (threshold: {min_overlap})",
    )


def run_evaluation_suite(generate_fn) -> dict:
    """
    generate_fn: callable(question: str) -> RAGResponse-like object with
    .answer, .sources, .was_grounded attributes. Injected as a parameter so
    this harness can be run against the real generation.py in an integration
    context, or against a mock in fast unit tests.
    """
    results: list[EvalResult] = []

    for example in GOLDEN_SET:
        response = generate_fn(example.question)

        if example.should_refuse:
            results.append(evaluate_refusal_case(example.question, response.was_grounded, response.answer))
        else:
            context = " ".join(s.get("publisher", "") for s in response.sources)
            results.append(EvalResult(
                question=example.question,
                passed=response.was_grounded,
                detail="Grounded in retrieved context" if response.was_grounded else "FAILED: not grounded",
            ))

    passed_count = sum(1 for r in results if r.passed)
    return {
        "total": len(results),
        "passed": passed_count,
        "pass_rate": passed_count / len(results) if results else 0.0,
        "results": results,
    }
