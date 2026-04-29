# Autoresearch Submission Pack

Use this when submitting Autoresearch through the OpenAI Platform Dashboard app review flow. Per OpenAI's current submission docs, approved apps can be published to the ChatGPT App Directory and Codex Plugin Directory; publishing the approved app creates the Codex plugin distribution.

## Current Status

Autoresearch is plugin-shaped locally, but it is not yet submit-ready for public review because the MCP server is local stdio only.

Submission blockers before final OpenAI review:

- Public HTTPS MCP endpoint is required. Replit deployment is the intended first host; use the deployed `/mcp` URL.
- Logo and screenshots are strongly expected for directory metadata.
- Organization verification and `api.apps.write` permission must exist in the OpenAI Platform account.
- Final submission must be performed in the OpenAI Platform Dashboard under the intended verified publisher.

## Recommended Submission Values

App name:

```text
Autoresearch
```

Short description:

```text
Run KPI-driven Codex improvement loops with experiment memory.
```

Long description:

```text
Autoresearch helps teams run structured KPI improvement loops from ChatGPT and Codex. It asks for a north-star outcome, confirms KPIs and guardrails, collects an iteration count, then coordinates MCP tools, a dashboard, subagent briefs, and experiment memory so each cycle carries forward measured results, user feedback, failed assumptions, and next bets.
```

Primary category:

```text
Productivity
```

Suggested test prompts:

```text
@autoresearch start a KPI improvement loop for trial-to-paid conversion.
@autoresearch run 3 iterations using conversion_rate, retention_d7, and p95_latency_ms.
@autoresearch review experiment memory and recommend the next KPI bet.
```

Expected behavior:

```text
The app asks for missing north-star, KPI, guardrail, browser, and iteration-count details. Once configured, it saves the KPI profile, records snapshots, generates a focus KPI and subagent plan, renders the dashboard, and records experiment outcomes with feedback, shortcomings, and next bets.
```

MCP tools:

- `autoresearch_start`: Finds missing setup values and returns operating instructions.
- `kpi_interview_questions`: Generates KPI discovery questions.
- `save_kpi_profile`: Saves KPI profile, guardrails, and iteration count.
- `update_kpi_snapshot`: Appends KPI measurements.
- `generate_subagent_plan`: Selects the focus KPI and subagent work.
- `record_experiment_result`: Stores hypothesis, change, outcome, feedback, shortcomings, and next bet.
- `render_dashboard`: Renders dashboard data.

Data returned:

- KPI names, baselines, targets, weights, guardrails, and snapshots supplied by the user.
- Experiment memory entered by the user or produced during the loop.
- No secrets, credentials, or external account data are intentionally returned.

## Public Hosting Work Needed

Before submission, deploy the HTTP MCP server on Replit. The review form will reject local or testing endpoints.

Replit deployment files are included:

- `.replit`
- `replit.nix`
- `scripts/smoke_http.py`
- `docs/replit-deploy.md`

After Replit deploys, use:

```text
https://<your-replit-app>.<your-replit-user>.replit.app/mcp
```

Production hardening still needed for real multi-user public use:

1. Replace local JSON state with durable per-user storage.
2. Add authentication if the app should not be public.
3. Add a content security policy that includes only the exact domains the dashboard fetches from.
4. Create a demo/test account or no-auth review path if authentication is required.

## Dashboard Evidence

Local dashboard:

```text
http://localhost:8765/
```

Files to screenshot after serving locally:

- `dashboard/index.html`
- `dashboard/data.json`

Suggested screenshots:

- KPI board with progress cards.
- Experiment memory panel.
- Subagent briefs panel.

## Final Submission Steps

1. Complete individual or business verification in the OpenAI Platform Dashboard.
2. Confirm the submitting account has `api.apps.write`.
3. Deploy the public HTTPS MCP endpoint on Replit.
4. Test the app in Developer Mode.
5. Fill out the OpenAI Platform app submission form with the values above.
6. Upload logo and screenshots.
7. Review all confirmation boxes and safety warnings.
8. Click **Submit for review**.

The final click submits content under the publisher's OpenAI account and starts OpenAI review. Codex should ask for explicit confirmation immediately before that action.
