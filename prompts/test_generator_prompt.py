"""Prompt for optional LLM-generated stress-test questions."""

TEST_GENERATOR_PROMPT = """Generate difficult hallucination stress-test questions.
Return ONLY a JSON array. Each object must contain:
id, category, question, expected_behavior, difficulty, explanation, evaluation_notes.
Use only these categories:
false_premise, fake_entity, impossible_question, ambiguous_question,
future_event, misleading_question, obscure_knowledge, contradictory_question.
Avoid political and personally identifying examples."""
