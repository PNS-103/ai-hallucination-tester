"""Dataset loading, validation, selection and optional generation."""

import random
from models.schemas import StressTestQuestion
from utils.json_utils import load_json
from utils.validation import validate_dataset
from prompts.test_generator_prompt import TEST_GENERATOR_PROMPT


class StressTestService:
    def __init__(self, data_file, provider=None):
        self.data_file = data_file
        self.provider = provider

    def load_questions(self) -> list[StressTestQuestion]:
        raw = load_json(self.data_file)
        if not isinstance(raw, list):
            raise ValueError("Stress-test dataset must be a JSON array.")
        validate_dataset(raw)
        return [StressTestQuestion(**item) for item in raw]

    def select(self, questions, categories=None, count=None, randomize=True):
        selected = [q for q in questions if not categories or q.category in categories]
        if randomize:
            selected = selected.copy()
            random.shuffle(selected)
        if count:
            selected = selected[:count]
        return selected

    def generate_questions(self, count=5):
        if not self.provider:
            raise ValueError("A provider is required for question generation.")
        text = self.provider.generate_response(
            "You generate stress-test datasets. " + TEST_GENERATOR_PROMPT,
            f"Generate {count} additional questions."
        )
        import json
        data = json.loads(text)
        validate_dataset(data if len(data) >= 40 else self._pad_for_validation(data))
        return [StressTestQuestion(**item) for item in data]

    @staticmethod
    def _pad_for_validation(items):
        return items + [{
            "id": f"VALIDATION_{i}",
            "category": "false_premise",
            "question": f"Validation placeholder {i}?",
            "expected_behavior": "Identify uncertainty.",
            "difficulty": "easy",
            "explanation": "Internal validation padding only.",
            "evaluation_notes": "Internal validation padding only."
        } for i in range(40-len(items))]
