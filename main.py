from src.agent.runner import Agent
from src.config import settings
from src.core.cli import ArgsParser
from src.core.github_scanner import GitScaner


def main() -> None:
    args = ArgsParser().parse_args()
    if args.command == "scan":
        GitScaner(settings).run()
        return

    if args.csv is None:
        raise ValueError("CSV path is required: provide --csv")
    Agent(args.csv, args.system_prompt, args.report_dir, args.base_url, args.model).run()
    print(f"Analysis complete. Reports: {args.report_dir / settings.ANALYSES_SUBDIRECTORY}")


if __name__ == "__main__":
    main()
