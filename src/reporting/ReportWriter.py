from __future__ import annotations

import csv
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict

from src.config import settings


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    severity: Literal["low", "medium", "high", "critical"]
    description: str


class Assessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    create_report: bool
    reason: str
    findings: list[Finding]


class ReportWriter:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.analyses_dir = output_dir / settings.ANALYSES_SUBDIRECTORY
        self.data_to_check_dir = output_dir / settings.DATA_TO_CHECK_SUBDIRECTORY

    def save_inventory(self, results: list[dict[str, str]], filename: str) -> Path:
        self.data_to_check_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.data_to_check_dir / filename
        with report_path.open("w", newline="", encoding="utf-8") as output_stream:
            fieldnames: tuple[str, ...] = ("repository", "configuration_path", "github_url")
            csv_writer: csv.DictWriter[str] = csv.DictWriter(output_stream, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerows(sorted(results, key=lambda result: (result["repository"], result["configuration_path"])))

        print(f"Collected {len(results)} unique file paths in {report_path}")
        print("No file contents or credentials were downloaded.")
        print("Results are not exhaustive: GitHub limits search to 1,000 matches per query.")
        return report_path

    def save_report(self, github_url: str, assessment: Assessment) -> Path:
        owner, repository = urlparse(github_url).path.strip("/").split("/")[:2]
        if any(part in {"", ".", ".."} for part in (owner, repository)):
            raise ValueError("Invalid repository URL")
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.analyses_dir / f"{owner}__{repository}.md"
        descriptions = "\n\n".join(finding.description for finding in assessment.findings)
        with report_path.open("a", encoding="utf-8") as output_stream:
            output_stream.write(descriptions + "\n\n")
        return report_path
