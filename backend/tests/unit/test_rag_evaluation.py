from dataclasses import dataclass

from app.services.rag.evaluation import (
    word_overlap_ratio,
    evaluate_refusal_case,
    evaluate_groundedness_case,
    run_evaluation_suite,
)


@dataclass
class FakeRAGResponse:
    answer: str
    sources: list[dict]
    was_grounded: bool


class TestGroundednessScoring:
    def test_high_overlap_scores_high(self):
        answer = "Dengue causes high fever and severe headache."
        context = "Dengue is a viral infection causing high fever, severe headache, and joint pain."
        assert word_overlap_ratio(answer, context) > 0.5

    def test_no_overlap_scores_zero(self):
        answer = "Bitcoin prices fluctuate wildly."
        context = "Dengue is a viral infection causing fever."
        assert word_overlap_ratio(answer, context) == 0.0

    def test_groundedness_case_passes_above_threshold(self):
        result = evaluate_groundedness_case(
            question="What is dengue?",
            answer="Dengue causes high fever and headache",
            context="Dengue causes high fever, headache, and joint pain",
            min_overlap=0.15,
        )
        assert result.passed is True


class TestRefusalEvaluation:
    def test_refusal_correctly_detected(self):
        result = evaluate_refusal_case(
            question="What's a good crypto investment?",
            was_grounded=False,
            answer="I don't have verified information on this topic yet.",
        )
        assert result.passed is True

    def test_hallucinated_answer_fails_refusal_check(self):
        result = evaluate_refusal_case(
            question="What's a good crypto investment?",
            was_grounded=True,
            answer="You should invest in Bitcoin because it's trending up.",
        )
        assert result.passed is False


class TestEvaluationSuite:
    def test_suite_runs_against_mocked_generator(self):
        def fake_generate(question: str) -> FakeRAGResponse:
            if "dengue" in question.lower() or "diabetes" in question.lower():
                return FakeRAGResponse(
                    answer="This is a grounded answer about the topic.",
                    sources=[{"publisher": "WHO"}],
                    was_grounded=True,
                )
            return FakeRAGResponse(
                answer="I don't have verified information on this topic yet.",
                sources=[],
                was_grounded=False,
            )

        report = run_evaluation_suite(fake_generate)
        assert report["total"] == 4
        assert report["pass_rate"] == 1.0  # all golden cases handled correctly by this fake
