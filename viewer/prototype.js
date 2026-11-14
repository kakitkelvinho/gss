// Throwaway UI prototype. The viewer uses verifier-only snapshots from runs_bundle.js.
const runs = window.GSS_RUNS_BUNDLE?.runs.filter(run => run.trajectory?.length) ?? [];
const app = document.getElementById('app');
const state = { run: 3, step: Math.max(0, Number(new URLSearchParams(location.search).get('step') ?? 108)), playing: false, speed: 1, timer: null, menu: null };

function esc(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]); }
function fmtTime(seconds) { const n = Math.round(seconds || 0); return `${Math.floor(n / 3600)}:${String(Math.floor(n % 3600 / 60)).padStart(2, '0')}:${String(n % 60).padStart(2, '0')}`; }
function money(n) { return `€${Math.round(n || 0).toLocaleString('en-US')}`; }
function currentRun() { return runs[state.run] || runs[0]; }
function currentCall() { return currentRun()?.trajectory[Math.min(state.step, currentRun().trajectory.length - 1)]; }
function shortArgs(args) { const parts = Object.entries(args || {}).slice(0, 2).map(([key, value]) => value && typeof value === 'object' ? `${Object.keys(value).length} ${key}` : `${key} ${typeof value === 'number' ? Number(value.toFixed(2)) : String(value).slice(0, 18)}`); return parts.join(' · ') || '—'; }
function cleanTool(tool) { return (tool || 'tool').replaceAll('_', ' '); }
function contextFor(call) { const t = call.tool || ''; if (/read_manual|get_datasheet/.test(t)) return { verb: 'Reading the optics manual', pose: 'manual' }; if (/buy|catalogue/.test(t)) return { verb: 'Choosing lab equipment', pose: 'buy' }; if (/place|knob|move_stage|steer/.test(t)) return { verb: 'Adjusting the optical path', pose: 'adjust' }; if (/scan|signal|camera|ir_card|measure/.test(t)) return { verb: 'Taking a measurement', pose: 'measure' }; return { verb: 'Working through the run', pose: 'observe' }; }

