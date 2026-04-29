from __future__ import annotations

import time

from trial_funnel import activation_checklist, qualified_trial_score, render_dashboard_summary


def test_activation_checklist_drives_trial_to_paid_conversion():
    account = {"has_data": False, "team_size": 1, "billing_connected": False}
    steps = activation_checklist(account)

    assert "import_data" in steps
    assert "invite_teammate" in steps
    assert "connect_billing" in steps
    assert "first_report" in steps


def test_qualified_trial_score_rewards_conversion_signals():
    weak = {"has_data": False, "team_size": 1, "billing_connected": False, "reports_created": 0}
    strong = {"has_data": True, "team_size": 4, "billing_connected": True, "reports_created": 2}

    assert qualified_trial_score(strong) >= 0.70
    assert qualified_trial_score(strong) > qualified_trial_score(weak)


def test_dashboard_summary_meets_latency_guardrail():
    events = [{"activated": i % 2 == 0, "converted": i % 5 == 0} for i in range(400)]
    started = time.perf_counter()
    summary = render_dashboard_summary(events)
    elapsed = time.perf_counter() - started

    assert summary["activation_rate"] == 0.5
    assert summary["conversion_rate"] == 0.2
    assert elapsed < 0.12
