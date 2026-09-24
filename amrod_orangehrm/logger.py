"""Consistent logging for the whole framework."""

import logging
import config

ROOT_NAME = "orangehrm"
LOG_DIR = config.REPORTS_DIR / "logs"
LOG_FILE = LOG_DIR / "test_run.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s"

def setup_logging(level: str = "INFO") -> None:
    """Create the log file (overwritten each run). Call once, at the start of the run."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(ROOT_NAME)
    logger.setLevel(level)
    logger.propagate = False  
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"{ROOT_NAME}.{name}")

def _flush() -> None:
    for handler in logging.getLogger(ROOT_NAME).handlers:
        handler.flush()

def log_position() -> int:
    """Current size of the log file, used to slice out one scenario's lines later."""
    _flush()
    return LOG_FILE.stat().st_size if LOG_FILE.exists() else 0

def read_log_since(position: int) -> str:
    _flush()
    with open(LOG_FILE, "rb") as file:
        file.seek(position)
        return file.read().decode("utf-8", errors="replace")
