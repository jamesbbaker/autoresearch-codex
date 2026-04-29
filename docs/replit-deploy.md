# Replit Deploy Guide

This repo is ready to import into Replit and deploy as a single Python web service.

## Import

1. Create a new Replit project.
2. Choose **Import from GitHub**.
3. Use:

```text
https://github.com/jamesbbaker/autoresearch-codex.git
```

4. Replit should detect `.replit` and use:

```bash
python3 mcp_server/server.py --http
```

## Local Replit Run

Click **Run**. The service exposes:

- Dashboard: `/`
- Health check: `/health`
- MCP JSON-RPC endpoint: `/mcp`

The Replit preview URL should show the Autoresearch dashboard.

## Deploy

Use an **Autoscale Deployment** for the first submission attempt. It is cheap when idle and exposes a public HTTPS URL.

After deployment, your public URLs will look like:

```text
https://<your-replit-app>.<your-replit-user>.replit.app/
https://<your-replit-app>.<your-replit-user>.replit.app/mcp
https://<your-replit-app>.<your-replit-user>.replit.app/health
```

Use the `/mcp` URL in the OpenAI app submission form.

## Smoke Test

In the Replit Shell, run:

```bash
python3 scripts/smoke_http.py http://localhost:8765/mcp
```

After deployment, test the public endpoint:

```bash
python3 scripts/smoke_http.py https://<your-replit-app>.<your-replit-user>.replit.app/mcp
```

Expected output:

```text
initialize: ok
tools/list: ok
autoresearch_start: ok
render_dashboard: ok
```

## OpenAI Submission

In the OpenAI Platform app submission form:

- MCP endpoint: your deployed Replit `/mcp` URL.
- App name and descriptions: use `docs/submission-pack.md`.
- Test prompts: use `docs/submission-pack.md`.
- Dashboard screenshot: use the deployed root URL `/`.

Before final submission, confirm:

- The Replit deployment is awake and `/health` returns JSON.
- `/mcp` responds to the smoke test.
- The dashboard loads without console errors.
- Privacy policy URL and publisher verification are complete.
