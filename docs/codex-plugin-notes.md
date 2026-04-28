# Codex plugin/MCP setup notes

This implementation is MCP-first because Codex natively connects to MCP servers in CLI/IDE/web contexts.

## Why this is closer to a “real plugin” setup

A practical Codex plugin can be represented as:
- MCP servers (tooling)
- skills/subagent instructions
- app integrations (e.g., Computer Use view loop)

This repository now includes all three:
- MCP server: `mcp_server/server.py`
- subagent playbooks: `subagents/*.md`
- Computer Use operating prompt in `README.md` and generated `data/iteration_plan.md`

## Computer Use

Computer Use is configured in Codex at runtime by tagging `@Computer Use` in prompts.
This repo’s role is to provide:
- dashboard URL
- iteration plan
- MCP tools Codex can call between UI observations and code changes.
