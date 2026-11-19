from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True)

    TARGET_FILENAMES: tuple[str, str] = ("settings.json", "settings.local.json")
    CLAUDE_DIRECTORY: str = ".claude"
    REPORT_DIRECTORY: Path = Path("report")
    ANALYSES_SUBDIRECTORY: str = "analyses"
    DATA_TO_CHECK_SUBDIRECTORY: str = "data_to_check"
    OUTPUT_FILE: Path = Path("report/claude_settings_inventory.csv")
    RESULTS_PER_PAGE: int = 100
    MAX_PAGES_PER_QUERY: int = 10
    DELAY_BETWEEN_REQUESTS_SECONDS: int = 7

    LLAMA_CPP_BASE_URL: str = ""
    LLAMA_CPP_MODEL: str = "local-model"
    LLAMA_CPP_API_KEY: str = "not-needed"
    LLM_TEMPERATURE: float = 0
    LLM_TIMEOUT_SECONDS: int = 900
    LLM_MAX_RETRIES: int = 2
    LLM_USE_RESPONSES_API: bool = False

    TEMPORAL_ADDRESS: str = "localhost:7233"
    TEMPORAL_DATABASE_FILE: Path = Path("src/runner/database/temporal.sqlite")
    TEMPORAL_TASK_QUEUE: str = "claude-analysis"
    TEMPORAL_ACTIVITY_TIMEOUT_SECONDS: int = 1200
    TEMPORAL_HEARTBEAT_SECONDS: int = 5
    TEMPORAL_HEARTBEAT_TIMEOUT_SECONDS: int = 30
    TEMPORAL_MAX_ATTEMPTS: int = 3


settings = Settings()
