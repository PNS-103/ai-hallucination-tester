"""LLM-under-test execution and latency/error handling."""

import time
from models.schemas import LLMResponse
from prompts.system_prompts import LLM_TEST_SYSTEM_PROMPT


class LLMService:
    def __init__(self, provider):
        self.provider = provider

    def run(self, question) -> LLMResponse:
        start = time.perf_counter()
        try:
            answer = self.provider.generate_response(LLM_TEST_SYSTEM_PROMPT, question.question)
            latency = time.perf_counter() - start
            if not answer.strip():
                return LLMResponse(question.id, question.question, "", self.provider.model,
                                    latency, "failed", "Empty LLM response.")
            return LLMResponse(question.id, question.question, answer,
                               self.provider.model, latency, "success")
        except Exception as exc:
            latency = time.perf_counter() - start
            return LLMResponse(question.id, question.question, "", self.provider.model,
                               latency, "failed", str(exc))
