import argparse
from pathlib import Path

from src.config import settings


class ArgsParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        commands = self.parser.add_subparsers(dest="command", required=True)
        commands.add_parser("scan", help="Find GitHub configurations and save a CSV")
        server = commands.add_parser("server", help="Start the persistent Temporal development server")
        server.add_argument("--db-filename", type=Path, default=settings.TEMPORAL_DATABASE_FILE)
        commands.add_parser("worker", help="Run the Temporal worker; restart to resume pending analysis")
        result = commands.add_parser("result", help="Wait for a Temporal execution and print its results")
        result.add_argument("--execution-id", required=True)
        run = commands.add_parser("analyze", help="Scan and analyze configurations with the agent")
        run.add_argument("--system-prompt", required=True)
        run.add_argument("--csv", type=Path, help="Process an existing CSV without scanning")
        run.add_argument("--report-dir", type=Path, default=settings.REPORT_DIRECTORY)
        run.add_argument("--base-url", default=settings.LLAMA_CPP_BASE_URL)
        run.add_argument("--model", default=settings.LLAMA_CPP_MODEL)
        run.add_argument("--temporal", action="store_true", help="Submit analysis to Temporal")
        run.add_argument("--execution-id", help="Unique Temporal execution ID; required with --temporal")

    def parse_args(self) -> argparse.Namespace:
        return self.parser.parse_args()
