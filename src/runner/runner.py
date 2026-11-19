import asyncio
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy, WorkflowIDReusePolicy
from temporalio.exceptions import ActivityError
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from src.agent.agent import Agent
    from src.config.settings import settings
    from src.core.data_fetching import DataFetcher


@dataclass
class AnalysisRequest:
    csv_path: str
    system_prompt: str
    report_dir: str
    base_url: str
    model_name: str
    activity_timeout_seconds: int = settings.TEMPORAL_ACTIVITY_TIMEOUT_SECONDS
    heartbeat_timeout_seconds: int = settings.TEMPORAL_HEARTBEAT_TIMEOUT_SECONDS
    maximum_attempts: int = settings.TEMPORAL_MAX_ATTEMPTS


class AnalysisActivities:
    @activity.defn
    async def read_inventory(self, request: AnalysisRequest) -> list[str]:
        return await asyncio.to_thread(self._read_inventory, request.csv_path)

    def _read_inventory(self, csv_path: str) -> list[str]:
        return list(dict.fromkeys(DataFetcher(csv_path).iter_urls()))

    def _process_file(self, request: AnalysisRequest, github_url: str) -> bool:
        content = DataFetcher.fetch_file(github_url)
        agent = Agent(
            Path(request.csv_path), request.system_prompt, Path(request.report_dir), request.base_url, request.model_name,
            deduplicate=True,
        )
        return agent.process_file(github_url, content)

    @activity.defn
    async def process_file(self, request: AnalysisRequest, github_url: str) -> dict[str, str | bool]:
        print(f"Processing: {github_url} ...", flush=True)
        task = asyncio.create_task(asyncio.to_thread(self._process_file, request, github_url))
        try:
            while not task.done():
                activity.heartbeat(github_url)
                await asyncio.wait({task}, timeout=settings.TEMPORAL_HEARTBEAT_SECONDS)
            create_report = await task
        finally:
            if not task.done():
                await asyncio.shield(task)
        print(f"{github_url}: create_report={create_report}", flush=True)
        return {"github_url": github_url, "create_report": create_report}


@workflow.defn
class AnalysisWorkflow:
    @workflow.run
    async def run(self, request: AnalysisRequest) -> list[dict[str, str | bool]]:
        urls = await workflow.execute_activity_method(
            AnalysisActivities.read_inventory,
            request,
            start_to_close_timeout=timedelta(minutes=1),
            retry_policy=RetryPolicy(maximum_attempts=1),
        )
        results: list[dict[str, str | bool]] = []
        for github_url in urls:
            try:
                result = await workflow.execute_activity_method(
                    AnalysisActivities.process_file,
                    args=[request, github_url],
                    start_to_close_timeout=timedelta(seconds=request.activity_timeout_seconds),
                    heartbeat_timeout=timedelta(seconds=request.heartbeat_timeout_seconds),
                    retry_policy=RetryPolicy(maximum_attempts=request.maximum_attempts),
                )
                results.append({**result, "status": "reported" if result["create_report"] else "no_findings"})
            except ActivityError as error:
                message = str(error.cause or error)
                workflow.logger.error("Skipped %s: %s", github_url, message)
                results.append({"github_url": github_url, "status": "failed", "error": message})
        return results


class TemporalRunner:
    def __init__(self, address: str = settings.TEMPORAL_ADDRESS, task_queue: str = settings.TEMPORAL_TASK_QUEUE) -> None:
        self.address = address
        self.task_queue = task_queue

    async def work(self) -> None:
        client = await Client.connect(self.address)
        activities = AnalysisActivities()
        worker = Worker(
            client,
            task_queue=self.task_queue,
            workflows=[AnalysisWorkflow],
            activities=[activities.read_inventory, activities.process_file],
            max_concurrent_activities=1,
        )
        print(f"Worker ready: {self.address}, queue={self.task_queue}", flush=True)
        await worker.run()

    async def start(self, execution_id: str, request: AnalysisRequest) -> str:
        client = await Client.connect(self.address)
        handle = await client.start_workflow(
            AnalysisWorkflow.run,
            request,
            id=execution_id,
            task_queue=self.task_queue,
            id_reuse_policy=WorkflowIDReusePolicy.REJECT_DUPLICATE,
        )
        return handle.id

    async def result(self, execution_id: str) -> list[dict[str, str | bool]]:
        client = await Client.connect(self.address)
        return await client.get_workflow_handle(execution_id).result()
