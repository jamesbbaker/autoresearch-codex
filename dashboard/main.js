async function load() {
  const resp = await fetch('./data.json');
  const payload = await resp.json();
  const history = (payload.history || []).slice(-50);

  const meta = document.getElementById('meta');
  meta.textContent = `Snapshots: ${history.length}`;

  if (history.length === 0) return;

  const latest = history[history.length - 1].kpis;
  const prev = history.length > 1 ? history[history.length - 2].kpis : {};
  const cards = document.getElementById('cards');

  Object.entries(latest).forEach(([k, v]) => {
    const d = prev[k] == null ? null : v - prev[k];
    const el = document.createElement('article');
    el.className = 'card';
    const deltaCls = d == null ? '' : d >= 0 ? 'delta-pos' : 'delta-neg';
    el.innerHTML = `
      <div class="label">${k}</div>
      <div class="value">${Number(v).toFixed(4)}</div>
      <div class="${deltaCls}">${d == null ? '—' : `Δ ${d.toFixed(4)}`}</div>
    `;
    cards.appendChild(el);
  });

  const labels = history.map((h) => new Date(h.timestamp).toLocaleString());
  const allKpis = Object.keys(latest);
  const datasets = allKpis.map((name, i) => {
    const hue = (i * 77) % 360;
    return {
      label: name,
      data: history.map((h) => h.kpis[name]),
      borderColor: `hsl(${hue}deg 80% 60%)`,
      tension: 0.25,
    };
  });

  new Chart(document.getElementById('kpiChart'), {
    type: 'line',
    data: { labels, datasets },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

load();
