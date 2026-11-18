# Claude Settings Scan

Finds Claude configuration files on GitHub and analyzes them using LangGraph and a llama.cpp model.

## How it works

1. `scan` searches for `.claude/settings.json` and `.claude/settings.local.json` and saves their URLs to CSV.
2. `analyze` downloads each file and sends it to the model with the system prompt and a fixed response schema.
3. When `create_report` is true, finding descriptions are saved as Markdown with a link to the source file.
4. Analysis errors are logged and processing continues with the next file.

Settings are in `src/config/settings.py`. CSV files are saved in `report/data_to_check/`.
Ordinary analysis reports are saved in `report/analyses/`.

## Usage

Install dependencies and activate the environment:

```bash
uv sync
source .venv/bin/activate
```

Scan GitHub:

```bash
claude-scan scan
```

Analyze an existing CSV without scanning:

```bash
claude-scan analyze --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Find serious vulnerabilities.'
```

## Temporal execution

Temporal is optional. It records completed file operations and resumes unfinished work after a Worker restart.
The ordinary `analyze` command does not persist execution progress.

With the Temporal CLI installed, start a persistent development server:

```bash
claude-scan server
```

Start one Worker in a separate terminal:

```bash
claude-scan worker
```

Submit an analysis with a unique execution ID:

```bash
claude-scan analyze --temporal --execution-id run-001 --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Find serious vulnerabilities.'
```

After stopping the Worker, restart `claude-scan worker` to resume the existing execution; do not submit it again.
An interrupted file may be processed again. Failed file operations are retried before being recorded as failed.
Keep the Temporal database and the original CSV available. If the server stops, restart it with the same database.
Reports are saved in `report/run-001/analyses/`, with duplicate source reports prevented within that execution.

Wait for completion and print the final results, including failed files:

```bash
claude-scan result --execution-id run-001
```
