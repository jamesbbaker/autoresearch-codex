# KPI Autoresearch Codex Toolkit

This repository implements a **Codex + MCP workflow** inspired by Karpathy's autoresearch loop:

1. Ask users key KPI discovery questions based on the codebase.
2. Maintain a KPI dashboard with history.
3. Generate methodical subagent plans to improve lagging KPIs.

## What's included

- `mcp_server/server.py` — lightweight MCP server (stdio) with tools for KPI interview, KPI updates, dashboard rendering, and subagent planning.
- `dashboard/` — static dashboard UI that reads `dashboard/data.json`.
- `subagents/` — reusable subagent playbooks for product, growth, and reliability KPI improvements.
- `scripts/run_recursive_cycle.py` — recursive loop runner to track KPI deltas and auto-generate next iteration plans.
- `.codex/config.toml` — sample Codex MCP wiring for this server.

## Quick start

```bash
python3 mcp_server/server.py --help
python3 scripts/run_recursive_cycle.py --help
python3 scripts/run_recursive_cycle.py \
  --kpi conversion_rate=0.032 \
  --kpi p95_latency_ms=780 \
  --kpi retention_d7=0.21
```

Then open:

```bash
python3 -m http.server 8000 --directory dashboard
```

and visit `http://localhost:8000`.

## Codex MCP setup

Add this to your Codex config (already included as `.codex/config.toml`):

```toml
[mcp_servers.kpiAutoresearch]
command = "python3"
args = ["mcp_server/server.py"]
```

## Suggested Codex prompt

"Use the `kpiAutoresearch` MCP server to:
- run KPI interview questions,
- initialize KPI snapshots,
- render dashboard,
- and produce 3 subagent task plans for the weakest KPI.
Then start the first iteration."
