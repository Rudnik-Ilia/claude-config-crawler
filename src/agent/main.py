from langchain_openai.chat_models.base import ChatOpenAI

from src.agent.cli import ArgsParser
from src.agent.graph import build_report_graph
from src.agent.llm import build_model
from src.core.data_fetching import DataFetcher


def main() -> None:
    args = ArgsParser().parse_args()
    if not args.csv:
        raise ValueError("CSV path is required: provide --csv")
    fetcher = DataFetcher(args.csv)
    llm_model: ChatOpenAI = build_model(args.base_url, args.model)

    report_graph = build_report_graph(llm_model, args.system_prompt, args.report_dir)
    for github_url, content in fetcher.fetch_files():
        print(f"Processing: {github_url} ...", end="", flush=True)
        result = report_graph.invoke({"github_url": github_url, "content": content})
        print(f"\r{github_url}: create_report={result['assessment'].create_report}    ")


if __name__ == "__main__":
    main()
