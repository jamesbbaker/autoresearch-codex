const fmt = new Intl.NumberFormat(undefined, { maximumFractionDigits: 4 });

function number(value) {
  const n = Number(value);
  return Number.isFinite(n) ? fmt.format(n) : "N/A";
}

function progressFor(value, spec) {
  const baseline = Number(spec.baseline ?? 0);
  const target = Number(spec.target ?? value);
  const current = Number(value);
  const span = target - baseline;
  if (!Number.isFinite(span) || span === 0) return 100;
  const raw = ((current - baseline) / span) * 100;
  return Math.max(0, Math.min(100, raw));
}

function isGoodDelta(delta, direction) {
  if (delta == null) return null;
  return direction === "minimize" ? delta <= 0 : delta >= 0;
}

function item(title, body) {
  const el = document.createElement("div");
  el.className = "list-item";
  el.innerHTML = `<strong>${title}</strong><p>${body}</p>`;
  return el;
}

async function load() {
  const resp = await fetch("./data.json", { cache: "no-store" });
  const payload = await resp.json();
  const history = (payload.history || []).slice(-80);
  const profile = payload.profile || { kpis: {} };
  const memory = payload.memory || [];
  const plan = payload.plan || {};

  document.getElementById("northStar").textContent = profile.north_star || "Not configured";
  document.getElementById("iterationCount").textContent = profile.iteration_count || 0;
  document.getElementById("updatedAt").textContent = payload.updated_at
    ? new Date(payload.updated_at).toLocaleString()
    : "Never rendered";
  document.getElementById("status").textContent = history.length ? "Ready" : "Needs baseline";

  const latest = history.length ? history[history.length - 1].kpis : {};
  const prev = history.length > 1 ? history[history.length - 2].kpis : {};
  document.getElementById("focusKpi").textContent = plan.focus_kpi || Object.keys(latest)[0] || "Awaiting snapshot";

  renderHealth(profile, history, memory);
  renderCards(profile, latest, prev);
  renderGuardrails(profile.guardrails || {});
  renderMemory(memory);
  renderPlans(plan.subagent_plans || []);
  renderChart(history, latest);
}

function renderHealth(profile, history, memory) {
  const health = document.getElementById("healthList");
  health.replaceChildren();
  const checks = [
    ["KPI profile", Object.keys(profile.kpis || {}).length ? "Configured" : "Missing"],
    ["Snapshots", history.length ? `${history.length} captured` : "No baseline"],
    ["Experiment memory", memory.length ? `${memory.length} learnings` : "No experiments recorded"],
  ];
  checks.forEach(([title, body]) => {
    const el = document.createElement("div");
    el.className = "health-item";
    el.innerHTML = `<strong>${title}</strong><p>${body}</p>`;
    health.appendChild(el);
  });
}

function renderCards(profile, latest, prev) {
  const cards = document.getElementById("cards");
  cards.replaceChildren();
  const entries = Object.entries(latest);
  if (!entries.length) {
    cards.innerHTML = `<p class="empty">Run onboarding to capture the first KPI snapshot.</p>`;
    return;
  }

  entries.forEach(([name, value]) => {
    const spec = profile.kpis?.[name] || {};
    const direction = spec.direction || "maximize";
    const delta = prev[name] == null ? null : Number(value) - Number(prev[name]);
    const good = isGoodDelta(delta, direction);
    const pct = progressFor(value, spec);
    const el = document.createElement("article");
    el.className = "card";
    el.innerHTML = `
      <div class="card-top">
        <div>
          <p class="kpi-name">${name}</p>
          <p class="label">${direction}</p>
        </div>
        <span class="tag">${Math.round(pct)}%</span>
      </div>
      <div class="value">${number(value)}</div>
      <div class="target">Target ${number(spec.target)}</div>
      <div class="delta ${good === null ? "" : good ? "good" : "bad"}">${delta == null ? "No prior delta" : `Delta ${number(delta)}`}</div>
      <div class="progress"><div class="bar" style="width: ${pct}%"></div></div>
    `;
    cards.appendChild(el);
  });
}

function renderGuardrails(guardrails) {
  const box = document.getElementById("guardrails");
  box.replaceChildren();
  const entries = Object.entries(guardrails);
  if (!entries.length) {
    box.innerHTML = `<p class="empty">No guardrails configured.</p>`;
    return;
  }
  entries.forEach(([name, spec]) => {
    box.appendChild(item(name, `${spec.direction || "watch"} threshold ${number(spec.threshold)}`));
  });
}

function renderMemory(memory) {
  const box = document.getElementById("memory");
  box.replaceChildren();
  if (!memory.length) {
    box.innerHTML = `<p class="empty">Experiment results will appear after the first recorded iteration.</p>`;
    return;
  }
  memory.slice(-6).reverse().forEach((m) => {
    const el = document.createElement("div");
    el.className = "memory-item";
    el.innerHTML = `
      <strong>Iteration ${m.iteration}: ${m.focus_kpi || "general"}</strong>
      <p><b>Hypothesis:</b> ${m.hypothesis}</p>
      <p><b>Outcome:</b> ${m.outcome}</p>
      ${m.shortcoming ? `<p><b>Shortcoming:</b> ${m.shortcoming}</p>` : ""}
      ${m.next_bet ? `<p><b>Next bet:</b> ${m.next_bet}</p>` : ""}
    `;
    box.appendChild(el);
  });
}

function renderPlans(plans) {
  const box = document.getElementById("plans");
  box.replaceChildren();
  if (!plans.length) {
    box.innerHTML = `<p class="empty">Generate a subagent plan to populate next work.</p>`;
    return;
  }
  plans.forEach((plan) => {
    box.appendChild(item(plan.agent, `${plan.objective} ${plan.deliverable ? `Deliverable: ${plan.deliverable}` : ""}`));
  });
}

function renderChart(history, latest) {
  if (!history.length) return;
  const labels = history.map((h) => new Date(h.timestamp).toLocaleString());
  const palette = ["#2563eb", "#138a5b", "#c2413b", "#9a6700", "#6941c6", "#087990"];
  const datasets = Object.keys(latest).map((name, i) => ({
    label: name,
    data: history.map((h) => h.kpis[name]),
    borderColor: palette[i % palette.length],
    backgroundColor: palette[i % palette.length],
    pointRadius: 2,
    borderWidth: 2,
    tension: 0.24,
  }));

  new Chart(document.getElementById("kpiChart"), {
    type: "line",
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { position: "bottom" } },
      scales: {
        x: { ticks: { maxTicksLimit: 6 } },
        y: { beginAtZero: false },
      },
    },
  });
}

load().catch((error) => {
  document.getElementById("status").textContent = "Data error";
  console.error(error);
});
