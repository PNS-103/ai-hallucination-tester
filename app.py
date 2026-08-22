"""Console entry point for AI Hallucination Stress Tester."""

import sys
from datetime import datetime
from uuid import uuid4

from config.settings import Settings
from models.model_provider import OpenAIProvider, MockProvider
from services.stress_test_service import StressTestService
from services.llm_service import LLMService
from services.evaluation_service import EvaluationService
from services.scoring_service import ScoringService
from services.comparison_service import ComparisonService
from services.result_service import ResultService
from utils.logger import get_logger


def make_provider(settings, model=None):
    selected = model or settings.model
    if settings.provider == "mock":
        return MockProvider(selected)
    return OpenAIProvider(settings.api_key, selected, settings.temperature, settings.max_tokens)


class Application:
    def __init__(self):
        self.settings = Settings()
        self.settings.ensure_directories()
        self.logger = get_logger()
        self.result_service = ResultService(self.settings.results_dir, self.settings.exports_dir)
        self.stress_service = StressTestService(self.settings.data_file)
        self.questions = self.stress_service.load_questions()
        self.categories = None
        self.question_count = 10
        self.last_run = None

    def run(self):
        print("\n" + "=" * 58)
        print("        AI HALLUCINATION STRESS TESTER")
        print("=" * 58)
        print("Provider:", self.settings.provider)
        print("Model:", self.settings.model)
        while True:
            print("""
1. Run Stress Test
2. Select Categories
3. Configure Model
4. View Previous Results
5. Compare Models
6. Export Results
7. View Dataset Statistics
8. Exit
""")
            choice = input("Enter your choice: ").strip()
            try:
                if choice == "1": self.run_stress_test()
                elif choice == "2": self.select_categories()
                elif choice == "3": self.configure_model()
                elif choice == "4": self.view_results()
                elif choice == "5": self.compare_models()
                elif choice == "6": self.export_results()
                elif choice == "7": self.dataset_stats()
                elif choice == "8":
                    print("Goodbye.")
                    return
                else:
                    print("Invalid choice. Please enter 1-8.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
            except Exception as exc:
                self.logger.exception("Unhandled application error")
                print(f"Error: {exc}")

    def run_stress_test(self):
        provider = make_provider(self.settings)
        llm = LLMService(provider)
        evaluator = EvaluationService(
            make_provider(self.settings, self.settings.evaluator_model),
            self.settings.evaluation_retries
        )
        selected = self.stress_service.select(
            self.questions, self.categories, self.question_count, self.settings.randomize
        )
        if not selected:
            print("No questions match the current selection.")
            return

        run_id = uuid4().hex[:8]
        responses, evaluations = [], []
        print(f"\nRun ID: {run_id}")
        for index, question in enumerate(selected, 1):
            print("\n" + "=" * 58)
            print(f"TEST {index} / {len(selected)} | {question.category} | {question.id}")
            print(f"Difficulty: {question.difficulty}")
            print("\nQUESTION:\n" + question.question)
            response = llm.run(question)
            responses.append(response.to_dict())
            print("\nLLM RESPONSE:\n" + (response.answer or f"[FAILED] {response.error}"))
            if response.status != "success":
                print("Evaluation skipped because the LLM call failed.")
                evaluations.append({
                    "question_id": question.id, "category": question.category,
                    "status": "failed", "reason": response.error or "LLM failure"
                })
                continue

            print("\nEvaluating...")
            evaluation = evaluator.evaluate(question, response.answer).to_dict()
            evaluation["question_id"] = question.id
            evaluation["category"] = question.category
            evaluations.append(evaluation)
            print(f"HALLUCINATION: {'YES' if evaluation['hallucination'] else 'NO'}")
            print(f"SEVERITY: {evaluation['severity']}/5")
            print(f"CONFIDENCE: {evaluation['confidence']:.2f}")
            print(f"TYPE: {evaluation['hallucination_type']}")
            print(f"CORRECTNESS: {evaluation['correctness']}")
            print("REASON:", evaluation["reason"])
            if index < len(selected):
                input("\nPress ENTER to continue...")

        summary = ScoringService.summary(evaluations, responses)
        categories = ScoringService.categories(evaluations, [q.to_dict() for q in selected])
        run = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "model": settings_model(self.settings),
            "evaluator_model": self.settings.evaluator_model,
            "configuration": {
                "provider": self.settings.provider,
                "question_count": len(selected),
                "randomize": self.settings.randomize,
                "evaluation_retries": self.settings.evaluation_retries,
            },
            "test_questions": [q.to_dict() for q in selected],
            "responses": responses,
            "evaluations": evaluations,
            "summary": summary,
            "category_statistics": categories,
        }
        path = self.result_service.save_run(run)
        self.last_run = run
        print_summary(run)
        print(f"\nRun saved to: {path}")

    def select_categories(self):
        print("\nCategories:")
        for i, category in enumerate(sorted({q.category for q in self.questions}), 1):
            print(f"{i}. {category}")
        raw = input("Enter numbers separated by commas, or ALL: ").strip().lower()
        if raw == "all" or not raw:
            self.categories = None
            print("All categories selected.")
            return
        names = sorted({q.category for q in self.questions})
        try:
            selected = {names[int(x)-1] for x in raw.split(",")}
            self.categories = selected
            print("Selected:", ", ".join(sorted(selected)))
        except (ValueError, IndexError):
            print("Invalid category selection.")

    def configure_model(self):
        print(f"\nCurrent provider: {self.settings.provider}")
        provider = input("Provider [mock/openai] (Enter to keep): ").strip().lower()
        if provider in {"mock", "openai"}:
            self.settings.provider = provider
        model = input(f"LLM model [{self.settings.model}]: ").strip()
        if model: self.settings.model = model
        evaluator = input(f"Evaluator model [{self.settings.evaluator_model}]: ").strip()
        if evaluator: self.settings.evaluator_model = evaluator
        raw = input(f"Questions [{self.question_count}]: ").strip()
        if raw.isdigit() and int(raw) > 0:
            self.question_count = min(int(raw), len(self.questions))
        print("Configuration updated.")

    def view_results(self):
        runs = self.result_service.load_runs()
        if not runs:
            print("No saved results.")
            return
        for run in runs:
            s = run.get("summary", {})
            print(f"{run.get('run_id')} | {run.get('timestamp')} | {run.get('model')} | "
                  f"Hallucination {s.get('hallucination_rate', 0):.1f}%")

    def compare_models(self):
        runs = self.result_service.load_runs()
        rows = ComparisonService.compare(runs)
        if not rows:
            print("No runs to compare.")
            return
        print("\nMODEL COMPARISON")
        print("-" * 90)
        print(f"{'Model':25} {'Hallucination':15} {'Correct':12} {'Severity':10} {'Confidence':12} {'Latency':10}")
        for r in rows:
            print(f"{r['model'][:25]:25} {r['hallucination_rate']:>8.2f}%       "
                  f"{r['correct_response_rate']:>6.2f}%    {r['average_severity']:>6.2f}     "
                  f"{r['average_confidence']:>7.2f}       {r['average_latency']:>7.2f}s")

    def export_results(self):
        run = self.last_run
        if not run:
            runs = self.result_service.load_runs()
            run = runs[-1] if runs else None
        if not run:
            print("No result available to export.")
            return
        path = self.result_service.export_csv(run)
        print(f"CSV exported to: {path}")

    def dataset_stats(self):
        from collections import Counter
        counts = Counter(q.category for q in self.questions)
        print(f"\nTotal questions: {len(self.questions)}")
        for category, count in sorted(counts.items()):
            print(f"{category:25} {count}")


