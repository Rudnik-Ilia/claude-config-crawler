import os
from pathlib import Path
from typing import Final

TARGET_FILENAMES: Final[tuple[str, str]] = ("settings.json", "settings.local.json")
CLAUDE_DIRECTORY: Final[str] = ".claude"
REPORT_DIRECTORY: Final[Path] = Path("report")
ANALYSES_SUBDIRECTORY: Final[str] = "analyses"
DATA_TO_CHECK_SUBDIRECTORY: Final[str] = "data_to_check"
OUTPUT_FILE: Final[Path] = REPORT_DIRECTORY / "claude_settings_inventory.csv"
RESULTS_PER_PAGE: Final[int] = 100
MAX_PAGES_PER_QUERY: Final[int] = 10
DELAY_BETWEEN_REQUESTS_SECONDS: Final[int] = 7

LLAMA_CPP_BASE_URL: Final[str] = os.getenv("LLAMA_CPP_BASE_URL", "http://10.100.102.5:8080/v1")
LLAMA_CPP_MODEL: Final[str] = os.getenv("LLAMA_CPP_MODEL", "local-model")
LLAMA_CPP_API_KEY: Final[str] = os.getenv("LLAMA_CPP_API_KEY", "not-needed")
LLM_TEMPERATURE: Final[float] = 0
LLM_TIMEOUT_SECONDS: Final[int] = 300
LLM_MAX_RETRIES: Final[int] = 2
LLM_USE_RESPONSES_API: Final[bool] = False
