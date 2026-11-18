from functools import partial
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agent.prompts import SYSTEM_PROMPT
from src.reporting.report_writer import Assessment, ReportWriter


class ReportState(TypedDict):
    github_url: str
    content: str
    assessment: NotRequired[Assessment]


def evaluate(state: ReportState, *, evaluator: Runnable, instructions: str):
    assessment = evaluator.invoke([SystemMessage(content=instructions), HumanMessage(content=state["content"])])
    return {"assessment": Assessment.model_validate(assessment)}


def write_report(state: ReportState, *, writer: ReportWriter):
    if "assessment" not in state:
        raise ValueError("Assessment is missing")
    writer.save_report(state["github_url"], state["assessment"])
    return {}


def route(state: ReportState) -> Literal["save", "__end__"]:
    if "assessment" not in state:
        raise ValueError("Assessment is missing")
    return "save" if state["assessment"].create_report else "__end__"


def build_report_graph(model: ChatOpenAI, system_prompt: str, output_dir: Path) -> CompiledStateGraph:
    evaluator = model.with_structured_output(Assessment, method="json_schema")
    instructions = SYSTEM_PROMPT.format(append_to_system_prompt=system_prompt)
    builder = StateGraph(ReportState)
    builder.add_node("evaluate", partial(evaluate, evaluator=evaluator, instructions=instructions))
    builder.add_node("save", partial(write_report, writer=ReportWriter(output_dir)))
    builder.add_edge(START, "evaluate")
    builder.add_conditional_edges("evaluate", route)
    builder.add_edge("save", END)
    return builder.compile()
