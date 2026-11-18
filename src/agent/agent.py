import sys
from pathlib import Path

from langchain_openai.chat_models.base import ChatOpenAI

from src.agent.graph import build_report_graph
from src.agent.llm import build_model
from src.core.data_fetching import DataFetcher
from src.core.exceptions import AgentProcessingError


class Agent:
    def __init__(
        self, csv_path: Path, system_prompt: str, report_dir: Path, base_url: str, model_name: str, deduplicate: bool = False) -> None:
        self._fetcher = DataFetcher(csv_path)
        llm_model: ChatOpenAI = build_model(base_url, model_name)
        self._report_graph = build_report_graph(llm_model, system_prompt, report_dir, deduplicate=deduplicate)

    def process_file(self, github_url: str, content: str) -> bool:
        try:
            result = self._report_graph.invoke({"github_url": github_url, "content": content})
            return result["assessment"].create_report
        except Exception as error:
            raise AgentProcessingError(github_url, error) from error

    def run(self) -> None:
        for github_url, content in self._fetcher.fetch_files():
            print(f"Processing: {github_url} ...", end="", flush=True)
            try:
                create_report = self.process_file(github_url, content)
                print(f"\r{github_url}: create_report={create_report}    ")
            except AgentProcessingError as error:
                print(flush=True)
                print(str(error), file=sys.stderr, flush=True)
                continue
