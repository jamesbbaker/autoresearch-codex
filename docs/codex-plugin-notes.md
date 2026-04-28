# Codex plugin vs MCP design notes

This project uses an MCP-first architecture so it works across Codex CLI/IDE/web surfaces with a single server.

## Why MCP-first

- OpenAI provides first-class MCP integration in Codex configuration.
- The public OpenAI Docs MCP can be configured alongside custom servers.
- Tooling here uses local JSON-RPC stdio to keep setup light.

## Plugin mapping

Per current Codex guidance, plugins can bundle:

- skills,
- app integrations,
- MCP server configuration.

This repo currently provides:

- MCP server (`mcp_server/server.py`)
- subagent playbooks (`subagents/*.md`)
- Codex config sample (`.codex/config.toml`)

You can package these into your org's plugin distribution process once available in your workspace.
