import csv
import sys
from collections.abc import Iterator
from urllib.request import urlopen


def fetch_files(csv_path: str) -> Iterator[tuple[str, str]]:
    with open(csv_path, newline="", encoding="utf-8") as input_stream:
        for row in csv.DictReader(input_stream):
            github_url = row["github_url"]
            raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

            try:
                with urlopen(raw_url) as response:
                    content = response.read().decode("utf-8")
            except Exception as error:
                print(f"\n{github_url}\nERROR: {error}", file=sys.stderr)
                continue
            yield github_url, content


if __name__ == "__main__":
    for github_url, content in fetch_files(sys.argv[1]):
        print(f"\n{github_url}\n{content}")
