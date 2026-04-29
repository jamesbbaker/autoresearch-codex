#!/usr/bin/env python3
"""KPI Autoresearch MCP server.

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
import mimetypes
import os
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
HISTORY_PATH = DATA_DIR / "kpi_history.json"
PROFILE_PATH = DATA_DIR / "kpi_profile.json"
DASHBOARD_DIR = ROOT / "dashboard"
DASHBOARD_DATA_PATH = DASHBOARD_DIR / "data.json"
MEMORY_PATH = DATA_DIR / "experiment_memory.json"
OPENAI_APPS_CHALLENGE_TOKEN = os.environ.get(
    "OPENAI_APPS_CHALLENGE_TOKEN",
    "oPPl8CU4K6IclLQv8CL4Hq1P4vn7qcwfjLHYELUdrTE",
)


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
    return load_json(PROFILE_PATH, {"kpis": {}, "guardrails": {}, "loop_cadence": "daily", "iteration_count": 3})


def load_memory() -> list[dict[str, Any]]:
    return load_json(MEMORY_PATH, [])


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


def tool_autoresearch_start(arguments: dict[str, Any]) -> dict[str, Any]:
    profile = load_profile()
    missing = []
    if not arguments.get("north_star") and not profile.get("north_star"):
        missing.append("What north-star outcome should this loop optimize?")
    if not arguments.get("kpis") and not profile.get("kpis"):
        missing.append("Which KPIs should Codex track? Include name, direction, baseline, target, and optional weight.")
    if not arguments.get("iteration_count") and not profile.get("iteration_count"):
        missing.append("How many iterations should Codex attempt before stopping and summarizing?")
    if not arguments.get("browser_enabled"):
        missing.append("Should Codex open and monitor the dashboard with Browser Use or Computer Use?")

    return {
        "generated_at": utc_now_iso(),
        "ready": not missing,
        "missing_questions": missing,
        "recommended_defaults": {
            "iteration_count": int(profile.get("iteration_count", 3)),
            "dashboard_url": "http://localhost:8765/",
            "loop_cadence": profile.get("loop_cadence", "daily"),
        },
        "instructions": [
            "Confirm KPIs and guardrails before changing code.",
            "Serve dashboard with: python3 -m http.server 8765 --directory dashboard",
            "If Browser Use or Computer Use is unavailable, ask the user to enable the plugin before live monitoring.",
            "After each iteration, record experiment result, feedback, shortcomings, and next bet.",
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
        "iteration_count": int(arguments.get("iteration_count", 3)),
        "guardrails": arguments.get("guardrails", {}),
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
    memory = load_memory()
    shortcomings = [m.get("shortcoming", "") for m in memory[-5:] if m.get("shortcoming")]

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
        "guardrails": profile.get("guardrails", {}),
        "recent_learnings": memory[-5:],
        "known_shortcomings": shortcomings,
        "subagent_plans": plans,
    }


def tool_record_experiment_result(arguments: dict[str, Any]) -> dict[str, Any]:
    required = ["iteration", "hypothesis", "change", "outcome"]
    missing = [name for name in required if not arguments.get(name)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    memory = load_memory()
    entry = {
        "timestamp": utc_now_iso(),
        "iteration": int(arguments["iteration"]),
        "focus_kpi": arguments.get("focus_kpi", ""),
        "hypothesis": arguments["hypothesis"],
        "change": arguments["change"],
        "outcome": arguments["outcome"],
        "feedback": arguments.get("feedback", ""),
        "shortcoming": arguments.get("shortcoming", ""),
        "next_bet": arguments.get("next_bet", ""),
        "guardrail_notes": arguments.get("guardrail_notes", ""),
    }
    memory.append(entry)
    save_json(MEMORY_PATH, memory)
    return {"ok": True, "memory_points": len(memory), "latest": entry}


def tool_render_dashboard(arguments: dict[str, Any]) -> dict[str, Any]:
    history = load_history()
    profile = load_profile()
    memory = load_memory()
    plan = load_json(DATA_DIR / "last_subagent_plan.json", {})
    payload = {
        "profile": profile,
        "history": history,
        "memory": memory,
        "plan": plan,
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
        "name": "autoresearch_start",
        "description": "Start an Autoresearch loop and return missing setup questions plus dashboard instructions.",
        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False},
        "inputSchema": {
            "type": "object",
            "properties": {
                "north_star": {"type": "string"},
                "kpis": {"type": "object"},
                "iteration_count": {"type": "number"},
                "browser_enabled": {"type": "boolean"},
            },
        },
    },
    {
        "name": "kpi_interview_questions",
        "description": "Generate KPI discovery questions based on repository context.",
        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False},
        "inputSchema": {"type": "object", "properties": {"product_goal": {"type": "string"}, "company_stage": {"type": "string"}}},
    },
    {
        "name": "save_kpi_profile",
        "description": "Persist KPI profile including direction, targets, and weights.",
        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
        "inputSchema": {
            "type": "object",
            "properties": {
                "north_star": {"type": "string"},
                "loop_cadence": {"type": "string"},
                "iteration_count": {"type": "number"},
                "guardrails": {"type": "object"},
                "kpis": {"type": "object"},
            },
            "required": ["kpis"],
        },
    },
    {
        "name": "update_kpi_snapshot",
        "description": "Append a KPI snapshot to local history storage.",
        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
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
        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False},
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "record_experiment_result",
        "description": "Persist experiment learnings, feedback, shortcomings, and next bets.",
        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
        "inputSchema": {
            "type": "object",
            "properties": {
                "iteration": {"type": "number"},
                "focus_kpi": {"type": "string"},
                "hypothesis": {"type": "string"},
                "change": {"type": "string"},
                "outcome": {"type": "string"},
                "feedback": {"type": "string"},
                "shortcoming": {"type": "string"},
                "next_bet": {"type": "string"},
                "guardrail_notes": {"type": "string"},
            },
            "required": ["iteration", "hypothesis", "change", "outcome"],
        },
    },
    {
        "name": "render_dashboard",
        "description": "Write dashboard/data.json from profile and KPI history.",
        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
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
            "autoresearch_start": tool_autoresearch_start,
            "kpi_interview_questions": tool_kpi_interview_questions,
            "save_kpi_profile": tool_save_kpi_profile,
            "update_kpi_snapshot": tool_update_kpi_snapshot,
            "generate_subagent_plan": tool_generate_subagent_plan,
            "record_experiment_result": tool_record_experiment_result,
            "render_dashboard": tool_render_dashboard,
        }
        if name not in handlers:
            raise ValueError(f"Unknown tool: {name}")
        output = handlers[name](arguments)
        return {"content": [{"type": "text", "text": json.dumps(output, indent=2)}]}
    raise ValueError(f"Unsupported method: {method}")


def response_for_request(payload: dict[str, Any]) -> dict[str, Any]:
    req_id = payload.get("id")
    try:
        req = JsonRpcRequest(id=req_id, method=payload.get("method", ""), params=payload.get("params", {}))
        result = handle(req.method, req.params)
        return {"jsonrpc": "2.0", "id": req.id, "result": result}
    except Exception as exc:  # noqa: BLE001
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}}


def parse_http_rpc_body(raw: bytes) -> list[dict[str, Any]]:
    text = raw.decode("utf-8").strip()
    if not text:
        raise ValueError("Empty JSON-RPC request body")
    parsed = json.loads(text)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    raise ValueError("JSON-RPC request body must be an object or array")


class AutoresearchHttpHandler(BaseHTTPRequestHandler):
    server_version = "AutoresearchMCP/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

    def send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type, authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def send_static(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type, authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/.well-known/openai-apps-challenge":
            self.send_response(200)
            body = OPENAI_APPS_CHALLENGE_TOKEN.encode("utf-8")
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/health":
            self.send_json(200, {"ok": True, "service": "autoresearch", "tools": [tool["name"] for tool in TOOLS]})
            return
        if self.path in {"/mcp", "/mcp/"}:
            self.send_json(
                200,
                {
                    "service": "autoresearch-mcp",
                    "jsonrpc_endpoint": "/mcp",
                    "dashboard": "/",
                    "tools": [tool["name"] for tool in TOOLS],
                },
            )
            return

        rel = "index.html" if self.path in {"/", ""} else unquote(self.path.lstrip("/"))
        candidate = (DASHBOARD_DIR / rel).resolve()
        if DASHBOARD_DIR.resolve() not in candidate.parents and candidate != DASHBOARD_DIR.resolve():
            self.send_error(403)
            return
        self.send_static(candidate)

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/mcp", "/mcp/"}:
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("content-length", "0"))
            payloads = parse_http_rpc_body(self.rfile.read(length))
            responses = [response_for_request(payload) for payload in payloads]
            self.send_json(200, responses if len(responses) > 1 else responses[0])
        except Exception as exc:  # noqa: BLE001
            self.send_json(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}})


def run_http(host: str, port: int) -> None:
    tool_render_dashboard({})
    server = ThreadingHTTPServer((host, port), AutoresearchHttpHandler)
    print(f"Autoresearch HTTP MCP server listening on http://{host}:{port}")
    print(f"Dashboard: http://{host}:{port}/")
    print(f"MCP JSON-RPC endpoint: http://{host}:{port}/mcp")
    server.serve_forever()


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
    parser.add_argument("--stdio", action="store_true", help="Run as stdio server")
    parser.add_argument("--http", action="store_true", help="Run HTTP JSON-RPC server and dashboard")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    args = parser.parse_args()
    if args.http:
        run_http(args.host, args.port)
    else:
        run_stdio()


if __name__ == "__main__":
    main()
