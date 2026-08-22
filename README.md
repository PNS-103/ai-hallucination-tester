# AI Hallucination Stress Tester

A complete Python console/CLI mini-project that stress-tests an LLM with deliberately difficult questions and uses a separate evaluator LLM to estimate hallucination behavior.

## Problem statement

LLMs can produce fluent but unsupported claims when faced with false premises, fictional entities, impossible requests, ambiguity, misleading wording, obscure information, future events, and contradictions. This project provides a repeatable local test harness for measuring those behaviors.

## Objectives

- Test an LLM with predefined stress questions.
- Optionally support generated questions.
- Evaluate responses with a separate evaluator LLM.
- Classify hallucination type and severity.
- Calculate hallucination, correctness, confidence, latency, category and weighted metrics.
- Save runs as JSON and export evaluated responses as CSV.
- Compare saved model runs.
- Provide mock mode for testing without an API key.
- Provide automated tests using mocked calls.

## Important model note

The provider and model are configurable. `gpt-4.1-mini` is used as an example configuration and is **not described as open-source**.

## Architecture

User -> Console -> Stress Test Service -> LLM Under Test -> Evaluation Service -> Evaluator LLM -> JSON Validation -> Scoring -> Results -> JSON/CSV

The provider abstraction is:

`BaseLLMProvider -> OpenAIProvider / MockProvider`

## Modules

- `app.py`: CLI entry point and navigation.
- `config/settings.py`: environment configuration.
- `models/schemas.py`: data structures and validation.
- `models/model_provider.py`: provider abstraction and implementations.
- `services/stress_test_service.py`: dataset loading, validation, selection and generation.
- `services/llm_service.py`: LLM execution, latency and errors.
- `services/evaluation_service.py`: evaluator prompt, parsing, validation and retries.
- `services/scoring_service.py`: scoring facade.
- `services/comparison_service.py`: model comparison.
- `services/result_service.py`: JSON persistence and CSV export.
- `utils/`: JSON, validation, metrics and logging utilities.
- `tests/`: automated tests.

## Project structure

```text
ai-hallucination-stress-tester/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── pytest.ini
├── config/
│   ├── __init__.py
│   └── settings.py
├── data/
│   ├── stress_tests.json
│   └── sample_results.json
├── prompts/
│   ├── __init__.py
│   ├── evaluator_prompt.py
│   ├── test_generator_prompt.py
│   └── system_prompts.py
├── models/
│   ├── __init__.py
│   ├── schemas.py
│   └── model_provider.py
├── services/
│   ├── __init__.py
│   ├── stress_test_service.py
│   ├── llm_service.py
│   ├── evaluation_service.py
│   ├── scoring_service.py
│   ├── comparison_service.py
│   └── result_service.py
├── utils/
│   ├── __init__.py
│   ├── json_utils.py
│   ├── validation.py
│   ├── metrics.py
│   └── logger.py
├── results/
│   └── .gitkeep
├── exports/
│   └── .gitkeep
└── tests/
    ├── __init__.py
    ├── test_validation.py
    ├── test_scoring.py
    ├── test_json_utils.py
    └── test_services.py
```

## Technology stack

Python 3.10+ and the standard library, plus:

| Library | Why required | Installation |
|---|---|---|
| openai | Communicates with the configured OpenAI-compatible API | `pip install openai` |
| python-dotenv | Loads `.env` configuration | `pip install python-dotenv` |
| pandas | Generates CSV exports | `pip install pandas` |
| pytest | Runs automated tests | `pip install pytest` |

You do not need to install these individually when using `pip install -r requirements.txt`.

No Streamlit, database, vector database, RAG framework, traditional ML classifier, or web interface is required.

## Windows + VS Code setup

1. Install Python 3.10 or newer.
2. Install VS Code.
3. Install the **Python** extension by Microsoft.
4. Open the project folder in VS Code.
5. Open Terminal -> New Terminal.
6. Create a virtual environment:

```powershell
python -m venv .venv
```

7. Activate it:

```powershell
.venv\Scripts\activate
```

8. Select `.venv` as the Python interpreter:
   `Ctrl+Shift+P` -> `Python: Select Interpreter` -> choose `.venv`.
9. Install dependencies:

```powershell
pip install -r requirements.txt
```

10. Copy `.env.example` to `.env`.
11. For mock mode, keep:

```text
LLM_PROVIDER=mock
```

12. Run:

```powershell
python app.py
```

13. Test:

```powershell
pytest
```

## API configuration

`.env` example:

```text
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4.1-mini
EVALUATOR_MODEL=gpt-4.1-mini
LLM_PROVIDER=openai
TEMPERATURE=0.2
MAX_TOKENS=800
EVALUATION_RETRIES=1
RANDOMIZE=true
```

Never hardcode an API key, print it, or store it in results. `.env` is ignored by Git.

If `LLM_PROVIDER=openai` and `LLM_API_KEY` is missing, the application reports a clear configuration error.

## Mock mode

Mock mode is deterministic and makes no external calls:

```text
LLM_PROVIDER=mock
```

It is suitable for demonstrations, unit tests and development without API cost.

## Running

```powershell
python app.py
```

The menu contains:

1. Run Stress Test
2. Select Categories
3. Configure Model
4. View Previous Results
5. Compare Models
6. Export Results
7. View Dataset Statistics
8. Exit

## Testing

