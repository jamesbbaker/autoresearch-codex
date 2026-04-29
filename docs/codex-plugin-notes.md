# Codex plugin/MCP setup notes

This implementation is now plugin-shaped and MCP-first because Codex natively connects to MCP servers in CLI/IDE/web contexts.

## Plugin entry point

The intended user entry point is:

```text
@autoresearch start a KPI improvement loop
```

The `skills/autoresearch/SKILL.md` flow asks only for missing setup values, confirms KPIs and guardrails, collects the requested iteration count, and opens the dashboard when Browser Use or Computer Use is available.

## Included surfaces

- Plugin manifest: `.codex-plugin/plugin.json`
- MCP server config: `.mcp.json`
- MCP server: `mcp_server/server.py`
- Skill instructions: `skills/autoresearch/SKILL.md`
- Subagent playbooks: `subagents/*.md`
- Dashboard: `dashboard/index.html`
- Experiment memory: `data/experiment_memory.json`

## Computer Use

Computer Use is configured in Codex at runtime by tagging `@Computer Use` in prompts.
This repo’s role is to provide:
- dashboard URL
- iteration plan
- MCP tools Codex can call between UI observations and code changes
- durable experiment memory so failed assumptions and user feedback influence later iterations
