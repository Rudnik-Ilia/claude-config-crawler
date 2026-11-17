import json
import subprocess
import time
from types import ModuleType

from src.config import settings
from src.core.gh_builder import GH
from src.reporting.ReportWriter import ReportWriter


class GitScaner:
    def __init__(self, settings: ModuleType) -> None:
        self.settings = settings

    def search_paths(self, filename: str) -> list[dict[str, str]]:
        found_paths = []
        github_query = f"{filename} in:path path:{self.settings.CLAUDE_DIRECTORY}"

        for page_number in range(1, self.settings.MAX_PAGES_PER_QUERY + 1):
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

            if len(search_items) < self.settings.RESULTS_PER_PAGE:
                break
            time.sleep(self.settings.DELAY_BETWEEN_REQUESTS_SECONDS)

        return found_paths


    def _filter_unique_results(self, results: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
        return {
            (result["repository"], result["configuration_path"]): result
            for result in results
        }

    def run(self) -> None:
        all_results = []
        for filename in self.settings.TARGET_FILENAMES:
            all_results.extend(self.search_paths(filename))
            time.sleep(self.settings.DELAY_BETWEEN_REQUESTS_SECONDS)

        unique_results = self._filter_unique_results(all_results)

        writer = ReportWriter(self.settings.OUTPUT_FILE.parent)
        writer.save_inventory(list(unique_results.values()), self.settings.OUTPUT_FILE.name)



if __name__ == "__main__":
    GitScaner(settings).run()