```powershell
pytest
```

The tests use `MockProvider` and do not require an API key.

## Stress-test categories

The dataset contains 40 questions, five each in:

1. False Premise
2. Fake Entity
3. Impossible Question
4. Ambiguous Question
5. Future Event
6. Misleading Question
7. Obscure/Knowledge-Limit Question
8. Contradictory Question

Each question contains:

`id`, `category`, `question`, `expected_behavior`, `difficulty`, `explanation`, `evaluation_notes`.

## Evaluation

The evaluator receives the original question, expected behavior, evaluation notes, and LLM response. It returns JSON with:

- hallucination
- severity (0-5)
- confidence (0-1)
- hallucination type
- correctness
- whether the model should have refused/corrected
- reason
- unsupported claims

Invalid evaluator JSON is safely parsed/rejected and retried according to `EVALUATION_RETRIES`. A failed evaluation does not crash the entire run.

## Scoring formulas

Hallucination rate:

`hallucinated_responses / evaluated_responses * 100`

Correct response rate:

`correct_responses / evaluated_responses * 100`

Weighted hallucination score:

`sum(severity values) / (evaluated responses * 5) * 100`

The weighted score ranges from 0% to 100%; higher means more severe hallucination burden.

Evaluator confidence is the evaluator's confidence in its judgment. It is **not** the LLM-under-test's confidence.

## Results

Runs are saved automatically under `results/` as JSON. A run contains:

- run ID
- timestamp
- model
- evaluator model
- configuration
- questions
- responses
- evaluations
- summary
- category statistics

CSV exports are written to `exports/`.

## Example console session

```text
==========================================================
        AI HALLUCINATION STRESS TESTER
==========================================================
Provider: mock
Model: gpt-4.1-mini

1. Run Stress Test
2. Select Categories
3. Configure Model
4. View Previous Results
5. Compare Models
6. Export Results
7. View Dataset Statistics
8. Exit

Enter your choice: 1

Run ID: a12bc345

==========================================================
TEST 1 / 10 | false_premise | FP001
Difficulty: medium

QUESTION:
Who was the president of India in 1890?

LLM RESPONSE:
I cannot verify that premise reliably...

Evaluating...
HALLUCINATION: NO
SEVERITY: 0/5
CONFIDENCE: 0.95
TYPE: none
CORRECTNESS: correct
```

The exact run ID, ordering and latency will vary.

## Example result

```json
{
  "run_id": "a12bc345",
  "timestamp": "2026-08-10T17:30:00",
  "model": "gpt-4.1-mini",
  "evaluator_model": "gpt-4.1-mini",
  "summary": {
    "hallucination_rate": 20.0,
    "correct_response_rate": 80.0,
    "average_severity": 1.0,
    "weighted_hallucination_score": 20.0
  }
}
```

This is an illustrative structure, not a claimed real run.

## Adding another provider/model

The rest of the project depends only on `BaseLLMProvider.generate_response(system_prompt, user_prompt)`. To add a provider:

1. Create a class inheriting `BaseLLMProvider`.
2. Implement `generate_response`.
3. Add provider selection in `app.py` or a dedicated factory.
4. Document its environment variables.
5. Add tests using a deterministic mock.

Provider-specific API calls should remain inside provider implementations.

## Optional question generation

`StressTestService.generate_questions()` contains the provider-based generation path. Generated content should be validated before use. For academic repeatability, the predefined dataset is the primary dataset.

## Logging

Application events are written to `application.log`. API keys and credentials are never intentionally logged.

## Limitations

- LLM-as-a-Judge is itself imperfect and can make evaluation mistakes.
- Therefore, the hallucination score is an **evaluation estimate**, not absolute proof of factual truth.
- Predefined expected behavior and evaluation notes improve consistency but do not eliminate evaluator bias.
- Future-event questions cannot establish actual future truth.
- Mock mode is deterministic and is not a substitute for real model behavior.
- The project intentionally avoids external knowledge retrieval, so it evaluates model behavior rather than independently verifying every fact.

## Future enhancements

- Additional provider adapters.
- More sophisticated calibration of evaluator judgments.
- Human review workflow.
- Statistical confidence intervals over repeated runs.
- More configurable prompt strategies.
- Richer model comparison reports.

## Troubleshooting

**`ModuleNotFoundError`**
- Activate `.venv`.
- Run `pip install -r requirements.txt`.

**Missing API key**
- Copy `.env.example` to `.env`.
- Set `LLM_API_KEY`.
- Set `LLM_PROVIDER=openai`.
- Or use `LLM_PROVIDER=mock`.

**Invalid model**
- Check `LLM_MODEL` and `EVALUATOR_MODEL` for the models available to your provider/account.

**CSV export failure**
- Confirm pandas is installed and the `exports` folder is writable.

**Dataset error**
- Confirm `data/stress_tests.json` exists and contains the required fields.

## Academic project explanation

This project demonstrates software engineering concepts including modular architecture, abstraction, configuration management, JSON persistence, API integration, automated testing, error handling, logging, metrics, and model evaluation. It remains LLM-centric: the central experiment is how an LLM behaves under adversarially difficult prompts.

## Audit note

The repository was generated with a 40-question dataset and mock-provider tests. Run `pytest` and `python app.py` in the generated environment to verify the runtime locally. This README does not claim execution results that have not been observed in the target environment.
