"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


@dataclass
class Settings:
    provider: str = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini").strip()
    evaluator_model: str = os.getenv("EVALUATOR_MODEL", "gpt-4.1-mini").strip()
    api_key: str = os.getenv("LLM_API_KEY", "").strip()
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "800"))
    evaluation_retries: int = int(os.getenv("EVALUATION_RETRIES", "1"))
    randomize: bool = os.getenv("RANDOMIZE", "true").lower() in {"1", "true", "yes"}

    data_file: Path = ROOT_DIR / "data" / "stress_tests.json"
    results_dir: Path = ROOT_DIR / "results"
    exports_dir: Path = ROOT_DIR / "exports"

    def ensure_directories(self) -> None:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        if self.provider not in {"openai", "mock"}:
            raise ValueError(f"Unsupported provider: {self.provider}")
        if self.provider == "openai" and not self.api_key:
            raise ValueError("LLM_API_KEY is missing. Configure it in .env.")
        if not self.model:
            raise ValueError("LLM_MODEL cannot be empty.")
        if not self.evaluator_model:
            raise ValueError("EVALUATOR_MODEL cannot be empty.")
        if not 0 <= self.temperature <= 2:
            raise ValueError("TEMPERATURE must be between 0 and 2.")
        if self.max_tokens <= 0:
            raise ValueError("MAX_TOKENS must be positive.")
        if self.evaluation_retries < 0:
            raise ValueError("EVALUATION_RETRIES cannot be negative.")
