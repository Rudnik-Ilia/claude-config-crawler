import argparse
from pathlib import Path

from src.config import settings


class ArgsParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--system-prompt", required=True)
        self.parser.add_argument("--csv")
        self.parser.add_argument("--report-dir", type=Path, default=settings.REPORT_DIRECTORY)
        self.parser.add_argument("--base-url", default=settings.LLAMA_CPP_BASE_URL)
        self.parser.add_argument("--model", default=settings.LLAMA_CPP_MODEL)

    def parse_args(self) -> argparse.Namespace:
        return self.parser.parse_args()
