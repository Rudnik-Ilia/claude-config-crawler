import json
import subprocess
import time
from pathlib import Path
from types import ModuleType

from src.core.gh_builder import GH
from src.reporting.ReportWriter import ReportWriter


class GitScaner:
    def __init__(self, settings: ModuleType) -> None:
        self.settings = settings

    def _show_progress(self, completed: int, total: int, message: str) -> None:
        percent = completed * 100 // total
        filled = percent * 20 // 100
        bar = "=" * filled + "." * (20 - filled)
        print(f"\r[{bar}] {percent:3d}% | {message}".ljust(160), end="", flush=True)

    def search_paths(self, filename: str) -> list[dict[str, str]]:
        found_paths = []
        github_query = f"{filename} in:path path:{self.settings.CLAUDE_DIRECTORY}"
        total = len(self.settings.TARGET_FILENAMES) * self.settings.MAX_PAGES_PER_QUERY + 1
        offset = self.settings.TARGET_FILENAMES.index(filename) * self.settings.MAX_PAGES_PER_QUERY

        for page_number in range(1, self.settings.MAX_PAGES_PER_QUERY + 1):
            self._show_progress(offset + page_number - 1, total, f"Requesting {filename}, page {page_number}")
            command = (
                GH.api("search/code")
                .method("GET")
                .field("q", github_query)
                .field("per_page", self.settings.RESULTS_PER_PAGE)
                .field("page", page_number)
                .build()
            )
            response = subprocess.run(command, capture_output=True, text=True, check=False)
            if response.returncode != 0:
                print()
                raise RuntimeError(f"GitHub API search failed: {response.stderr.strip()}")
            search_result = json.loads(response.stdout)
            search_items = search_result.get("items", [])

            for search_item in search_items:
                configuration_path = search_item.get("path", "")
                if not configuration_path.endswith(f"{self.settings.CLAUDE_DIRECTORY}/{filename}"):
                    continue
                found_paths.append({
                    "repository": search_item["repository"]["full_name"],
                    "configuration_path": configuration_path,
                    "github_url": search_item["html_url"],
                })

            self._show_progress(offset + page_number, total, f"{filename}, page {page_number}: {len(found_paths)} files found")
            if len(search_items) < self.settings.RESULTS_PER_PAGE:
                break
            self._show_progress(offset + page_number, total, f"{filename}: waiting {self.settings.DELAY_BETWEEN_REQUESTS_SECONDS}s")
            time.sleep(self.settings.DELAY_BETWEEN_REQUESTS_SECONDS)

        return found_paths


    def _filter_unique_results(self, results: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
        return {
            (result["repository"], result["configuration_path"]): result
            for result in results
        }

    def run(self) -> Path:
        all_results = []
        total = len(self.settings.TARGET_FILENAMES) * self.settings.MAX_PAGES_PER_QUERY + 1
        self._show_progress(0, total, "Starting GitHub scan")
        for index, filename in enumerate(self.settings.TARGET_FILENAMES, start=1):
            all_results.extend(self.search_paths(filename))
            self._show_progress(
                index * self.settings.MAX_PAGES_PER_QUERY,
                total,
                f"{filename} complete | {len(all_results)} files | waiting {self.settings.DELAY_BETWEEN_REQUESTS_SECONDS}s",
            )
            time.sleep(self.settings.DELAY_BETWEEN_REQUESTS_SECONDS)

        unique_results = self._filter_unique_results(all_results)

        writer = ReportWriter(self.settings.OUTPUT_FILE.parent)
        self._show_progress(total - 1, total, f"Saving CSV: {len(unique_results)} unique files")
        print()
        report_path = writer.save_inventory(list(unique_results.values()), self.settings.OUTPUT_FILE.name)
        self._show_progress(total, total, f"Scan complete: {report_path}")
        print()
        return report_path
