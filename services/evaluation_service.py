"""Evaluator LLM execution, parsing, validation and retries."""

import time
from models.schemas import validate_evaluation, EvaluationResult
from prompts.evaluator_prompt import EVALUATOR_SYSTEM_PROMPT, build_evaluator_prompt
from utils.json_utils import parse_json_object


class EvaluationService:
    def __init__(self, provider, retries=1):
        self.provider = provider
        self.retries = retries

    def evaluate(self, question, answer) -> EvaluationResult:
        prompt = build_evaluator_prompt(question, answer)
        last_error = None
        for _ in range(self.retries + 1):
            try:
                raw = self.provider.generate_response(EVALUATOR_SYSTEM_PROMPT, prompt)
                return validate_evaluation(parse_json_object(raw))
            except Exception as exc:
                last_error = exc
        return EvaluationResult(
            hallucination=False, severity=0, confidence=0.0,
            hallucination_type="evaluation_failed", correctness="unknown",
            should_have_refused_or_corrected=False,
            reason=f"Evaluation failed: {last_error}",
            unsupported_claims=[], status="failed"
        )
