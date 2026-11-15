const app = document.getElementById('app');
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = value => value == null ? '—' : Number(value).toFixed(3);
function render(index) {
  const s = index.summary;
  app.innerHTML = `<header><h1>Run archive</h1><a class="home" href="prototype.html">← Replay viewer</a></header>
    <p class="intro">Verified simulator replays shared by contributors. Rewards are the recorded verifier scores; runs marked “old scorer” used an earlier grading formula. Model results should be compared within the same level and scorer.</p>
    <div class="cards"><div class="card"><span>Runs</span><strong>${s.count}</strong></div><div class="card"><span>Mean reward</span><strong>${fmt(s.mean_reward)}</strong></div><div class="card"><span>Median reward</span><strong>${fmt(s.median_reward)}</strong></div><div class="card"><span>Best reward</span><strong>${fmt(s.best_reward)}</strong></div></div>
    <p class="muted">Harbor token usage available for ${s.usage_covered_runs} of ${s.count} runs: ${s.total_input_tokens.toLocaleString()} input tokens (including cached input), ${s.total_output_tokens.toLocaleString()} output tokens. Reported API cost: $${s.total_cost_usd.toFixed(2)} across ${s.cost_covered_runs} runs with cost data.</p>
    <h2>By model and level</h2><div class="table-wrap"><table><thead><tr><th>Model</th><th>Level</th><th>Runs</th><th>Mean R</th><th>Median R</th><th>Best R</th><th>Old scorer</th><th>Usage records</th></tr></thead><tbody>${index.by_model_level.map(g => `<tr><td>${esc(g.model)}</td><td>L${g.level}</td><td>${g.count}</td><td class="number">${fmt(g.mean_reward)}</td><td class="number">${fmt(g.median_reward)}</td><td class="number">${fmt(g.best_reward)}</td><td>${g.old_scorer_count}</td><td>${g.usage_covered_runs}/${g.count}</td></tr>`).join('')}</tbody></table></div>
    <div class="toolbar"><h2>All runs</h2><label>Model <select id="model-filter"><option value="">All models</option>${[...new Set(index.runs.map(r => r.model))].sort().map(m => `<option value="${esc(m)}">${esc(m)}</option>`).join('')}</select></label></div>
    <div class="table-wrap"><table><thead><tr><th>Run</th><th>Model</th><th>Seed</th><th>Level</th><th>Reward</th><th>Calls</th><th>Wall min</th><th>Tokens in/out</th><th>API USD</th><th>Ended</th><th>Failure tags</th></tr></thead><tbody id="run-rows"></tbody></table></div>
    <p class="muted">Runs without recorded steps count in statistics but have no replay link. Scores from different scorer versions are shown as recorded.</p>`;
  const rows = app.querySelector('#run-rows');
  function draw() {
    const model = app.querySelector('#model-filter').value;
    rows.innerHTML = index.runs.filter(r => !model || r.model === model).map(r => `<tr><td>${r.replayable ? `<a href="prototype.html?run=${encodeURIComponent(r.id)}">Replay ↗</a>` : 'No replay'}<div class="muted">${esc(r.id)}</div></td><td>${esc(r.model)}</td><td>${r.seed}</td><td>L${r.level}</td><td class="number">${fmt(r.reward)}${r.old_scorer ? '<div class="muted">old scorer</div>' : ''}</td><td>${r.tool_calls ?? '—'}</td><td>${r.agent_usage?.wall_time_s != null ? (r.agent_usage.wall_time_s/60).toFixed(1) : '—'}</td><td>${r.agent_usage?.n_input_tokens?.toLocaleString() ?? '—'} / ${r.agent_usage?.n_output_tokens?.toLocaleString() ?? '—'}</td><td>${r.agent_usage?.cost_usd != null ? '$'+r.agent_usage.cost_usd.toFixed(2) : '—'}</td><td>${esc(r.ended_by)}</td><td>${r.failure_tags.map(t => `<span class="tag">${esc(t)}</span>`).join('') || '—'}</td></tr>`).join('');
  }
  app.querySelector('#model-filter').addEventListener('change', draw);
  draw();
}
fetch('runs_index.json').then(response => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then(index => {
  if (index.schema_version !== 'gss.archive.v1') throw new Error('unsupported archive schema');
  render(index);
}).catch(error => { app.textContent = `Could not load archive: ${error.message}`; });
