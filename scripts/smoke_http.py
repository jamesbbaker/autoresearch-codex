#!/usr/bin/env python3
"""Smoke-test the Autoresearch HTTP MCP endpoint."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any


def rpc(endpoint: str, method: str, params: dict[str, Any] | None = None, req_id: int = 1) -> dict[str, Any]:
    body = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=body, headers={"content-type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload["result"]


def main() -> None:
    endpoint = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765/mcp"
    try:
        rpc(endpoint, "initialize")
        print("initialize: ok")
        tools = rpc(endpoint, "tools/list")
        print("tools/list: ok", ", ".join(tool["name"] for tool in tools["tools"]))
        start = rpc(endpoint, "tools/call", {"name": "autoresearch_start", "arguments": {"browser_enabled": True}})
        json.loads(start["content"][0]["text"])
        print("autoresearch_start: ok")
        rendered = rpc(endpoint, "tools/call", {"name": "render_dashboard", "arguments": {}})
        json.loads(rendered["content"][0]["text"])
        print("render_dashboard: ok")
    except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
