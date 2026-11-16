import csv
import sys
from urllib.request import urlopen

with open(sys.argv[1], newline="", encoding="utf-8") as input_stream:
    for row in csv.DictReader(input_stream):
        github_url = row["github_url"]
        raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

        try:
            with urlopen(raw_url) as response:
                print(f"\n{github_url}\n{response.read().decode('utf-8')}")
        except Exception as error:
            print(f"\n{github_url}\nERROR: {error}", file=sys.stderr)
