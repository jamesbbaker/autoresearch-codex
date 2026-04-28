#!/usr/bin/env python3
"""KPI Autoresearch MCP server (stdio JSON-RPC).

Tools:
- kpi_interview_questions
- save_kpi_profile
- update_kpi_snapshot
- generate_subagent_plan
- render_dashboard
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
PROFILE_PATH = DATA_DIR / "kpi_profile.json"
DASHBOARD_DIR = ROOT / "dashboard"
DASHBOARD_DATA_PATH = DASHBOARD_DIR / "data.json"


@dataclass
class JsonRpcRequest:
    id: Any
    method: str
    params: dict[str, Any]


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2))


def load_history() -> list[dict[str, Any]]:
    return load_json(HISTORY_PATH, [])


def load_profile() -> dict[str, Any]:
    return load_json(PROFILE_PATH, {"kpis": {}, "loop_cadence": "daily"})


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
    return {
        "generated_at": utc_now_iso(),
        "context": {
            "product_goal": product_goal,
            "company_stage": current_stage,
            "codebase_languages": language_breakdown(),
        },
        "questions": [
            "What is your North Star KPI for the next 90 days?",
            "Which KPIs should be maximized vs minimized?",
            "What are the current baseline and 30/60/90-day targets for each KPI?",
            "Which user segment is highest priority for KPI improvement?",
            "What guardrail KPIs must never regress?",
            "What instrumentation gaps currently make KPI attribution unreliable?",
            "How often should Codex run this recursive loop?",
            "Which KPI should trigger automatic focus if it drifts beyond threshold?",
        ],
    }


def tool_save_kpi_profile(arguments: dict[str, Any]) -> dict[str, Any]:
    kpis = arguments.get("kpis", {})
    if not isinstance(kpis, dict) or not kpis:
        raise ValueError("kpis must be a non-empty object")

    normalized: dict[str, Any] = {}
    for name, spec in kpis.items():
        direction = spec.get("direction", "maximize")
        if direction not in {"maximize", "minimize"}:
            raise ValueError(f"Invalid direction for {name}: {direction}")
        normalized[name] = {
            "direction": direction,
            "baseline": float(spec.get("baseline", 0.0)),
            "target": float(spec.get("target", spec.get("baseline", 0.0))),
            "weight": float(spec.get("weight", 1.0)),
        }

    profile = {
        "updated_at": utc_now_iso(),
        "loop_cadence": arguments.get("loop_cadence", "daily"),
        "north_star": arguments.get("north_star", ""),
        "kpis": normalized,
    }
    save_json(PROFILE_PATH, profile)
    return {"ok": True, "profile_path": str(PROFILE_PATH.relative_to(ROOT)), "profile": profile}


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
    save_json(HISTORY_PATH, history)
    return {"ok": True, "history_points": len(history), "latest": snapshot}


def kpi_delta(history: list[dict[str, Any]], kpi: str) -> float | None:
    if len(history) < 2:
        return None
    prev = history[-2]["kpis"].get(kpi)
    curr = history[-1]["kpis"].get(kpi)
    if prev is None or curr is None:
        return None
    return curr - prev


def score_kpi(name: str, latest: float, spec: dict[str, Any]) -> float:
    target = float(spec.get("target", latest))
    direction = spec.get("direction", "maximize")
    weight = float(spec.get("weight", 1.0))
    gap = (target - latest) if direction == "maximize" else (latest - target)
    return gap * weight


def tool_generate_subagent_plan(arguments: dict[str, Any]) -> dict[str, Any]:
    history = load_history()
    if not history:
        raise ValueError("No KPI history found. Call update_kpi_snapshot first.")

    latest = history[-1]["kpis"]
    profile = load_profile()
    prof_kpis = profile.get("kpis", {})

    scored = []
    for name, value in latest.items():
        spec = prof_kpis.get(name, {"direction": "maximize", "target": value, "weight": 1.0})
        scored.append((name, score_kpi(name, float(value), spec), spec))

    scored.sort(key=lambda row: row[1], reverse=True)
    focus_kpi, focus_score, focus_spec = scored[0]
    direction = focus_spec.get("direction", "maximize")

    plans = [
        {
            "agent": "instrumentation-auditor",
            "objective": f"Increase measurement confidence for {focus_kpi}",
            "method": [
                "Validate KPI event pipeline end-to-end.",
                "Add attribution tests and anomaly checks.",
                "Publish a KPI decomposition view for diagnosis.",
            ],
            "deliverable": "PR with telemetry + automated KPI checks",
        },
        {
            "agent": "product-experimenter",
            "objective": f"Design and ship 2 small experiments to {direction} {focus_kpi}",
            "method": [
                "Choose one funnel bottleneck and define hypotheses.",
                "Implement a reversible change behind a flag.",
                "Track guardrails and decision thresholds.",
            ],
            "deliverable": "Experiment brief + implementation PR",
        },
        {
            "agent": "performance-optimizer",
            "objective": "Remove latency/reliability blockers affecting top-line KPIs",
            "method": [
                "Profile critical path and rank hotspots by user impact.",
                "Fix one high-leverage bottleneck.",
                "Measure before/after KPI movement with confidence notes.",
            ],
            "deliverable": "Performance PR + impact note",
        },
    ]

    return {
        "generated_at": utc_now_iso(),
        "focus_kpi": focus_kpi,
        "focus_score": focus_score,
        "focus_direction": direction,
        "latest_kpis": latest,
        "deltas": {k: kpi_delta(history, k) for k in latest},
        "subagent_plans": plans,
    }


def tool_render_dashboard(arguments: dict[str, Any]) -> dict[str, Any]:
    history = load_history()
    profile = load_profile()
    payload = {
        "profile": profile,
        "history": history,
        "updated_at": utc_now_iso(),
    }
    save_json(DASHBOARD_DATA_PATH, payload)
    return {
        "ok": True,
        "dashboard_data": str(DASHBOARD_DATA_PATH.relative_to(ROOT)),
        "dashboard_html": "dashboard/index.html",
        "history_points": len(history),
    }


TOOLS = [
    {
        "name": "kpi_interview_questions",
        "description": "Generate KPI discovery questions based on repository context.",
        "inputSchema": {"type": "object", "properties": {"product_goal": {"type": "string"}, "company_stage": {"type": "string"}}},
    },
    {
        "name": "save_kpi_profile",
        "description": "Persist KPI profile including direction, targets, and weights.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "north_star": {"type": "string"},
                "loop_cadence": {"type": "string"},
                "kpis": {"type": "object"},
            },
            "required": ["kpis"],
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
        "description": "Create methodical subagent plans based on profile + latest KPI state.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "render_dashboard",
        "description": "Write dashboard/data.json from profile and KPI history.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def parse_request(line: str) -> JsonRpcRequest:
    payload = json.loads(line)
    return JsonRpcRequest(id=payload.get("id"), method=payload.get("method", ""), params=payload.get("params", {}))


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
            "serverInfo": {"name": "kpi-autoresearch", "version": "0.2.0"},
            "capabilities": {"tools": {}},
        }
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        handlers = {
            "kpi_interview_questions": tool_kpi_interview_questions,
            "save_kpi_profile": tool_save_kpi_profile,
            "update_kpi_snapshot": tool_update_kpi_snapshot,
            "generate_subagent_plan": tool_generate_subagent_plan,
            "render_dashboard": tool_render_dashboard,
        }
        if name not in handlers:
            raise ValueError(f"Unknown tool: {name}")
        output = handlers[name](arguments)
        return {"content": [{"type": "text", "text": json.dumps(output, indent=2)}]}
    raise ValueError(f"Unsupported method: {method}")


def run_stdio() -> None:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        req_id = None
        try:
            req = parse_request(line)
            req_id = req.id
            result = handle(req.method, req.params)
            write_response(req.id, result=result)
        except Exception as exc:  # noqa: BLE001
            write_response(req_id, error=str(exc))


def main() -> None:
    parser = argparse.ArgumentParser(description="KPI Autoresearch MCP server")
    parser.add_argument("--stdio", action="store_true", default=True, help="Run as stdio server")
    _ = parser.parse_args()
    run_stdio()


if __name__ == "__main__":
    main()
