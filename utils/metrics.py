"""Metric calculation helpers."""

from collections import Counter, defaultdict
from typing import Iterable


def calculate_summary(evaluations: list[dict], responses: list[dict]) -> dict:
    evaluated = [e for e in evaluations if e.get("status", "success") == "success"]
    successful = [r for r in responses if r.get("status") == "success"]
    failed = [r for r in responses if r.get("status") != "success"]
    hallucinated = [e for e in evaluated if e["hallucination"]]
    correct = [e for e in evaluated if e["correctness"] == "correct"]

    n = len(evaluated)
    severity_sum = sum(e["severity"] for e in evaluated)
    weighted = severity_sum / (n * 5) * 100 if n else 0.0

    return {
        "total_questions": len(responses),
        "successful_tests": len(successful),
        "failed_tests": len(failed),
        "evaluated_responses": n,
        "hallucinated_responses": len(hallucinated),
        "non_hallucinated_responses": n - len(hallucinated),
        "hallucination_rate": len(hallucinated) / n * 100 if n else 0.0,
        "correct_response_rate": len(correct) / n * 100 if n else 0.0,
        "average_severity": severity_sum / n if n else 0.0,
        "average_evaluator_confidence": (
            sum(e["confidence"] for e in evaluated) / n if n else 0.0
        ),
        "average_latency": (
            sum(r["latency"] for r in successful) / len(successful) if successful else 0.0
        ),
        "weighted_hallucination_score": weighted,
        "severity_distribution": dict(Counter(str(e["severity"]) for e in evaluated)),
    }


def category_statistics(evaluations: list[dict], question_by_id: dict[str, dict]) -> dict:
    buckets = defaultdict(list)
    for evaluation in evaluations:
        if evaluation.get("status", "success") != "success":
            continue
        q = question_by_id.get(evaluation.get("question_id"))
        if q:
            buckets[q["category"]].append(evaluation)

    stats = {}
    for category, values in buckets.items():
        n = len(values)
        stats[category] = {
            "evaluated": n,
            "hallucination_rate": sum(v["hallucination"] for v in values) / n * 100,
            "accuracy": sum(v["correctness"] == "correct" for v in values) / n * 100,
        }
    return stats
