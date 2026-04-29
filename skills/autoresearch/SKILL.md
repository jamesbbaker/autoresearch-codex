---
name: autoresearch
description: Run a recursive KPI-driven research and improvement loop in Codex using the Autoresearch MCP server, dashboard, and experiment memory.
---

# Autoresearch

Use this skill when the user invokes `@autoresearch` or asks Codex to run recursive KPI/product/performance improvement cycles.

## Entry Flow

1. Confirm the plugin is enabled.
   - If the `autoresearch` MCP tools are unavailable, tell the user to enable/install the Autoresearch plugin, then restart Codex.
   - Do not continue with a pretend loop if the MCP tools cannot be reached.
2. Ask only for missing setup values:
   - North-star outcome.
   - KPI names, direction (`maximize` or `minimize`), current baseline, target, and optional weight.
   - Guardrail KPIs that must not regress.
   - Number of iterations Codex should attempt.
   - Dashboard/browser preference. If browser capability is unavailable, ask the user to enable Browser Use or Computer Use for live dashboard monitoring.
3. Call the MCP tools in this order:
   - `autoresearch_start` to obtain missing questions and operating instructions.
   - `save_kpi_profile` once KPIs are confirmed.
   - `update_kpi_snapshot` with the baseline values.
   - `generate_subagent_plan`.
   - `render_dashboard`.
4. Open or serve the dashboard cleanly:
   - Start `python3 -m http.server 8765 --directory dashboard` from the plugin repo if needed.
   - Open `http://localhost:8765/` with Browser Use or Computer Use when enabled.
   - If browser control is not enabled, give the URL and ask the user to enable the relevant plugin for automatic monitoring.

## Iteration Loop

For each requested iteration:

1. Review the dashboard and `data/last_subagent_plan.json`.
2. Pick one focus KPI and one narrow experiment or engineering improvement.
3. State hypothesis, expected KPI movement, guardrails, rollback condition, and measurement plan.
4. Implement the smallest credible code change in the target repository.
5. Run relevant tests or checks.
6. Ask the user for fresh KPI values if Codex cannot measure them directly.
7. Call `update_kpi_snapshot`, `record_experiment_result`, `generate_subagent_plan`, and `render_dashboard`.
8. Carry forward learnings, failed assumptions, unresolved shortcomings, and next bets.

## Operating Principles

- Treat instrumentation quality as a first-class blocker. If KPI data is unreliable, fix measurement before optimizing.
- Prefer reversible experiments and small product changes over broad rewrites.
- Preserve memory of negative results. A failed experiment is useful when its hypothesis, evidence, and next adjustment are recorded.
- Stop after the requested iteration count, then summarize KPI movement, experiments tried, shortcomings, and recommended next loop.
