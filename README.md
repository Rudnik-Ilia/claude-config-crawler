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

Copy the environment template:

```bash
cp -n .env.example .env
```

Set `LLAMA_CPP_BASE_URL` to the address of your llama.cpp server, including `/v1`.
Both analysis modes require this URL. You can also pass it with `--base-url`.
Set `LLAMA_CPP_MODEL` if your server uses a different model name.
If your server requires authentication, uncomment and set `LLAMA_CPP_API_KEY`.

Install dependencies and activate the environment:

```bash
uv sync
source .venv/bin/activate
```

Scan GitHub:

Install GitHub CLI and authenticate with `gh auth login` before running the local scan.

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

## Docker Compose

From the repository root, configure `.env` as above. For scanning in Docker, set `GH_TOKEN` in `.env`.
The llama.cpp address must be reachable from the containers.

```bash
docker compose build cli
docker compose run --rm cli scan
docker compose run --rm cli analyze --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Summarize configuration settings.'
```

To run with Temporal:

```bash
docker compose --profile temporal up -d --wait temporal worker
docker compose run --rm cli analyze --temporal --execution-id run-001 --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Summarize configuration settings.'
docker compose logs -f worker
docker compose run --rm cli result --execution-id run-001
```

The Temporal UI is available at <http://localhost:8233>. CSV files and reports are written to `report/` on the host.
Temporal stores its history in the `temporal-data` Docker volume.

To pause processing, stop the worker. To resume the same execution, start it again:

```bash
docker compose stop worker
docker compose start worker
```
