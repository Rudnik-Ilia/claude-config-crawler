import asyncio
import json
import subprocess

from src.agent.agent import Agent
from src.config.settings import settings
from src.core.cli import ArgsParser
from src.core.github_scanner import GitScaner


def main() -> None:
    args = ArgsParser().parse_args()
    if args.command == "server":
        args.db_filename.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["temporal", "server", "start-dev", "--db-filename", str(args.db_filename)], check=True)
        return
    if args.command in {"worker", "result"}:
        from src.runner.runner import TemporalRunner

        runner = TemporalRunner()
        if args.command == "worker":
            asyncio.run(runner.work())
        else:
            print(json.dumps(asyncio.run(runner.result(args.execution_id)), ensure_ascii=False, indent=2))
        return
    if args.command == "scan":
        GitScaner(settings).run()
        return

    if args.csv is None:
        raise ValueError("CSV path is required: provide --csv")
    if args.temporal:
        from src.runner.runner import AnalysisRequest, TemporalRunner

        if not args.execution_id:
            raise ValueError("Execution ID is required: provide --execution-id")
        request = AnalysisRequest(
            csv_path=str(args.csv.resolve()),
            system_prompt=args.system_prompt,
            report_dir=str((args.report_dir / args.execution_id).resolve()),
            base_url=args.base_url,
            model_name=args.model,
        )
        execution_id = asyncio.run(TemporalRunner().start(args.execution_id, request))
        print(f"Analysis submitted: {execution_id}. Start claude-scan worker to process it.")
        return
    Agent(args.csv, args.system_prompt, args.report_dir, args.base_url, args.model).run()
    print(f"Analysis complete. Reports: {args.report_dir / settings.ANALYSES_SUBDIRECTORY}")


if __name__ == "__main__":
    main()
