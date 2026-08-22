"""Model comparison calculations."""

from utils.metrics import calculate_summary


class ComparisonService:
    @staticmethod
    def compare(runs: list[dict]) -> list[dict]:
        rows = []
        for run in runs:
            summary = run.get("summary", calculate_summary(
                run.get("evaluations", []), run.get("responses", [])
            ))
            rows.append({
                "model": run.get("model", "unknown"),
                "evaluator_model": run.get("evaluator_model", "unknown"),
                "hallucination_rate": summary.get("hallucination_rate", 0),
                "correct_response_rate": summary.get("correct_response_rate", 0),
                "average_severity": summary.get("average_severity", 0),
                "average_confidence": summary.get("average_evaluator_confidence", 0),
                "average_latency": summary.get("average_latency", 0),
            })
        return rows
