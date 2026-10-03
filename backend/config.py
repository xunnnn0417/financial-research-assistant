"""Small, explicit configuration module for V1."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
REQUEST_TIMEOUT_SECONDS = 10.0
