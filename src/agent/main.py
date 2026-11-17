import argparse
import os
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.pregel.main import RunnableConfig
from pydantic import SecretStr

from src.agent.reports import build_report_graph
from src.core.get_github_file import fetch_files


def build_model(base_url: str, model_name: str) -> ChatOpenAI:
    return ChatOpenAI(
        base_url=base_url,
        api_key=SecretStr(os.getenv("LLAMA_CPP_API_KEY", "not-needed")),
        model=model_name,
        temperature=0,
    )


def build_graph(base_url: str, model_name: str):
    model = build_model(base_url, model_name)

    def call_model(state: MessagesState):
        return {"messages": [model.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_edge(START, "model")
    return builder.compile(checkpointer=InMemorySaver())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--system-prompt", required=True)
    parser.add_argument("--user-prompt")
    parser.add_argument("--csv")
    parser.add_argument("--report-dir", type=Path, default=Path("report/analyses"))
    parser.add_argument(
        "--base-url",
        default=os.getenv("LLAMA_CPP_BASE_URL", "http://10.100.102.5:8080/v1"),
    )
    parser.add_argument("--model", default=os.getenv("LLAMA_CPP_MODEL", "local-model"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.csv:
        report_graph = build_report_graph(build_model(args.base_url, args.model), args.system_prompt, args.report_dir)
        for github_url, content in fetch_files(args.csv):
            result = report_graph.invoke({"github_url": github_url, "content": content})
            print(f"{github_url}: create_report={result['assessment'].create_report}")
        return

    graph = build_graph(args.base_url, args.model)
    config = RunnableConfig({"configurable": {"thread_id": "cli"}})
    user_prompt = args.user_prompt
    first_message = True

    while True:
        try:
            if user_prompt is None:
                user_prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_prompt.lower() in {"exit", "quit"}:
            break
        if not user_prompt:
            user_prompt = None
            continue

        state: MessagesState = {"messages": [HumanMessage(content=user_prompt)]}
        if first_message:
            state["messages"].insert(0, SystemMessage(content=args.system_prompt))

        result = graph.invoke(state, config=config)
        print(f"Assistant: {result['messages'][-1].content}")
        first_message = False
        user_prompt = None


if __name__ == "__main__":
    main()