def settings_model(settings):
    return settings.model


def print_summary(run):
    s = run["summary"]
    print("\n" + "=" * 58)
    print("                 TEST RUN SUMMARY")
    print("=" * 58)
    for key, label in [
        ("model", "Model"), ("evaluator_model", "Evaluator"),
    ]:
        print(f"{label}: {run[key]}")
    for key, label in [
        ("total_questions","Total Questions"), ("successful_tests","Successful Tests"),
        ("failed_tests","Failed Tests"), ("evaluated_responses","Evaluated Responses"),
        ("hallucinated_responses","Hallucinated Responses"),
        ("non_hallucinated_responses","Non-Hallucinated Responses"),
    ]:
        print(f"{label}: {s[key]}")
    print(f"Hallucination Rate: {s['hallucination_rate']:.2f}%")
    print(f"Correct Response Rate: {s['correct_response_rate']:.2f}%")
    print(f"Average Severity: {s['average_severity']:.2f}")
    print(f"Average Evaluator Confidence: {s['average_evaluator_confidence']:.2f}")
    print(f"Average Latency: {s['average_latency']:.2f}s")
    print(f"Weighted Hallucination Score: {s['weighted_hallucination_score']:.2f}%")
    print("\nCATEGORY PERFORMANCE")
    for category, stats in sorted(run["category_statistics"].items()):
        print(f"{category:25} Hallucination {stats['hallucination_rate']:6.2f}% | "
              f"Accuracy {stats['accuracy']:6.2f}%")


if __name__ == "__main__":
    try:
        Application().run()
    except Exception as exc:
        print(f"Startup error: {exc}")
        sys.exit(1)