function project(p) { return { x: 520 + (p.x - 1200) * .246 - (p.z - 600) * .204, y: 335 + (p.x - 1200) * .070 + (p.z - 600) * .140 - (p.h || 0) * .39 }; }
function at(p) { const q = project(p); return `${q.x.toFixed(1)},${q.y.toFixed(1)}`; }
function partSvg(part) {
  const p = project(part.pos), id = esc(part.id), kind = part.kind;
  const base = `<ellipse cx="0" cy="0" rx="20" ry="8" fill="#162c36" stroke="#8da19e" stroke-width="2"/><ellipse cx="0" cy="-2" rx="10" ry="4" fill="#b5b7a8"/><path d="M-7 -4 L-7 -40 Q0 -44 7 -40 L7 -4" fill="url(#metal)" stroke="#6e8587" stroke-width="1"/>`;
  let head = '';
  if (kind === 'mirror') head = `<g transform="translate(0,-45) rotate(${(part.yaw_deg || 0) * .35})"><rect x="-17" y="-16" width="34" height="28" rx="3" fill="#39494e" stroke="#c4c6b8" stroke-width="2"/><ellipse cx="0" cy="-3" rx="12" ry="11" fill="url(#mirror)" stroke="#f6f2e4" stroke-width="2"/><circle cx="18" cy="-9" r="4" fill="#d0a562"/><circle cx="18" cy="4" r="4" fill="#b3aaa0"/><path d="M-18 14 L18 14" stroke="#263944" stroke-width="5"/></g>`;
  if (kind === 'stage') head = `<g transform="translate(0,-44)"><rect x="-28" y="-18" width="56" height="33" rx="3" fill="#485861" stroke="#c7c2b1" stroke-width="2"/><path d="M-24 -12 L24 -12 M-24 8 L24 8" stroke="#d8b779" stroke-width="2"/><rect x="-17" y="-25" width="34" height="8" fill="#a7ada7"/><circle cx="-22" cy="1" r="5" fill="#2b3c41"/><circle cx="22" cy="1" r="5" fill="#2b3c41"/><path d="M-8 -18 L-8 -9 M8 -18 L8 -9" stroke="#ece6d5" stroke-width="3"/></g>`;
  if (kind === 'periscope') head = `<g transform="translate(0,-43)"><rect x="-10" y="-47" width="20" height="48" rx="2" fill="#68767a" stroke="#c9c3ad" stroke-width="2"/><ellipse cx="0" cy="-42" rx="13" ry="6" fill="url(#mirror)" stroke="#dbe1db" stroke-width="2"/><ellipse cx="0" cy="-1" rx="13" ry="6" fill="url(#mirror)" stroke="#dbe1db" stroke-width="2"/><circle cx="13" cy="-24" r="4" fill="#d7a76b"/></g>`;
  if (kind === 'sample') head = `<g transform="translate(0,-43)"><rect x="-34" y="-10" width="68" height="13" rx="2" fill="#465560" stroke="#b5b6ac" stroke-width="2"/><ellipse cx="0" cy="-11" rx="20" ry="8" fill="#d1af79" stroke="#f1d9a0" stroke-width="2"/><circle cx="0" cy="-11" r="5" fill="#eec99e"/><path d="M-22 -21 L-22 -9 M22 -21 L22 -9" stroke="#b7c1bb" stroke-width="5"/><ellipse cx="-22" cy="-22" rx="6" ry="9" fill="#8bd0d1" fill-opacity=".5" stroke="#c6f1e8"/><ellipse cx="22" cy="-22" rx="6" ry="9" fill="#8bd0d1" fill-opacity=".5" stroke="#c6f1e8"/></g>`;
  return `<g transform="translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})" aria-label="${id} ${kind}">${base}${head}<title>${id}</title></g>`;
}
function housingSvg(x, z, label, color) {
  const p = project({ x, z, h: 140 });
  return `<g transform="translate(${p.x} ${p.y})"><path d="M-66 -26 L-18 -50 L70 -18 L20 6 Z" fill="#e1e1d6" stroke="#f7f5e9" stroke-width="2"/><path d="M-66 -26 L20 6 L20 42 L-66 10 Z" fill="#aeb7b0"/><path d="M20 6 L70 -18 L70 17 L20 42 Z" fill="#85989a"/><path d="M-35 0 L-35 99 M40 23 L40 111" stroke="#465963" stroke-width="9"/><ellipse cx="-36" cy="99" rx="22" ry="7" fill="#2a3d45"/><ellipse cx="40" cy="111" rx="22" ry="7" fill="#2a3d45"/><rect x="-62" y="-15" width="28" height="14" rx="2" fill="${color}"/><circle cx="-61" cy="-8" r="7" fill="${color}" stroke="#ffede1" stroke-width="1"/><text class="label tag" x="-4" y="-21" text-anchor="middle">${label}</text></g>`;
}
function robotSvg(pose, targetPart) {
  // The front table edge is y ~= 306 + .28x. Keep the robot's entire body beyond it.
  const x = pose === 'manual' || pose === 'buy' ? 180 : Math.max(370, Math.min(720, project(targetPart?.pos || { x: 1200, z: 600 }).x));
  const y = Math.min(655, Math.max(550, 445 + .28 * x));
  const bent = pose === 'adjust' || pose === 'manual';
  const worktop = pose === 'manual' || pose === 'buy' || pose === 'measure'
    ? `<g><path d="M47 -68 L124 -91 L172 -72 L95 -48 Z" fill="#5b6768" stroke="#a1aaaa" stroke-width="2"/><path d="M47 -68 L95 -48 L95 -41 L47 -61 Z" fill="#39474a"/><path d="M95 -48 L172 -72 L172 -65 L95 -41 Z" fill="#303d40"/><path d="M65 -56 L65 7 M148 -72 L148 -4" stroke="#657273" stroke-width="6"/></g>` : '';
  const prop = pose === 'manual'
    ? `<g transform="translate(110,-66)"><path d="M-35 0 L0 -12 L35 0 L0 11 Z" fill="#d7d6c8" stroke="#eee9d8" stroke-width="2"/><path d="M0 -12 L0 11 M-27 -1 L-7 -6 M8 -6 L28 -1" stroke="#657476"/></g>`
    : pose === 'buy'
      ? `<g transform="translate(108,-74)"><rect x="-25" y="-18" width="50" height="34" rx="2" fill="#1d343b" stroke="#9aaba9"/><text x="0" y="7" text-anchor="middle" fill="#d7a865" font-size="20">€</text></g><g transform="translate(27,-182)"><rect x="-22" y="-22" width="44" height="44" rx="5" fill="#2a3536" stroke="#d7a865"/><text x="0" y="11" text-anchor="middle" fill="#d7a865" font-size="30">€</text></g>`
      : pose === 'measure'
        ? `<g transform="translate(109,-78)"><rect x="-26" y="-22" width="52" height="38" rx="2" fill="#20363a" stroke="#a6b7b4"/><path d="M-20 0 L-8 -4 L0 2 L12 -14 L21 -8" fill="none" stroke="#85c5c8" stroke-width="2"/></g>` : '';
  const arms = pose === 'manual'
    ? `<path d="M-19 -106 L27 -88 L80 -78 M25 -107 L65 -77 L98 -67" fill="none" stroke="#8b9898" stroke-width="13" stroke-linecap="round"/><circle cx="80" cy="-78" r="6" fill="#b2bfbc"/><circle cx="98" cy="-67" r="6" fill="#b2bfbc"/>`
    : bent
    ? `<path d="M-19 -106 L14 -111 L52 -142 M26 -107 L59 -112 L85 -132" fill="none" stroke="#8b9898" stroke-width="13" stroke-linecap="round"/><circle cx="52" cy="-142" r="6" fill="#b2bfbc"/><circle cx="85" cy="-132" r="6" fill="#b2bfbc"/>`
    : `<path d="M-19 -108 L-33 -68 L-14 -57 M24 -108 L56 -75 L93 -82" fill="none" stroke="#8b9898" stroke-width="13" stroke-linecap="round"/><circle cx="-14" cy="-57" r="6" fill="#b2bfbc"/><circle cx="93" cy="-82" r="6" fill="#b2bfbc"/>`;
  return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})"><ellipse cx="0" cy="3" rx="42" ry="11" fill="#0c1416" opacity=".45"/>${worktop}<path d="M-17 -63 L-23 -3 L-5 -3 L2 -61 M15 -63 L24 -3 L42 -3 L27 -63" fill="#576669" stroke="#8e9d9b" stroke-width="2"/><path d="M-27 -113 Q0 -130 30 -112 L29 -65 L-24 -65 Z" fill="#697777" stroke="#b4beb9" stroke-width="2"/><path d="M-24 -90 L27 -90" stroke="#45575a" stroke-width="4"/>${arms}<g transform="translate(${bent ? 19 : 2} -143) rotate(${bent ? 20 : 0})"><path d="M-22 -20 L16 -20 L22 -11 L20 15 L-19 15 L-23 -8 Z" fill="#a9b4b0" stroke="#d7dcd4" stroke-width="2"/><rect x="-17" y="-9" width="35" height="15" rx="3" fill="#273a3d"/><path d="M-11 -2 H-5 M5 -2 H11" stroke="#9bc8c7" stroke-width="3"/><circle cx="0" cy="-23" r="4" fill="#c1cbc4"/></g>${prop}</g>`;
}
function sceneSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {}, action = contextFor(call);
  const target = /place|knob|move_stage|steer/.test(call.tool) ? parts.find(p => Object.values(call.args || {}).includes(p.id)) || parts[parts.length - 1] : parts.find(p => p.kind === 'sample');
  const dots = [];
  for (let x = 0; x <= 2400; x += 100) for (let z = 0; z <= 1200; z += 100) { const p = project({ x, z, h: 0 }); dots.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="1.1" fill="#809395" opacity=".56"/>`); }
  const lines = [['800nm', '#ed745b'], ['opa', '#6dc9d1']].map(([key, color]) => (beams[key]?.open ? (beams[key].segments || []).map(segment => `<path d="M${at(segment[0])} L${at(segment[1])}" stroke="${color}" stroke-width="6" opacity=".16"/><path d="M${at(segment[0])} L${at(segment[1])}" stroke="${color}" stroke-width="2.4" stroke-linecap="round"/>`).join('') : '')).join('');
  const table = `<path d="M${at({x:0,z:0})} L${at({x:2400,z:0})} L${at({x:2400,z:1200})} L${at({x:0,z:1200})} Z" fill="url(#table)" stroke="#c3c9bd" stroke-width="3"/><path d="M${at({x:0,z:1200})} L${at({x:2400,z:1200})} l0 22 L${at({x:0,z:1200})} Z" fill="#213b43" opacity=".6"/>${dots.join('')}`;
  return `<svg viewBox="0 0 1040 700" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Optical table with mounted components and a robot working beside the table"><defs><linearGradient id="table" x2="1" y2="1"><stop stop-color="#687579"/><stop offset="1" stop-color="#3b4b50"/></linearGradient><linearGradient id="metal"><stop stop-color="#526469"/><stop offset=".45" stop-color="#e1e1d6"/><stop offset="1" stop-color="#66777a"/></linearGradient><radialGradient id="mirror"><stop stop-color="#e2f1ec"/><stop offset=".55" stop-color="#93afb4"/><stop offset="1" stop-color="#4d6369"/></radialGradient></defs><rect width="1040" height="700" fill="#20282b"/><ellipse cx="525" cy="517" rx="440" ry="84" fill="#101719" opacity=".45"/>${table}${lines}${housingSvg(2320,294,'800 nm','#cc6b5c')}${housingSvg(2320,935,'OPA','#6eafb6')}${parts.map(partSvg).join('')}${robotSvg(action.pose,target)}</svg>`;
}
function mapSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {};
  const sx = x => 12 + x / 2400 * 306, sz = z => 10 + z / 1200 * 150;
  const beam = [['800nm','#ed745b'],['opa','#6dc9d1']].map(([key,color]) => beams[key]?.open ? (beams[key].segments || []).map(seg => `<path d="M${sx(seg[0].x)},${sz(seg[0].z)} L${sx(seg[1].x)},${sz(seg[1].z)}" stroke="${color}" stroke-width="2.2" stroke-linecap="round"/>`).join('') : '').join('');
  return `<svg class="map-svg" viewBox="0 0 330 170" role="img" aria-label="Top down layout of the optical table"><rect x="12" y="10" width="306" height="150" rx="2" fill="#28444d" stroke="#c1c5b8"/><path d="M88.5 10 V160 M165 10 V160 M241.5 10 V160 M12 47.5 H318 M12 85 H318 M12 122.5 H318" stroke="#739091" stroke-width=".6" opacity=".5"/>${beam}${parts.map(p=>`<g><circle cx="${sx(p.pos.x)}" cy="${sz(p.pos.z)}" r="4.5" fill="#e3d8b7" stroke="#102831" stroke-width="1.3"/><title>${esc(p.id)}</title></g>`).join('')}<rect x="299" y="29" width="19" height="35" fill="#d1d0c2"/><rect x="299" y="108" width="19" height="35" fill="#d1d0c2"/></svg>`;
}
function scoreSvg(run, step) {
  const trajectory = run.trajectory, end = Math.max(1, step), values = trajectory.slice(0, end + 1).map(t => Math.max(0, Math.min(1, Number(t.truth?.reward || 0))));
  const path = values.map((v, i) => `${i ? 'L' : 'M'}${(i / Math.max(end, 1) * 270).toFixed(1)},${(32 - v * 29).toFixed(1)}`).join(' ');
  return `<svg class="graph" viewBox="0 0 270 34" preserveAspectRatio="none" aria-label="Score history"><path d="M0 32 H270" stroke="var(--line)"/><path d="${path}" fill="none" stroke="var(--accent)" stroke-width="2.5" vector-effect="non-scaling-stroke"/></svg>`;
}
function runName(run) { return `${run.model === 'oracle' ? 'Oracle' : 'AI run'} · L${run.meta.level} · ${run.meta.opa_lambda_nm} nm`; }
function menuMarkup(call) {
  if (state.menu === 'parts') {
    const parts = call.snapshot?.parts || [];
    return `<div class="flyout parts-flyout" role="menu" aria-label="Parts"><div class="flyout-title">Parts · ${parts.length}</div>${parts.map((part, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}"><span class="mini-icon">${part.kind === 'mirror' ? '◉' : part.kind === 'stage' ? '▤' : '◇'}</span><span>${esc(part.id)}</span></button>`).join('')}</div>`;
  }
  if (state.menu === 'view') return `<div class="flyout view-flyout" role="menu" aria-label="View"><div class="flyout-title">Top view</div><button class="flyout-item" role="menuitem" tabindex="0" data-action="close-menu"><span class="mini-icon">▣</span><span>Isometric view</span></button>${mapSvg(call)}</div>`;
  return '';
}
function render() {
  const run = currentRun(), call = currentCall(); if (!run || !call) { app.textContent = 'No run snapshots found.'; return; }
  const trajectory = run.trajectory, score = Number(call.truth?.reward || 0);
  const rows = trajectory.map((t, index) => `<button class="call-row ${index === state.step ? 'active' : ''}" data-step="${index}" aria-current="${index === state.step ? 'step' : 'false'}"><span class="number">${String(index + 1).padStart(3, '0')}</span><span class="summary">${esc(cleanTool(t.tool))}${Object.keys(t.args || {}).length ? ` · ${esc(shortArgs(t.args))}` : ''}</span><span class="mark">${t.result?.error ? '!' : index === state.step ? '●' : ''}</span></button>`).join('');
  app.innerHTML = `<main class="app"><section class="scene-shell"><div class="scene">${sceneSvg(call)}</div></section><div class="player" aria-label="Playback"><select class="run-picker" aria-label="AI run">${runs.map((r,i)=>`<option value="${i}" ${i===state.run?'selected':''}>${esc(runName(r))}</option>`).join('')}</select><button data-action="prev" aria-label="Previous step" title="Previous step">‹</button><button data-action="play" aria-label="${state.playing ? 'Pause' : 'Play'}" aria-pressed="${state.playing}" title="Space">${state.playing ? 'Ⅱ' : '▶'}</button><button data-action="next" aria-label="Next step" title="Next step">›</button><input class="scrub" type="range" min="0" max="${trajectory.length-1}" value="${state.step}" aria-label="Scrub steps"><span class="counter">${state.step+1}/${trajectory.length}</span><select class="speed" aria-label="Playback speed"><option value="1" ${state.speed===1?'selected':''}>1×</option><option value="2" ${state.speed===2?'selected':''}>2×</option><option value="4" ${state.speed===4?'selected':''}>4×</option></select></div><aside class="sidebar"><section class="call-panel"><div class="panel-heading">Steps <small>${trajectory.length} tool calls</small></div><div class="call-stack">${rows}</div></section><section class="score-panel"><div class="score-heading">Score</div><div class="score-line"><strong>${score.toFixed(3)}</strong><small>/ 1 · replay diagnostic</small></div>${scoreSvg(run,state.step)}<div class="totals"><div><span>Money</span><strong>${money(call.snapshot?.cost_eur)}</strong></div><div><span>Lab time</span><strong>${fmtTime(call.t_s)}</strong></div></div></section></aside><button class="corner-button parts-trigger" data-action="parts" aria-label="Parts" aria-expanded="${state.menu === 'parts'}" aria-haspopup="menu" title="Parts">≡</button><span class="hint">Parts</span><button class="corner-button view-trigger" data-action="view" aria-label="View" aria-expanded="${state.menu === 'view'}" aria-haspopup="menu" title="View">▣</button>${menuMarkup(call)}</main>`;
  const active = app.querySelector('.call-row.active'); active?.scrollIntoView({ block: 'nearest' });
}
function changeStep(next) { const max = currentRun().trajectory.length - 1; state.step = Math.max(0, Math.min(max, next)); if (state.step === max && state.playing) stop(); render(); }
function stop() { state.playing = false; clearInterval(state.timer); state.timer = null; }
function togglePlay() { if (state.playing) { stop(); render(); return; } if (state.step >= currentRun().trajectory.length - 1) state.step = 0; state.playing = true; state.timer = setInterval(() => changeStep(state.step + 1), 720 / state.speed); render(); }
function setMenu(menu) { state.menu = state.menu === menu ? null : menu; render(); if (state.menu) app.querySelector('.flyout-item')?.focus(); else app.querySelector(`[data-action="${menu}"]`)?.focus(); }
app.addEventListener('click', e => { const button = e.target.closest('button'); if (!button) return; if (button.dataset.step !== undefined) { changeStep(Number(button.dataset.step)); return; } switch (button.dataset.action) { case 'prev': changeStep(state.step-1); break; case 'play': togglePlay(); break; case 'next': changeStep(state.step+1); break; case 'parts': setMenu('parts'); break; case 'view': setMenu('view'); break; case 'close-menu': setMenu(state.menu); break; } });
app.addEventListener('input', e => { if (e.target.matches('input[type=range]')) changeStep(Number(e.target.value)); });
app.addEventListener('change', e => { if (e.target.matches('.run-picker')) { stop(); state.run = Number(e.target.value); state.step = currentRun().trajectory.length - 2; render(); } if (e.target.matches('.speed')) { state.speed=Number(e.target.value); if (state.playing) { stop(); togglePlay(); } else render(); } });
document.addEventListener('pointerdown', e => { if (state.menu && !e.target.closest('.flyout,.parts-trigger,.view-trigger')) { const menu = state.menu; state.menu = null; render(); app.querySelector(`[data-action="${menu}"]`)?.focus(); } });
document.addEventListener('keydown', e => {
  if (state.menu && e.key === 'Escape') { e.preventDefault(); setMenu(state.menu); return; }
  const items = [...app.querySelectorAll('.flyout-item')];
  if (state.menu && items.length && ['ArrowDown','ArrowUp','Home','End'].includes(e.key)) {
    e.preventDefault(); const current = items.indexOf(document.activeElement);
    const next = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : (current + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
    items.forEach((item, i) => item.tabIndex = i === next ? 0 : -1); items[next].focus(); return;
  }
  if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable) return;
  if (e.key === 'Escape') { state.menu = null; render(); return; }
  if (e.key === 'ArrowLeft') changeStep(state.step - 1);
  if (e.key === 'ArrowRight') changeStep(state.step + 1);
  if (e.key === ' ') { e.preventDefault(); togglePlay(); }
});
render();
