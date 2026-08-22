from models.schemas import validate_evaluation
from utils.validation import validate_dataset
import json
from pathlib import Path


def test_dataset():
    data = json.loads(Path("data/stress_tests.json").read_text(encoding="utf-8"))
    validate_dataset(data)
    assert len(data) >= 40


def test_evaluation_validation():
    result = validate_evaluation({
        "hallucination": False, "severity": 0, "confidence": 0.9,
        "hallucination_type": "none", "correctness": "correct",
        "should_have_refused_or_corrected": False, "reason": "Good.",
        "unsupported_claims": []
    })
    assert result.severity == 0
