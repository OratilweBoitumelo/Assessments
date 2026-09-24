"""Central configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT_DIR / "reports"             # Allure results live here
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"

load_dotenv(ROOT_DIR / ".env")

def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable '{name}'. "
            "Copy .env.example to .env and fill it in."
        )
    return value

BASE_URL = _require("BASE_URL").rstrip("/")
USERNAME = _require("ORANGEHRM_USERNAME")
PASSWORD = _require("ORANGEHRM_PASSWORD")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "20"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
