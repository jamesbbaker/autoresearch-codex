# KPI Autoresearch Codex Toolkit

This repo is a practical **Codex + MCP + Computer Use** setup for recursive KPI improvement in any codebase.

## Target flow

1. **User runs setup in a repo** and defines KPI profile (direction, baseline, target, weight).
2. **Dashboard opens** with KPI history and targets.
3. **Codex iterates** with subagent plans, updating KPI snapshots each cycle.

## Components

- `mcp_server/server.py`: MCP stdio server with tools for KPI interview, profile save, snapshots, subagent planning, and dashboard rendering.
- `scripts/use_in_repo.py`: one-command onboarding flow for a repository.
- `scripts/run_recursive_cycle.py`: one iteration update from latest KPI measurements.
- `dashboard/`: static dashboard UI.
- `subagents/`: role playbooks for iterative execution.
- `.codex/config.toml`: Codex MCP wiring (local + OpenAI docs MCP).

## Setup in a repo

### 1) Configure MCP in Codex

`.codex/config.toml` already includes:

```toml
[mcp_servers.kpiAutoresearch]
command = "python3"
args = ["mcp_server/server.py"]
```

### 2) Run initial onboarding

```bash
python3 scripts/use_in_repo.py \
  --north-star "Increase qualified trial-to-paid conversion" \
  --kpi conversion_rate:maximize:0.031:0.055:1.5 \
  --kpi retention_d7:maximize:0.22:0.30:1.2 \
  --kpi p95_latency_ms:minimize:712:450:1.0 \
  --snapshot conversion_rate=0.031 \
  --snapshot retention_d7=0.22 \
  --snapshot p95_latency_ms=712 \
  --notes "baseline"
```

This writes:
- `data/kpi_profile.json`
- `data/kpi_history.json`
- `data/iteration_plan.md`
- `dashboard/data.json`

### 3) Open dashboard

```bash
python3 -m http.server 8765 --directory dashboard
```

Visit `http://localhost:8765`.

### 4) Run iterative loop

After each engineering iteration and fresh measurements:

```bash
python3 scripts/run_recursive_cycle.py \
  --kpi conversion_rate=0.034 \
  --kpi retention_d7=0.235 \
  --kpi p95_latency_ms=680 \
  --notes "iteration-1"
```

## Using `@Computer Use` in Codex

Use this prompt in Codex:

> `@Computer Use Keep http://localhost:8765 open and visible while we run KPI iterations. After each code change, read KPI cards/trends, then ask me for the next KPI snapshot values and call kpiAutoresearch MCP tools to refresh the plan.`

This keeps the dashboard in view while Codex recursively improves the most off-target KPI.
