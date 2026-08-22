"""Provider abstraction and OpenAI/mock implementations."""

from abc import ABC, abstractmethod
import json
import time
from typing import Any



class BaseLLMProvider(ABC):
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text from the provider."""


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str, temperature: float = 0.2, max_tokens: int = 800):
        super().__init__(model)
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The openai package is required for LLM_PROVIDER=openai. Run: pip install -r requirements.txt") from exc
        self.client = OpenAI(api_key=api_key)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return (response.choices[0].message.content or "").strip()


class MockProvider(BaseLLMProvider):
    """Deterministic provider used for demos and tests without API calls."""

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        if "Return ONLY valid JSON" in system_prompt:
            question = user_prompt.lower()
            bad = any(term in question for term in [
                "president of india in 1890", "zephyria", "square circle",
                "tomorrow's", "invisible", "made-up"
            ])
            return json.dumps({
                "hallucination": bad,
                "severity": 5 if bad else 0,
                "confidence": 0.95,
                "hallucination_type": "false_premise" if bad else "none",
                "correctness": "incorrect" if bad else "correct",
                "should_have_refused_or_corrected": bad,
                "reason": "Mock evaluator detected a deliberately problematic premise."
                if bad else "Mock evaluator found an appropriate response.",
                "unsupported_claims": ["Mock unsupported claim"] if bad else [],
            })
        return (
            "I cannot verify that premise reliably. The question appears designed "
            "to test whether I will invent unsupported facts, so I would correct "
            "the premise or state uncertainty rather than fabricate an answer."
        )
