#!/usr/bin/env python3
"""KPI Autoresearch MCP server (stdio JSON-RPC).

Implements a compact subset of MCP methods:
- initialize
- tools/list
- tools/call
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
HISTORY_PATH = DATA_DIR / "kpi_history.json"
DASHBOARD_DIR = ROOT / "dashboard"
DASHBOARD_DATA_PATH = DASHBOARD_DIR / "data.json"


@dataclass
class JsonRpcRequest:
    id: Any
    method: str
    params: dict[str, Any]


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text())


def save_history(history: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(history, indent=2))


def language_breakdown(max_files: int = 2000) -> dict[str, int]:
    ext_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".js": "javascript",
        ".jsx": "jsx",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".kt": "kotlin",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".md": "markdown",
    }
    counts: dict[str, int] = {}
    seen = 0
    for p in ROOT.rglob("*"):
        if ".git" in p.parts or p.is_dir():
            continue
        if seen >= max_files:
            break
        seen += 1
        lang = ext_map.get(p.suffix.lower(), "other")
        counts[lang] = counts.get(lang, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))


def tool_kpi_interview_questions(arguments: dict[str, Any]) -> dict[str, Any]:
    product_goal = arguments.get("product_goal", "Improve user outcomes and business growth")
    current_stage = arguments.get("company_stage", "early-growth")
    langs = language_breakdown()
    return {
        "generated_at": utc_now_iso(),
        "context": {
            "product_goal": product_goal,
            "company_stage": current_stage,
            "codebase_languages": langs,
        },
        "questions": [
            "What is your single North Star metric for the next 90 days?",
            "Which 3 leading indicators most strongly predict the North Star in your business model?",
            "What is your current baseline for each KPI, and what target do you want by date?",
            "Which user segment matters most for this quarter (new users, activated users, retained users, revenue users)?",
            "What constraints must optimization respect (latency, reliability, budget, trust/safety, compliance)?",
            "Which KPI can improve fastest with engineering effort in the next two weeks?",
            "What instrumentation gaps prevent reliable KPI attribution today?",
            "Which regressions are unacceptable (guardrail metrics and hard thresholds)?",
            "How frequently should Codex run this loop (daily/weekly), and who approves high-impact changes?",
        ],
    }


def tool_update_kpi_snapshot(arguments: dict[str, Any]) -> dict[str, Any]:
    kpis = arguments.get("kpis", {})
    if not isinstance(kpis, dict) or not kpis:
        raise ValueError("kpis must be a non-empty object mapping KPI name -> numeric value")
    snapshot = {
        "timestamp": utc_now_iso(),
        "kpis": {k: float(v) for k, v in kpis.items()},
        "notes": arguments.get("notes", ""),
    }
    history = load_history()
    history.append(snapshot)
    save_history(history)
    return {
        "ok": True,
        "history_points": len(history),
        "latest": snapshot,
        "history_path": str(HISTORY_PATH.relative_to(ROOT)),
    }


def kpi_delta_summary(history: list[dict[str, Any]]) -> dict[str, Any]:
    if len(history) < 2:
        return {"message": "Need at least two snapshots to compute deltas."}
    prev = history[-2]["kpis"]
    curr = history[-1]["kpis"]
    deltas = {}
    for k, v in curr.items():
        old = prev.get(k)
        deltas[k] = None if old is None else v - old
    return deltas


def tool_generate_subagent_plan(arguments: dict[str, Any]) -> dict[str, Any]:
    history = load_history()
    if not history:
        raise ValueError("No KPI history found. Call update_kpi_snapshot first.")
    latest = history[-1]["kpis"]
    optimization_direction = arguments.get("direction", "maximize")
    weakest_kpi = sorted(latest.items(), key=lambda kv: kv[1])[0][0]

    plans = [
        {
            "agent": "instrumentation-auditor",
            "objective": f"Improve signal quality for {weakest_kpi}",
            "method": [
                "Audit event coverage, missing joins, and KPI definitions.",
                "Add tests for metric pipeline consistency.",
                "Ship observability panel for KPI decomposition.",
            ],
            "deliverable": "PR with metric definitions + validation checks",
        },
        {
            "agent": "growth-experimenter",
            "objective": f"Design 2 experiments to {optimization_direction} {weakest_kpi}",
            "method": [
                "Generate hypotheses tied to activation funnel stages.",
                "Implement smallest reversible product change.",
                "Define guardrails and stop conditions before rollout.",
            ],
            "deliverable": "Experiment plan + implementation PR",
        },
        {
            "agent": "performance-optimizer",
            "objective": "Reduce technical friction blocking conversion/retention",
            "method": [
                "Profile top user path latency and error rates.",
                "Target p95 latency + failure hotspots.",
                "Document before/after KPI impact with confidence notes.",
            ],
            "deliverable": "Perf PR + KPI impact report",
        },
    ]

    return {
        "generated_at": utc_now_iso(),
        "weakest_kpi": weakest_kpi,
        "latest_kpis": latest,
        "delta": kpi_delta_summary(history),
        "subagent_plans": plans,
    }


def tool_render_dashboard(arguments: dict[str, Any]) -> dict[str, Any]:
    history = load_history()
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_DATA_PATH.write_text(json.dumps({"history": history}, indent=2))
    return {
        "ok": True,
        "history_points": len(history),
        "dashboard_data": str(DASHBOARD_DATA_PATH.relative_to(ROOT)),
        "dashboard_html": "dashboard/index.html",
    }


TOOLS = [
    {
        "name": "kpi_interview_questions",
        "description": "Generate KPI discovery questions based on repository context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_goal": {"type": "string"},
                "company_stage": {"type": "string"},
            },
        },
    },
    {
        "name": "update_kpi_snapshot",
        "description": "Append a KPI snapshot to local history storage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "kpis": {"type": "object", "additionalProperties": {"type": "number"}},
                "notes": {"type": "string"},
            },
            "required": ["kpis"],
        },
    },
    {
        "name": "generate_subagent_plan",
        "description": "Create methodical subagent plans based on latest KPI state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["maximize", "minimize"]},
            },
        },
    },
    {
        "name": "render_dashboard",
        "description": "Write dashboard/data.json from KPI history so the dashboard UI can render trends.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def parse_request(line: str) -> JsonRpcRequest:
    payload = json.loads(line)
    return JsonRpcRequest(
        id=payload.get("id"),
        method=payload.get("method", ""),
        params=payload.get("params", {}),
    )


def write_response(id_val: Any, result: Any = None, error: str | None = None) -> None:
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": id_val}
    if error is None:
        body["result"] = result
    else:
        body["error"] = {"code": -32000, "message": error}
    sys.stdout.write(json.dumps(body) + "\n")
    sys.stdout.flush()


def handle(method: str, params: dict[str, Any]) -> Any:
    if method == "initialize":
        return {
            "protocolVersion": "2025-03-26",
            "serverInfo": {"name": "kpi-autoresearch", "version": "0.1.0"},
            "capabilities": {"tools": {}},
        }
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name == "kpi_interview_questions":
            output = tool_kpi_interview_questions(arguments)
        elif name == "update_kpi_snapshot":
            output = tool_update_kpi_snapshot(arguments)
        elif name == "generate_subagent_plan":
            output = tool_generate_subagent_plan(arguments)
        elif name == "render_dashboard":
            output = tool_render_dashboard(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        return {"content": [{"type": "text", "text": json.dumps(output, indent=2)}]}
    raise ValueError(f"Unsupported method: {method}")


def run_stdio() -> None:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            req = parse_request(line)
            result = handle(req.method, req.params)
            write_response(req.id, result=result)
        except Exception as exc:  # noqa: BLE001
            req_id = None
            try:
                req_id = json.loads(line).get("id")
            except Exception:
                pass
            write_response(req_id, error=str(exc))


def main() -> None:
    parser = argparse.ArgumentParser(description="KPI Autoresearch MCP server")
    parser.add_argument("--stdio", action="store_true", default=True, help="Run as stdio server")
    _ = parser.parse_args()
    run_stdio()


if __name__ == "__main__":
    main()
