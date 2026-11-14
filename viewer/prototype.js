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
  const tableY = project({ x: part.pos.x, z: part.pos.z, h: 0 }).y - p.y;
  const base = `<ellipse cx="0" cy="${tableY.toFixed(1)}" rx="20" ry="7" fill="#363248" stroke="#d7c4bb" stroke-width="1.5"/><ellipse cx="0" cy="${(tableY - 2).toFixed(1)}" rx="10" ry="3.5" fill="#a8abb0"/><path d="M-5 9 L-5 ${tableY - 2} Q0 ${tableY + 2} 5 ${tableY - 2} L5 9 Z" fill="url(#metal)" stroke="#656b79" stroke-width="1.5"/><rect x="-11" y="7" width="22" height="10" rx="2" fill="#626b75" stroke="#b9b9b4" stroke-width="1"/>`;
  let head = '';
  if (kind === 'mirror') head = `<g transform="rotate(${(part.yaw_deg || 0) * .35})"><path d="M-20 -17 L12 -17 L20 -9 L20 15 L-20 15 Z" fill="#555765" stroke="#c6c0be" stroke-width="2"/><path d="M-20 -17 L-14 -22 L18 -22 L12 -17 Z" fill="#a6a4a8"/><ellipse cx="-2" cy="-1" rx="13" ry="13" fill="url(#mirror)" stroke="#eee5da" stroke-width="2.5"/><path d="M-15 -5 Q-1 -15 10 -4" fill="none" stroke="#fff7ee" stroke-width="1" opacity=".7"/><circle cx="19" cy="-14" r="5" fill="url(#metal)" stroke="#3b4051"/><circle cx="19" cy="12" r="5" fill="url(#metal)" stroke="#3b4051"/><path d="M15 -14 H23 M15 12 H23" stroke="#53515d" stroke-width="1"/></g>`;
  if (kind === 'stage') head = `<g><path d="M-34 -13 L29 -13 L36 -7 L36 14 L-34 14 Z" fill="#555a68" stroke="#cbc3be" stroke-width="2"/><path d="M-29 -7 H30 M-29 8 H30" stroke="#dbd4cc" stroke-width="2"/><rect x="-11" y="-19" width="31" height="26" rx="2" fill="#8c8f98" stroke="#eee6dc" stroke-width="1.5"/><path d="M-6 -15 L-6 3 M15 -15 L15 3" stroke="#4b5161" stroke-width="2"/><path d="M-5 -21 L5 -31 L15 -21" fill="none" stroke="#e2d6cc" stroke-width="3"/><circle cx="-29" cy="11" r="4" fill="#303746"/><circle cx="29" cy="11" r="4" fill="#303746"/></g>`;
  if (kind === 'periscope') head = `<g><rect x="-9" y="-36" width="18" height="44" rx="2" fill="#686e7a" stroke="#bfc0bf" stroke-width="1.5"/><path d="M-18 -39 L10 -39 L18 -32 L-11 -32 Z" fill="#a7a8ae" stroke="#e5ddd3"/><ellipse cx="-2" cy="-32" rx="12" ry="7" fill="url(#mirror)" stroke="#e9e4db" stroke-width="2"/><path d="M-18 -4 L10 -4 L18 3 L-11 3 Z" fill="#a7a8ae" stroke="#e5ddd3"/><ellipse cx="-2" cy="3" rx="12" ry="7" fill="url(#mirror)" stroke="#e9e4db" stroke-width="2"/><circle cx="13" cy="-17" r="4" fill="url(#metal)"/></g>`;
  if (kind === 'sample') {
    const secondLens = (part.lenses || []).length > 1 ? `<path d="M26 -17 V7" stroke="#b5b7bd" stroke-width="5"/><ellipse cx="26" cy="-15" rx="7" ry="15" fill="#83aab6" fill-opacity=".62" stroke="#e5e7df" stroke-width="2"/>` : '';
    head = `<g><path d="M-34 11 H34" stroke="#c4c0bc" stroke-width="6"/><path d="M-8 -17 V7" stroke="#b5b7bd" stroke-width="5"/><ellipse cx="-8" cy="-15" rx="7" ry="15" fill="#83aab6" fill-opacity=".62" stroke="#e5e7df" stroke-width="2"/>${secondLens}<rect x="8" y="-11" width="11" height="18" rx="1" fill="#d1a87b" stroke="#f4dfca" stroke-width="1.5"/><path d="M13 -16 V-11" stroke="#e4d6ca" stroke-width="2"/></g>`;
  }
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
  return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(1.1)">
    <ellipse cx="0" cy="3" rx="43" ry="10" fill="#231e37" opacity=".45"/>
    ${worktop}
    <path d="M-24 -68 L-3 -68 L-8 -37 L-17 -30 L-30 -33 Z M8 -68 L28 -68 L35 -32 L21 -28 L10 -38 Z" fill="#d8d2c9" stroke="#343249" stroke-width="2"/>
    <circle cx="-18" cy="-34" r="8" fill="#3a354e" stroke="#b5aaa8" stroke-width="2"/><circle cx="23" cy="-33" r="8" fill="#3a354e" stroke="#b5aaa8" stroke-width="2"/>
    <path d="M-29 -32 L-31 -4 L-4 -4 L-5 -12 L-13 -13 L-15 -31 Z M17 -31 L20 -13 L13 -11 L12 -4 L43 -4 L39 -31 Z" fill="#c8c6c0" stroke="#3a354e" stroke-width="2"/>
    <path d="M-32 -12 H-11 M20 -12 H40" stroke="#d77b81" stroke-width="3"/>
    <path d="M-28 -116 L28 -116 L33 -76 L22 -63 L-19 -63 L-31 -77 Z" fill="#34324c" stroke="#d6d0ca" stroke-width="2"/>
    ${arms}
    <path d="M-39 -121 L-16 -127 L-8 -111 L-29 -99 L-45 -105 Z M13 -111 L27 -127 L48 -121 L51 -105 L30 -99 Z" fill="#d77b81" stroke="#ede0d2" stroke-width="2"/>
    <path d="M-29 -112 L-3 -119 L8 -114 L30 -111 L24 -81 L6 -70 L-22 -82 Z" fill="#e2d8ca" stroke="#fff0dc" stroke-width="2"/>
    <path d="M-23 -105 L-3 -108 L-3 -86 L-18 -90 Z M9 -107 L25 -104 L19 -90 L9 -85 Z" fill="#b9adb4"/>
    <path d="M-6 -104 L5 -104 L10 -90 L0 -82 L-10 -90 Z" fill="#e9a659" stroke="#fff0d6" stroke-width="1.5"/>
    <path d="M-19 -71 L24 -71 L20 -62 L-17 -62 Z" fill="#a3a1aa" stroke="#343249" stroke-width="2"/>
    <g transform="translate(${bent ? 19 : 2} -150) rotate(${bent ? 20 : 0})">
      <path d="M-24 -16 L-13 -30 L8 -30 L23 -15 L23 10 L12 20 L-17 20 L-25 9 Z" fill="#e2d8ca" stroke="#39364d" stroke-width="2"/>
      <path d="M-22 -17 L-11 -27 L11 -27 L21 -17 L13 -12 L-14 -12 Z" fill="#c66e7d"/>
      <path d="M-20 -8 L18 -8 L17 8 L-18 8 Z" fill="#292a43"/>
      <path d="M-12 -1 H-3 M5 -1 H13" stroke="#f6b466" stroke-width="3"/>
      <path d="M-13 -30 L0 -39 L14 -30 M-1 -38 L-1 -49 L6 -39" fill="none" stroke="#eadfcf" stroke-width="3"/>
      <path d="M-20 11 L-13 20 H12 L19 11" fill="none" stroke="#b9abb1" stroke-width="2"/>
    </g>${prop}</g>`;
}
function sceneSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {}, action = contextFor(call);
  const target = /place|knob|move_stage|steer/.test(call.tool) ? parts.find(p => Object.values(call.args || {}).includes(p.id)) || parts[parts.length - 1] : parts.find(p => p.kind === 'sample');
  const dots = [];
  for (let x = 0; x <= 2400; x += 100) for (let z = 0; z <= 1200; z += 100) { const p = project({ x, z, h: 0 }); dots.push(`<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="1.1" fill="#809395" opacity=".56"/>`); }
  const lines = [['800nm', '#ed745b'], ['opa', '#6dc9d1']].map(([key, color]) => (beams[key]?.open ? (beams[key].segments || []).map(segment => `<path d="M${at(segment[0])} L${at(segment[1])}" stroke="${color}" stroke-width="6" opacity=".16"/><path d="M${at(segment[0])} L${at(segment[1])}" stroke="${color}" stroke-width="2.4" stroke-linecap="round"/>`).join('') : '')).join('');
  const table = `<path d="M${at({x:0,z:0})} L${at({x:2400,z:0})} L${at({x:2400,z:1200})} L${at({x:0,z:1200})} Z" fill="url(#table)" stroke="#c3c9bd" stroke-width="3"/><path d="M${at({x:0,z:1200})} L${at({x:2400,z:1200})} l0 22 L${at({x:0,z:1200})} Z" fill="#213b43" opacity=".6"/>${dots.join('')}`;
  return `<svg viewBox="0 0 1040 700" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Optical table with mounted components and a mecha working beside the table">
    <defs>
      <linearGradient id="posterSky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#df8794"/><stop offset=".53" stop-color="#9c698c"/><stop offset="1" stop-color="#3d355a"/></linearGradient>
      <linearGradient id="table" x2="1" y2="1"><stop stop-color="#77748c"/><stop offset="1" stop-color="#42415d"/></linearGradient>
      <linearGradient id="metal"><stop stop-color="#5a5b70"/><stop offset=".46" stop-color="#e4dfd5"/><stop offset="1" stop-color="#6b6b7b"/></linearGradient>
      <radialGradient id="mirror"><stop stop-color="#f4f4e9"/><stop offset=".55" stop-color="#abc1c0"/><stop offset="1" stop-color="#586477"/></radialGradient>
    </defs>
    <rect width="1040" height="700" fill="url(#posterSky)"/>
    <circle cx="813" cy="144" r="173" fill="#f6b094" opacity=".2"/>
    <g fill="#3d3558" opacity=".35"><path d="M89 513 V261 H99 V245 H107 V220 H116 V245 H124 V513 Z M168 514 V306 H177 V281 H185 V222 H193 V281 H201 V514 Z M825 511 V267 H833 V252 H842 V210 H850 V252 H860 V511 Z M919 515 V332 H927 V311 H936 V278 H943 V311 H951 V515 Z"/><path d="M55 495 Q300 465 520 491 T1010 485 V700 H55 Z"/></g>
    <text x="62" y="135" font-family="Avenir Next Condensed, Arial Narrow, Impact, sans-serif" font-size="55" font-weight="900" letter-spacing="3" fill="#fae7d6">FIND TIME ZERO</text>
    <ellipse cx="525" cy="520" rx="448" ry="92" fill="#29243f" opacity=".55"/>
    ${table}${lines}${housingSvg(2320,294,'800 nm','#cc6b5c')}${housingSvg(2320,935,'OPA','#6eafb6')}${parts.map(partSvg).join('')}${robotSvg(action.pose,target)}
  </svg>`;
}
function mapSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {};
  const sx = x => 12 + x / 2400 * 306, sz = z => 10 + z / 1200 * 150;
  const beam = [['800nm','#ed745b'],['opa','#6dc9d1']].map(([key,color]) => beams[key]?.open ? (beams[key].segments || []).map(seg => `<path d="M${sx(seg[0].x)},${sz(seg[0].z)} L${sx(seg[1].x)},${sz(seg[1].z)}" stroke="${color}" stroke-width="2.2" stroke-linecap="round"/>`).join('') : '').join('');
  return `<svg class="map-svg" viewBox="0 0 330 170" role="img" aria-label="Top down layout of the optical table"><rect x="12" y="10" width="306" height="150" rx="2" fill="#514663" stroke="#e5c9c4"/><path d="M88.5 10 V160 M165 10 V160 M241.5 10 V160 M12 47.5 H318 M12 85 H318 M12 122.5 H318" stroke="#b7a0b7" stroke-width=".6" opacity=".5"/>${beam}${parts.map(p=>`<g><circle cx="${sx(p.pos.x)}" cy="${sz(p.pos.z)}" r="4.5" fill="#efdfcf" stroke="#352b47" stroke-width="1.3"/><title>${esc(p.id)}</title></g>`).join('')}<rect x="299" y="29" width="19" height="35" fill="#dfd3cb"/><rect x="299" y="108" width="19" height="35" fill="#dfd3cb"/></svg>`;
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
