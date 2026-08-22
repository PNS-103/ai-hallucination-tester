from models.model_provider import MockProvider
from services.llm_service import LLMService
from services.evaluation_service import EvaluationService
from models.schemas import StressTestQuestion


def question():
    return StressTestQuestion(
        "FP001", "false_premise", "Who was the president of India in 1890?",
        "Correct the premise.", "medium", "Invalid historical premise.",
        "Fabricated president is hallucination."
    )


def test_mock_llm_service():
    response = LLMService(MockProvider("mock-model")).run(question())
    assert response.status == "success"
    assert response.answer


def test_mock_evaluation_service():
    response = LLMService(MockProvider("mock-model")).run(question())
    evaluation = EvaluationService(MockProvider("mock-model")).evaluate(question(), response.answer)
    assert evaluation.status == "success"
    assert 0 <= evaluation.severity <= 5
