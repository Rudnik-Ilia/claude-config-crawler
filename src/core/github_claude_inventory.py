import csv
import json
import subprocess
import time
from pathlib import Path
from typing import Final

TARGET_FILENAMES: Final[tuple[str, str]] = ("settings.json", "settings.local.json")
OUTPUT_FILE: Final[Path] = Path("./report/claude_settings_inventory.csv")
RESULTS_PER_PAGE: Final[int] = 100
MAX_PAGES_PER_QUERY: Final[int]  = 10
DELAY_BETWEEN_REQUESTS_SECONDS: Final[int]  = 7


def search_paths(filename: str) -> list[dict[str, str]]:
    found_paths = []
    github_query = f"{filename} in:path path:.claude"

    for page_number in range(1, MAX_PAGES_PER_QUERY + 1):
        command = [
            "gh", "api", "--method", "GET", "search/code",
            "-f", f"q={github_query}",
            "-f", f"per_page={RESULTS_PER_PAGE}",
            "-f", f"page={page_number}",
        ]
        response = subprocess.run(command, capture_output=True, text=True, check=False)
        if response.returncode != 0:
            raise RuntimeError(f"GitHub search failed: {response.stderr.strip()}")
        search_result = json.loads(response.stdout)
        search_items = search_result.get("items", [])

        for search_item in search_items:
            configuration_path = search_item.get("path", "")
            if not configuration_path.endswith(f".claude/{filename}"):
                continue
            found_paths.append({
                "repository": search_item["repository"]["full_name"],
                "configuration_path": configuration_path,
                "github_url": search_item["html_url"],
            })

        if len(search_items) < RESULTS_PER_PAGE:
            break
        time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

    return found_paths


def main() -> None:
    all_results = []
    for filename in TARGET_FILENAMES:
        all_results.extend(search_paths(filename))
        time.sleep(DELAY_BETWEEN_REQUESTS_SECONDS)

    unique_results = {
        (result["repository"], result["configuration_path"]): result
        for result in all_results
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as output_stream:
        fieldnames = ("repository", "configuration_path", "github_url")
        csv_writer = csv.DictWriter(output_stream, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(
            sorted(unique_results.values(), key=lambda result: (
                result["repository"], result["configuration_path"]
            ))
        )

    print(f"Collected {len(unique_results)} unique file paths in {OUTPUT_FILE}")
    print("No file contents or credentials were downloaded.")
    print("Results are not exhaustive: GitHub limits search to 1,000 matches per query.")


if __name__ == "__main__":
    main()
