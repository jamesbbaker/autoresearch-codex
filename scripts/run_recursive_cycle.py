#!/usr/bin/env python3
"""Run one KPI autoresearch iteration and emit next-step subagent briefs."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "mcp_server" / "server.py"
OUT = ROOT / "data" / "last_subagent_plan.json"


def call_tool(name: str, arguments: dict) -> dict:
    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}},
    ]
    payload = "\n".join(json.dumps(r) for r in reqs) + "\n"
    p = subprocess.run(["python3", str(SERVER)], input=payload, text=True, capture_output=True, check=True)
    lines = [json.loads(line) for line in p.stdout.splitlines() if line.strip()]
    result_text = lines[-1]["result"]["content"][0]["text"]
    return json.loads(result_text)


def parse_kpis(raw: list[str]) -> dict[str, float]:
    out = {}
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Expected KPI format name=value, got: {item}")
        k, v = item.split("=", 1)
        out[k.strip()] = float(v)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpi", action="append", default=[], help="KPI pair: name=value")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    kpis = parse_kpis(args.kpi)
    snap = call_tool("update_kpi_snapshot", {"kpis": kpis, "notes": args.notes})
    plan = call_tool("generate_subagent_plan", {"direction": "maximize"})
    _ = call_tool("render_dashboard", {})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, indent=2))

    print("Snapshot saved:", snap["history_path"])
    print("Weakest KPI:", plan["weakest_kpi"])
    print("Subagent briefs written to:", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
