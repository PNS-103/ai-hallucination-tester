"""JSON result persistence and CSV export."""

from datetime import datetime
from pathlib import Path
import pandas as pd
from utils.json_utils import save_json, load_json


class ResultService:
    def __init__(self, results_dir: Path, exports_dir: Path):
        self.results_dir = results_dir
        self.exports_dir = exports_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def save_run(self, run: dict) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.results_dir / f"test_run_{timestamp}_{run['run_id']}.json"
        save_json(path, run)
        return path

    def load_runs(self) -> list[dict]:
        runs = []
        for path in sorted(self.results_dir.glob("*.json")):
            try:
                runs.append(load_json(path))
            except Exception:
                continue
        return runs

    def export_csv(self, run: dict) -> Path:
        rows = []
        response_by_id = {r["question_id"]: r for r in run.get("responses", [])}
        for evaluation in run.get("evaluations", []):
            response = response_by_id.get(evaluation.get("question_id"), {})
            row = {
                "run_id": run.get("run_id"),
                "question_id": evaluation.get("question_id"),
                "category": evaluation.get("category"),
                "question": response.get("question"),
                "answer": response.get("answer"),
                "model": response.get("model"),
                "latency": response.get("latency"),
                "hallucination": evaluation.get("hallucination"),
                "severity": evaluation.get("severity"),
                "confidence": evaluation.get("confidence"),
                "hallucination_type": evaluation.get("hallucination_type"),
                "correctness": evaluation.get("correctness"),
                "should_have_refused_or_corrected": evaluation.get(
                    "should_have_refused_or_corrected"
                ),
                "reason": evaluation.get("reason"),
                "unsupported_claims": "; ".join(evaluation.get("unsupported_claims", [])),
            }
            rows.append(row)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.exports_dir / f"export_{timestamp}_{run['run_id']}.csv"
        pd.DataFrame(rows).to_csv(path, index=False)
        return path
