#!/usr/bin/env python3
"""Onboard a repo into KPI autoresearch and start iterative loop assets."""

from __future__ import annotations

import argparse
import json
import subprocess
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "mcp_server" / "server.py"
PLAN_PATH = ROOT / "data" / "iteration_plan.md"


def call_tool(name: str, arguments: dict) -> dict:
    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}},
    ]
    payload = "\n".join(json.dumps(r) for r in reqs) + "\n"
    p = subprocess.run(["python3", str(SERVER)], input=payload, text=True, capture_output=True, check=True)
    lines = [json.loads(line) for line in p.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1]["result"]["content"][0]["text"])


def parse_profile(items: list[str]) -> dict[str, dict]:
    """Parse KPI string: name:direction:baseline:target[:weight]."""
    out: dict[str, dict] = {}
    for item in items:
        parts = item.split(":")
        if len(parts) < 4:
            raise ValueError(f"Invalid --kpi '{item}'. Expected name:direction:baseline:target[:weight]")
        name, direction, baseline, target = parts[:4]
        weight = parts[4] if len(parts) > 4 else "1.0"
        out[name] = {
            "direction": direction,
            "baseline": float(baseline),
            "target": float(target),
            "weight": float(weight),
        }
    return out


def parse_snapshot(items: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in items:
        key, value = item.split("=", 1)
        out[key] = float(value)
    return out


def write_plan(questions: dict, plan: dict, dashboard_url: str) -> None:
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = [
        "# Codex Recursive KPI Iteration Plan",
        "",
        f"Dashboard URL: {dashboard_url}",
        "",
        "## Discovery questions asked",
    ]
    text.extend([f"- {q}" for q in questions.get("questions", [])])
    text.extend([
        "",
        "## Current focus",
        f"- Focus KPI: `{plan['focus_kpi']}`",
        f"- Direction: `{plan['focus_direction']}`",
        "",
        "## Subagent tasks (run in Codex)",
    ])
    for s in plan["subagent_plans"]:
        text.append(f"### {s['agent']}")
        text.append(f"- Objective: {s['objective']}")
        text.append("- Method:")
        for step in s["method"]:
            text.append(f"  - {step}")
        text.append(f"- Deliverable: {s['deliverable']}")
        text.append("")

    text.extend([
        "## Computer Use mode instruction",
        "In Codex, tag `@Computer Use` and ask it to keep the dashboard open while running iterative KPI improvement cycles.",
    ])
    PLAN_PATH.write_text("\n".join(text))


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up and run KPI autoresearch flow in this repo")
    parser.add_argument("--north-star", required=True)
    parser.add_argument("--kpi", action="append", default=[], help="name:direction:baseline:target[:weight]")
    parser.add_argument("--snapshot", action="append", default=[], help="name=value for current measurement")
    parser.add_argument("--notes", default="")
    parser.add_argument("--dashboard-port", type=int, default=8765)
    parser.add_argument("--open-browser", action="store_true")
    args = parser.parse_args()

    profile_kpis = parse_profile(args.kpi)
    snapshot_kpis = parse_snapshot(args.snapshot)

    questions = call_tool("kpi_interview_questions", {"product_goal": args.north_star})
    _ = call_tool(
        "save_kpi_profile",
        {
            "north_star": args.north_star,
            "loop_cadence": "daily",
            "kpis": profile_kpis,
        },
    )
    _ = call_tool("update_kpi_snapshot", {"kpis": snapshot_kpis, "notes": args.notes})
    plan = call_tool("generate_subagent_plan", {})
    _ = call_tool("render_dashboard", {})

    dashboard_url = f"http://localhost:{args.dashboard_port}"
    write_plan(questions, plan, dashboard_url)

    print("Setup complete.")
    print(f"Iteration plan: {PLAN_PATH.relative_to(ROOT)}")
    print("To serve dashboard:")
    print(f"  python3 -m http.server {args.dashboard_port} --directory dashboard")
    if args.open_browser:
        webbrowser.open(dashboard_url)
        print(f"Opened {dashboard_url} in browser.")


if __name__ == "__main__":
    main()
