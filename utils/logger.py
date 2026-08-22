"""Safe application logging."""

import logging
from pathlib import Path


def get_logger() -> logging.Logger:
    logger = logging.getLogger("hallucination_tester")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(Path("application.log"), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    return logger
