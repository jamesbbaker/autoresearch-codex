# Codex Recursive KPI Iteration Plan

Dashboard URL: http://localhost:8765

## Discovery questions asked
- What is your North Star KPI for the next 90 days?
- Which KPIs should be maximized vs minimized?
- What are the current baseline and 30/60/90-day targets for each KPI?
- Which user segment is highest priority for KPI improvement?
- What guardrail KPIs must never regress?
- What instrumentation gaps currently make KPI attribution unreliable?
- How often should Codex run this recursive loop?
- Which KPI should trigger automatic focus if it drifts beyond threshold?

## Current focus
- Focus KPI: `p95_latency_ms`
- Direction: `minimize`

## Subagent tasks (run in Codex)
### instrumentation-auditor
- Objective: Increase measurement confidence for p95_latency_ms
- Method:
  - Validate KPI event pipeline end-to-end.
  - Add attribution tests and anomaly checks.
  - Publish a KPI decomposition view for diagnosis.
- Deliverable: PR with telemetry + automated KPI checks

### product-experimenter
- Objective: Design and ship 2 small experiments to minimize p95_latency_ms
- Method:
  - Choose one funnel bottleneck and define hypotheses.
  - Implement a reversible change behind a flag.
  - Track guardrails and decision thresholds.
- Deliverable: Experiment brief + implementation PR

### performance-optimizer
- Objective: Remove latency/reliability blockers affecting top-line KPIs
- Method:
  - Profile critical path and rank hotspots by user impact.
  - Fix one high-leverage bottleneck.
  - Measure before/after KPI movement with confidence notes.
- Deliverable: Performance PR + impact note

## Computer Use mode instruction
In Codex, tag `@Computer Use` and ask it to keep the dashboard open while running iterative KPI improvement cycles.