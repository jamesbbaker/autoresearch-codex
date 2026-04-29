#!/usr/bin/env python3
"""Run one recursive KPI iteration from measured KPI values."""

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
    parser.add_argument("--iteration", type=int, default=1)
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--change", default="")
    parser.add_argument("--outcome", default="")
    parser.add_argument("--feedback", default="")
    parser.add_argument("--shortcoming", default="")
    parser.add_argument("--next-bet", default="")
    parser.add_argument("--guardrail-notes", default="")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    kpis = parse_kpis(args.kpi)
    _ = call_tool("update_kpi_snapshot", {"kpis": kpis, "notes": args.notes})
    plan = call_tool("generate_subagent_plan", {})
    if args.hypothesis and args.change and args.outcome:
        _ = call_tool(
            "record_experiment_result",
            {
                "iteration": args.iteration,
                "focus_kpi": plan["focus_kpi"],
                "hypothesis": args.hypothesis,
                "change": args.change,
                "outcome": args.outcome,
                "feedback": args.feedback,
                "shortcoming": args.shortcoming,
                "next_bet": args.next_bet,
                "guardrail_notes": args.guardrail_notes,
            },
        )
        plan = call_tool("generate_subagent_plan", {})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(plan, indent=2))
    _ = call_tool("render_dashboard", {})

    print("Focus KPI:", plan["focus_kpi"])
    print("Direction:", plan["focus_direction"])
    print("Subagent briefs written to:", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
