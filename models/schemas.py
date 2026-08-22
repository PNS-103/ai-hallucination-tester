"""Dataclasses and validation helpers for project data."""

from dataclasses import dataclass, field, asdict
from typing import Any


SUPPORTED_CATEGORIES = {
    "false_premise", "fake_entity", "impossible_question", "ambiguous_question",
    "future_event", "misleading_question", "obscure_knowledge",
    "contradictory_question",
}
DIFFICULTIES = {"easy", "medium", "hard"}


@dataclass
class StressTestQuestion:
    id: str
    category: str
    question: str
    expected_behavior: str
    difficulty: str
    explanation: str
    evaluation_notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LLMResponse:
    question_id: str
    question: str
    answer: str
    model: str
    latency: float
    status: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationResult:
    hallucination: bool
    severity: int
    confidence: float
    hallucination_type: str
    correctness: str
    should_have_refused_or_corrected: bool
    reason: str
    unsupported_claims: list[str] = field(default_factory=list)
    status: str = "success"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_question_dict(item: dict[str, Any]) -> None:
    required = {
        "id", "category", "question", "expected_behavior",
        "difficulty", "explanation", "evaluation_notes"
    }
    missing = required - item.keys()
    if missing:
        raise ValueError(f"Missing question fields: {sorted(missing)}")
    if not all(isinstance(item[k], str) for k in required):
        raise ValueError(f"Question {item.get('id')} contains invalid field types.")
    if not item["id"].strip() or not item["question"].strip():
        raise ValueError("Question id and question must be non-empty.")
    if item["category"] not in SUPPORTED_CATEGORIES:
        raise ValueError(f"Unsupported category: {item['category']}")
    if item["difficulty"] not in DIFFICULTIES:
        raise ValueError(f"Unsupported difficulty: {item['difficulty']}")


def validate_evaluation(data: dict[str, Any]) -> EvaluationResult:
    required = {
        "hallucination", "severity", "confidence", "hallucination_type",
        "correctness", "should_have_refused_or_corrected", "reason",
        "unsupported_claims"
    }
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing evaluator fields: {sorted(missing)}")
    if not isinstance(data["hallucination"], bool):
        raise ValueError("hallucination must be boolean.")
    if not isinstance(data["severity"], int) or not 0 <= data["severity"] <= 5:
        raise ValueError("severity must be an integer from 0 to 5.")
    if not isinstance(data["confidence"], (int, float)) or not 0 <= float(data["confidence"]) <= 1:
        raise ValueError("confidence must be between 0 and 1.")
    if data["correctness"] not in {"correct", "incorrect", "partially_correct", "unknown"}:
        raise ValueError("Invalid correctness value.")
    if not isinstance(data["unsupported_claims"], list):
        raise ValueError("unsupported_claims must be a list.")
    return EvaluationResult(
        hallucination=data["hallucination"],
        severity=data["severity"],
        confidence=float(data["confidence"]),
        hallucination_type=str(data["hallucination_type"]),
        correctness=data["correctness"],
        should_have_refused_or_corrected=bool(data["should_have_refused_or_corrected"]),
        reason=str(data["reason"]),
        unsupported_claims=[str(x) for x in data["unsupported_claims"]],
    )
