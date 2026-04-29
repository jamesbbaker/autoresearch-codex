# Autoresearch Codex Plugin

Autoresearch is a Codex plugin prototype for recursive KPI improvement. A user starts with `@autoresearch`, confirms the north-star outcome, KPIs, guardrails, iteration count, and browser preference, then Codex runs bounded improvement loops while preserving experiment memory and shortcomings.

## What It Includes

- `.codex-plugin/plugin.json`: plugin manifest for Codex packaging/submission.
- `.mcp.json`: MCP server wiring for the plugin.
- `skills/autoresearch/SKILL.md`: `@autoresearch` operating flow.
- `mcp_server/server.py`: stdio MCP server with KPI profile, snapshot, plan, dashboard, and experiment-memory tools.
- `dashboard/`: local dashboard for KPI progress, guardrails, subagent briefs, and learnings.
- `scripts/`: local onboarding and iteration helpers.
- `subagents/`: role briefs for instrumentation, product experimentation, and performance optimization.

## Local Test

```bash
cd /Users/jamesbaker/Desktop/autoresearch-codex

python3 scripts/use_in_repo.py \
  --north-star "Increase qualified trial-to-paid conversion" \
  --iterations 3 \
  --kpi conversion_rate:maximize:0.031:0.055:1.5 \
  --kpi retention_d7:maximize:0.22:0.30:1.2 \
  --kpi p95_latency_ms:minimize:712:450:1.0 \
  --guardrail error_rate:minimize:0.02 \
  --snapshot conversion_rate=0.031 \
  --snapshot retention_d7=0.22 \
  --snapshot p95_latency_ms=712 \
  --notes "baseline"
```

Serve the dashboard:

```bash
python3 -m http.server 8765 --directory dashboard
```

Open `http://localhost:8765/`.

## Replit Hosting

This repo includes Replit deployment files:

- `.replit`
- `replit.nix`
- `scripts/smoke_http.py`
- `docs/replit-deploy.md`

Import the GitHub repo into Replit and click **Run**. Replit should start:

```bash
python3 mcp_server/server.py --http
```

The hosted service exposes:

- Dashboard: `/`
- Health check: `/health`
- MCP JSON-RPC endpoint: `/mcp`

Use the deployed Replit `/mcp` URL in the OpenAI app submission form.

Run one iteration with memory:

```bash
python3 scripts/run_recursive_cycle.py \
  --iteration 1 \
  --kpi conversion_rate=0.034 \
  --kpi retention_d7=0.235 \
  --kpi p95_latency_ms=680 \
  --notes "iteration-1" \
  --hypothesis "Reducing critical-path latency should improve trial conversion" \
  --change "Ranked p95 latency as the first optimization focus" \
  --outcome "Latency improved in the snapshot while conversion moved up" \
  --feedback "Need better attribution between latency and conversion" \
  --shortcoming "Current snapshot is aggregate-only and lacks segment attribution" \
  --next-bet "Add segment-level KPI decomposition" \
  --guardrail-notes "No guardrail regression observed"
```

## Codex Usage

After installing/enabling the plugin, start with:

```text
@autoresearch start a KPI improvement loop for this repo
```

Codex should ask only for missing setup values:

- North-star outcome.
- KPI names, directions, baselines, targets, and weights.
- Guardrail KPIs.
- Number of iterations to run.
- Whether Browser Use or Computer Use is enabled for dashboard monitoring.

If browser control is unavailable, Codex should ask the user to enable the relevant plugin and provide `http://localhost:8765/`.

## MCP Tools

- `autoresearch_start`: returns missing setup questions and operating instructions.
- `kpi_interview_questions`: generates KPI discovery questions.
- `save_kpi_profile`: saves KPIs, guardrails, and iteration count.
- `update_kpi_snapshot`: appends measured KPI values.
- `generate_subagent_plan`: chooses focus KPI and next subagent briefs.
- `record_experiment_result`: stores hypothesis, outcome, feedback, shortcomings, and next bet.
- `render_dashboard`: writes dashboard data.

## Submission Notes

This repository is now plugin-shaped, but public distribution is handled through OpenAI's app submission flow. See `docs/submission-pack.md` for current submission steps and ready-to-paste form content. OpenAI review requires a public HTTPS MCP endpoint; deploy this repo on Replit and use the deployed `/mcp` URL.
