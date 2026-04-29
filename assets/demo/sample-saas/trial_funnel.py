"""Tiny demo SaaS trial funnel module used by the Autoresearch demo."""

from __future__ import annotations

def activation_checklist(account: dict) -> list[str]:
    """Return onboarding steps for a trial account."""
    steps = []
    if not account.get("has_data"):
        steps.append("import_data")
    if account.get("team_size", 1) < 2:
        steps.append("invite_teammate")
    if not account.get("billing_connected"):
        steps.append("connect_billing")
    if account.get("reports_created", 0) < 1:
        steps.append("first_report")
    return steps


def qualified_trial_score(account: dict) -> float:
    """Estimate whether a trial is likely to convert."""
    score = 0.20
    if account.get("has_data"):
        score += 0.20
    if account.get("team_size", 1) > 1:
        score += 0.15
    if account.get("billing_connected"):
        score += 0.20
    if account.get("reports_created", 0) > 0:
        score += 0.15
    return min(score, 1.0)


def render_dashboard_summary(events: list[dict]) -> dict:
    """Summarize dashboard state for trial users."""
    activated = sum(1 for event in events if event.get("activated"))
    converted = sum(1 for event in events if event.get("converted"))
    total = len(events) or 1
    return {
        "activation_rate": activated / total,
        "conversion_rate": converted / total,
        "accounts": len(events),
    }
