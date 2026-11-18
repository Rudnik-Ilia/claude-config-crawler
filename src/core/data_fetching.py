import csv
import sys
from collections.abc import Iterator
from pathlib import Path
from urllib.request import urlopen

from src.core.exceptions import ReadLineCSVExeption


class DataFetcher:
    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"The provided path is not exists {self.csv_path}")
        if not self.csv_path.is_file():
            raise ValueError(f"CSV path must point to a file: {self.csv_path}")
        with self.csv_path.open(newline="", encoding="utf-8") as input_stream:
            fieldnames = csv.DictReader(input_stream).fieldnames
            if not fieldnames or "github_url" not in fieldnames:
                raise ValueError("CSV must contain a github_url column")

    def iter_urls(self) -> Iterator[str]:
        with self.csv_path.open(newline="", encoding="utf-8") as input_stream:
            for row in csv.DictReader(input_stream):
                yield row["github_url"]

    @staticmethod
    def fetch_file(github_url: str) -> str:
        raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        with urlopen(raw_url) as response:
            return response.read().decode("utf-8")

    def fetch_files(self) -> Iterator[tuple[str, str]]:
        for github_url in self.iter_urls():
            try:
                content = self.fetch_file(github_url)
            except ReadLineCSVExeption as error:
                print(f"\n{github_url}\nERROR: {error}", file=sys.stderr)
                continue
            yield github_url, content
