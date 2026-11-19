# Claude Settings Scan

Find Claude Code settings on GitHub, save their URLs to a CSV, and analyze a CSV with llama.cpp. The analyzer writes Markdown findings with links to the source files.

## Setup

Run the commands from the repository root.

```bash
cp -n .env.example .env
```

Set `LLAMA_CPP_BASE_URL` in `.env` to your running llama.cpp endpoint, including `/v1`. Analysis requires this setting or the `--base-url` flag. Set `LLAMA_CPP_MODEL` if the server uses a different model name, and uncomment `LLAMA_CPP_API_KEY` if it requires authentication.

## Run locally

Install [uv](https://docs.astral.sh/uv/) and sync the project. To scan GitHub, install [GitHub CLI](https://cli.github.com/) and authenticate first.

```bash
uv sync
gh auth login
uv run claude-scan scan
uv run claude-scan analyze --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Summarize configuration settings.'
```

`scan` writes `report/data_to_check/claude_settings_inventory.csv`. If you already have a CSV with a `github_url` column, pass it to `analyze` directly. Markdown reports are written to `report/analyses/`.

### Resume with Temporal

Install the [Temporal CLI](https://docs.temporal.io/cli/setup-cli). In two separate terminals, start the server and worker:

```bash
uv run claude-scan server
```

```bash
uv run claude-scan worker
```

Submit the analysis in a third terminal. Use a new execution ID for each new run.

```bash
uv run claude-scan analyze --temporal --execution-id run-001 --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Summarize configuration settings.'
uv run claude-scan result --execution-id run-001
```

The local server stores its history in `src/runner/database/temporal.sqlite` by default. Stop the worker with `Ctrl+C` and restart it to resume the existing run. If the server stops, restart it with the same database. Keep the input CSV available at the same path.

## Run with Docker Compose

Install Docker with Compose. Ensure the containers can reach the llama.cpp address in `.env`. For scanning, set `GH_TOKEN` in `.env`.

```bash
docker compose build cli
docker compose run --rm cli scan
docker compose run --rm cli analyze --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Summarize configuration settings.'
```

For resumable analysis, start Temporal and submit a run:

```bash
docker compose --profile temporal up -d --wait temporal worker
docker compose run --rm cli analyze --temporal --execution-id run-001 --csv report/data_to_check/claude_settings_inventory.csv --system-prompt 'Summarize configuration settings.'
docker compose run --rm cli result --execution-id run-001
```

Place any existing CSV under the host's `report/` directory so both containers can read it. Reports are also written there. The `temporal-data` Docker volume holds execution history.

Pause and resume the worker with these commands:

```bash
docker compose stop worker
docker compose start worker
```

## Monitor a Temporal run

Open the [Temporal UI](http://localhost:8233) and select your execution ID. For Docker, you can also run `docker compose logs -f worker`. The `result` command waits for completion and prints each file's status, including failures.

Resume by restarting the worker for the existing run. Completed files are skipped and an interrupted file may be retried. Temporal reports are written to `report/<execution-id>/analyses/`.
