"""Scoring facade."""

from utils.metrics import calculate_summary, category_statistics


class ScoringService:
    @staticmethod
    def summary(evaluations, responses):
        return calculate_summary(evaluations, responses)

    @staticmethod
    def categories(evaluations, questions):
        lookup = {q["id"]: q for q in questions}
        return category_statistics(evaluations, lookup)
