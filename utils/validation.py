"""Input and dataset validation utilities."""

from models.schemas import validate_question_dict


def validate_dataset(items: list[dict]) -> None:
    if len(items) < 40:
        raise ValueError("Dataset must contain at least 40 questions.")
    ids = set()
    categories = set()
    for item in items:
        validate_question_dict(item)
        if item["id"] in ids:
            raise ValueError(f"Duplicate question ID: {item['id']}")
        ids.add(item["id"])
        categories.add(item["category"])
    if len(categories) != 8:
        raise ValueError("Dataset must represent all eight required categories.")


def choose_int(prompt: str, minimum: int, maximum: int, default: int) -> int:
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        value = int(raw)
        if minimum <= value <= maximum:
            return value
    except ValueError:
        pass
    print(f"Please enter an integer from {minimum} to {maximum}. Using {default}.")
    return default


def choose_bool(prompt: str, default: bool = True) -> bool:
    raw = input(prompt).strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes", "true", "1"}
