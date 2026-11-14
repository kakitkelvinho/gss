// Throwaway UI prototype. The viewer uses verifier-only snapshots from runs_bundle.js.
const runs = window.GSS_RUNS_BUNDLE?.runs.filter(run => run.trajectory?.length) ?? [];
const app = document.getElementById('app');
const state = { run: 3, step: Math.max(0, Number(new URLSearchParams(location.search).get('step') ?? 108)), playing: false, speed: 1, timer: null, menu: null, railOpen: new URLSearchParams(location.search).get('rail') !== 'closed', expanded: new Set(), selectedPart: null };

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
  const base = `<ellipse cx="0" cy="${tableY.toFixed(1)}" rx="17" ry="6" fill="#172630" stroke="#c7d0cb" stroke-width="1.5"/>
    <path d="M-4 10 V${(tableY - 2).toFixed(1)} H4 V10 Z" fill="#27353e" stroke="#aab9bc" stroke-width="1"/>
    <ellipse cx="0" cy="${(tableY - 2).toFixed(1)}" rx="7" ry="3" fill="#34464e"/>
    <rect x="-8" y="6" width="16" height="8" fill="#25343c" stroke="#aebfc1" stroke-width="1"/>`;
  let head = '';
  if (kind === 'mirror') head = `<g transform="rotate(${(part.yaw_deg || 0) * .35})">
    <path d="M-17 -15 L10 -16 L17 -10 V13 L-17 14 Z" fill="#293842" stroke="#d5dcd8" stroke-width="1.5"/>
    <circle cx="-2" cy="-1" r="12" fill="#d5e5e4" stroke="#eef0e8" stroke-width="2.5"/>
    <path d="M-9 -7 Q-2 -11 5 -7" stroke="#ffffff" stroke-width="1.5" fill="none"/>
    <path d="M17 -11 H24 M17 10 H24" stroke="#b9c8c9" stroke-width="3"/>
    <circle cx="25" cy="-11" r="3" fill="#e8ede8" stroke="#26343c"/><circle cx="25" cy="10" r="3" fill="#e8ede8" stroke="#26343c"/>
  </g>`;
  if (kind === 'stage') head = `<g>
    <path d="M-33 8 L32 8 L39 15 L-26 15 Z" fill="#1e2e38" stroke="#c4ceca" stroke-width="1.5"/>
    <path d="M-35 -10 L28 -10 L35 -4 L-28 -4 Z" fill="#c9d3d0" stroke="#f3f3e9" stroke-width="1.5"/>
    <path d="M-28 -4 H35 V8 H-28 Z" fill="#34454e" stroke="#c4ceca" stroke-width="1.5"/>
    <path d="M-22 1 H29 M-22 5 H29" stroke="#94a8ac" stroke-width="1"/>
    <circle cx="-35" cy="4" r="5" fill="#d6ddda" stroke="#33424b" stroke-width="2"/>
    <rect x="-8" y="-20" width="20" height="21" fill="#303f48" stroke="#d9e0dc" stroke-width="1.5"/>
    <circle cx="2" cy="-9" r="6" fill="#dce8e5" stroke="#778d92" stroke-width="2"/>
  </g>`;
  if (kind === 'periscope') head = `<g>
    <rect x="-8" y="-35" width="16" height="42" fill="#283941" stroke="#c9d4d2" stroke-width="1.5"/>
    <path d="M-13 -38 L4 -38 L13 -32 L-4 -32 Z" fill="#e6eae3" stroke="#f8f8ef" stroke-width="1.5"/>
    <ellipse cx="-2" cy="-31" rx="11" ry="7" fill="#d4e5e4" stroke="#eff2eb" stroke-width="2"/>
    <ellipse cx="-2" cy="3" rx="11" ry="7" fill="#d4e5e4" stroke="#eff2eb" stroke-width="2"/>
    <path d="M9 -17 H17" stroke="#b9c6c6" stroke-width="3"/><circle cx="18" cy="-17" r="3" fill="#e9ede7" stroke="#293841"/>
  </g>`;
  if (kind === 'sample') {
    const secondLens = (part.lenses || []).length > 1 ? `<path d="M26 -17 V7" stroke="#b7c6c6" stroke-width="5"/><ellipse cx="26" cy="-15" rx="7" ry="15" fill="#afdbdd" stroke="#e8f3ef" stroke-width="2"/>` : '';
    head = `<g><path d="M-34 11 H34" stroke="#d4dcda" stroke-width="5"/><path d="M-8 -17 V7" stroke="#c3d1d0" stroke-width="5"/><ellipse cx="-8" cy="-15" rx="7" ry="15" fill="#afdbdd" stroke="#f2f5ed" stroke-width="2"/>${secondLens}<rect x="8" y="-11" width="11" height="18" fill="#d6ad70" stroke="#f2e4ce" stroke-width="2"/></g>`;
  }
  return `<g transform="translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})" aria-label="${id} ${kind}">${base}${head}<title>${id}</title></g>`;
}
function housingSvg(port, label, color) {
  const pos = port?.pos || { x: 2250, z: label === 'OPA' ? 935 : 294, h: label === 'OPA' ? 158 : 120 };
  const p = project(pos), tableY = project({ x: pos.x, z: pos.z, h: 0 }).y - p.y;
  return `<g transform="translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})">
    <path d="M-8 -27 L38 -50 L119 -22 L73 1 Z" fill="#f2f1e9" stroke="#ffffff" stroke-width="1.5"/>
    <path d="M-8 -27 L73 1 V27 L-8 -1 Z" fill="#c6cbca" stroke="#e8ece9" stroke-width="1.5"/>
    <path d="M73 1 L119 -22 V4 L73 27 Z" fill="#89969b" stroke="#d7dedb" stroke-width="1.5"/>
    <path d="M16 8 V${tableY.toFixed(1)} M73 27 V${(tableY + 5).toFixed(1)}" stroke="#293940" stroke-width="8"/>
    <ellipse cx="16" cy="${tableY.toFixed(1)}" rx="16" ry="5" fill="#1b2b33"/><ellipse cx="73" cy="${(tableY + 5).toFixed(1)}" rx="16" ry="5" fill="#1b2b33"/>
    <circle r="8" fill="${color}" stroke="#f3efea" stroke-width="2"/><circle r="3" fill="#f1efe8"/>
    <text class="label tag" x="64" y="-25" text-anchor="middle">${label}</text>
  </g>`;
}
function mannequinSvg(pose, targetPart) {
  const x = pose === 'manual' || pose === 'buy' ? 180 : Math.max(370, Math.min(720, project(targetPart?.pos || { x: 1200, z: 600 }).x));
  const y = Math.min(655, Math.max(550, 445 + .28 * x));
  const ink = '#e4e2d9';
  const desk = ['manual', 'buy', 'measure'].includes(pose)
    ? `<g><path d="M48 -67 L121 -91 L174 -73 L100 -47 Z" fill="#56717b" stroke="${ink}" stroke-width="3"/><path d="M48 -67 L100 -47 L100 -40 L48 -59 Z" fill="#22363f"/><path d="M100 -47 L174 -73 L174 -66 L100 -40 Z" fill="#1b303a"/><path d="M66 -53 V4 M151 -67 V3" stroke="${ink}" stroke-width="6"/></g>` : '';
  const book = pose === 'manual' ? `<g transform="translate(110,-66)"><path d="M-33 0 L0 -12 L34 0 L0 10 Z" fill="#263b44" stroke="${ink}" stroke-width="2"/><path d="M0 -12 V10 M-24 -1 L-7 -6 M7 -5 L25 -1" stroke="${ink}" stroke-width="1.5"/></g>` : '';
  const buying = pose === 'buy' ? `<g transform="translate(106,-75)"><rect x="-24" y="-17" width="48" height="30" fill="${ink}"/><text x="0" y="6" text-anchor="middle" fill="#ec8135" font-size="21">€</text></g><g transform="translate(22,-184)"><path d="M-19 -22 H19 V21 H-19 Z" fill="#ed8232"/><text x="0" y="10" text-anchor="middle" fill="${ink}" font-size="30">€</text></g>` : '';
  const measuring = pose === 'measure' ? `<g transform="translate(108,-77)"><rect x="-26" y="-22" width="52" height="37" fill="${ink}"/><path d="M-20 0 L-9 -5 L0 2 L11 -13 L20 -7" fill="none" stroke="#263b44" stroke-width="2"/></g>` : '';
  const arm = pose === 'manual'
    ? `<path d="M-24 -109 L20 -89 M24 -86 L78 -77 M27 -110 L62 -79 M67 -75 L97 -68" stroke="${ink}" stroke-width="14" fill="none" stroke-linecap="square"/>`
    : pose === 'adjust'
      ? `<path d="M-24 -112 L17 -122 M21 -124 L51 -151 M27 -111 L60 -123 M64 -125 L88 -143" stroke="${ink}" stroke-width="14" fill="none" stroke-linecap="square"/>`
      : `<path d="M-24 -111 L-33 -74 M-31 -69 L-15 -58 M26 -110 L58 -78 M62 -76 L93 -84" stroke="${ink}" stroke-width="14" fill="none" stroke-linecap="square"/>`;
  return `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) scale(1.08)">
    <ellipse cx="0" cy="5" rx="49" ry="8" fill="${ink}" opacity=".18"/>
    ${desk}
    <path d="M-22 -64 L-4 -64 L-9 -37 L-28 -35 Z M8 -64 L27 -64 L36 -35 L17 -34 Z" fill="${ink}"/>
    <path d="M-28 -30 L-10 -30 L-13 -5 L-33 -5 Z M18 -29 L37 -29 L43 -5 L22 -5 Z" fill="${ink}"/>
    <path d="M-34 -5 L-11 -5 L-9 1 L-40 1 Z M20 -5 L45 -5 L50 1 L19 1 Z" fill="${ink}"/>
    ${arm}
    <path d="M-29 -121 L21 -126 L36 -102 L27 -66 L-24 -64 L-35 -99 Z" fill="${ink}"/>
    <path d="M-29 -80 L23 -80" stroke="#263b44" stroke-width="3" opacity=".65"/>
    <g transform="translate(${pose === 'manual' || pose === 'adjust' ? 18 : 2} -150) rotate(${pose === 'manual' || pose === 'adjust' ? 18 : 0})">
      <path d="M-17 -22 L10 -25 L22 -12 L17 13 L-13 18 L-23 5 L-24 -11 Z" fill="${ink}"/>
    </g>
    ${book}${buying}${measuring}
  </g>`;
}
function actionCoordinates(call) {
  const args = call.args || {}, parts = call.snapshot?.parts || [];
  if (state.selectedPart) { const selected = parts.find(part => part.id === state.selectedPart); if (selected) return selected.pos; }
  if (Number.isFinite(args.x) && Number.isFinite(args.z)) return { x: args.x, z: args.z };
  const referenced = parts.find(part => part.id === args.part || part.id === args.mirror);
  if (referenced) return referenced.pos;
  if (args.plane === 'sample') return parts.find(part => part.kind === 'sample')?.pos || null;
  return null;
}
function sceneSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {}, action = contextFor(call);
  const target = /place|knob|move_stage|steer/.test(call.tool) ? parts.find(p => Object.values(call.args || {}).includes(p.id)) || parts[parts.length - 1] : parts.find(p => p.kind === 'sample');
  const lines = [['800nm', '#ff626f'], ['opa', '#ae9eff']].map(([key, color]) => (beams[key]?.open ? (beams[key].segments || []).map(segment => `<path d="M${at(segment[0])} L${at(segment[1])}" stroke="${color}" stroke-width="7" opacity=".22"/><path d="M${at(segment[0])} L${at(segment[1])}" stroke="${color}" stroke-width="2.8" stroke-linecap="round"/>`).join('') : '')).join('');
  const top = [{x:0,z:0,h:0},{x:2400,z:0,h:0},{x:2400,z:1200,h:0},{x:0,z:1200,h:0}];
  const below = top.map(point => ({...point,h:-40}));
  const table = `<path d="M${at(top[3])} L${at(top[2])} L${at(below[2])} L${at(below[3])} Z" fill="#4a626b" stroke="#172830" stroke-width="1.5"/><path d="M${at(top[1])} L${at(top[2])} L${at(below[2])} L${at(below[1])} Z" fill="#38525d" stroke="#172830" stroke-width="1.5"/><g transform="matrix(.246 .070 -.204 .140 347.2 167)"><rect width="2400" height="1200" fill="#8098a0"/><rect width="2400" height="1200" fill="url(#breadboardHoles)"/></g><path d="M${top.map(at).join(' L')} Z" fill="none" stroke="#e1e9e6" stroke-width="2"/>`;
  const targetPosition = actionCoordinates(call);
  const coordinate = targetPosition ? (() => {
    const q = project({ x: targetPosition.x, z: targetPosition.z, h: 0 });
    const left = q.x > 750, boxX = left ? -150 : 18;
    return `<g transform="translate(${q.x.toFixed(1)} ${q.y.toFixed(1)})"><circle r="13" fill="none" stroke="#ee8134" stroke-width="2"/><path d="M-20 0 H20 M0 -20 V20" stroke="#ee8134" stroke-width="1.5"/><rect x="${boxX}" y="-29" width="132" height="20" fill="#073a49"/><text x="${boxX + 6}" y="-15" fill="#f1e9dc" font-family="Avenir Next, Arial" font-size="10">x ${Math.round(targetPosition.x)} · z ${Math.round(targetPosition.z)} mm</text></g>`;
  })() : '';
  return `<svg viewBox="0 0 1040 700" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Optical table and a cut-paper mannequin working beside it">
    <defs><pattern id="breadboardHoles" width="25" height="25" patternUnits="userSpaceOnUse"><circle cx="12.5" cy="12.5" r="3.5" fill="#304650"/><circle cx="11.5" cy="11.5" r="1.2" fill="#b8c9c9"/></pattern></defs>
    <rect width="1040" height="700" fill="#181b1c"/>
    <ellipse cx="525" cy="420" rx="480" ry="286" fill="#2b3335" opacity=".65"/>
    <ellipse cx="525" cy="526" rx="445" ry="86" fill="#080c0d" opacity=".6"/>
    ${table}<text x="347" y="156" font-family="Avenir Next, Arial" font-size="10" fill="#d7e8e4">0</text><text x="77" y="346" font-family="Avenir Next, Arial" font-size="10" fill="#d7e8e4">z 1200 mm</text><text x="705" y="519" font-family="Avenir Next, Arial" font-size="10" fill="#d7e8e4">x 2400 mm</text>${lines}${housingSvg(currentRun()?.meta?.ports?.['800nm'], '800 nm', '#c7777c')}${housingSvg(currentRun()?.meta?.ports?.opa, 'OPA', '#9c95c7')}${parts.map(partSvg).join('')}${coordinate}${mannequinSvg(action.pose,target)}
  </svg>`;
}
function mapSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {};
  const sx = x => 15 + x / 2400 * 300, sz = z => 10 + z / 1200 * 150;
  const beam = [['800nm','#ff626f'],['opa','#ae9eff']].map(([key,color]) => beams[key]?.open ? (beams[key].segments || []).map(seg => `<path d="M${sx(seg[0].x)},${sz(seg[0].z)} L${sx(seg[1].x)},${sz(seg[1].z)}" stroke="${color}" stroke-width="2.2" stroke-linecap="round"/>`).join('') : '').join('');
  return `<svg class="map-svg" viewBox="0 0 330 170" role="img" aria-label="Top down layout of the optical table"><rect x="15" y="10" width="300" height="150" fill="#8098a0" stroke="#e1e9e6"/><path d="M90 10 V160 M165 10 V160 M240 10 V160 M15 47.5 H315 M15 85 H315 M15 122.5 H315" stroke="#aec2c4" stroke-width=".6" opacity=".6"/>${beam}${parts.map(p=>`<g><circle cx="${sx(p.pos.x)}" cy="${sz(p.pos.z)}" r="4.5" fill="#e8e9df" stroke="#10252b" stroke-width="1.3"/><title>${esc(p.id)}</title></g>`).join('')}<rect x="296" y="29" width="19" height="35" fill="#e8e9df"/><rect x="296" y="108" width="19" height="35" fill="#e8e9df"/></svg>`;
}
function scoreSvg(run, step) {
  const trajectory = run.trajectory, end = Math.max(1, step), values = trajectory.slice(0, end + 1).map(t => Math.max(0, Math.min(1, Number(t.truth?.reward || 0))));
  const path = values.map((v, i) => `${i ? 'L' : 'M'}${(i / Math.max(end, 1) * 270).toFixed(1)},${(32 - v * 29).toFixed(1)}`).join(' ');
  return `<svg class="graph" viewBox="0 0 270 34" preserveAspectRatio="none" aria-label="Score history"><path d="M0 32 H270" stroke="var(--line)"/><path d="${path}" fill="none" stroke="#8dbec3" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>`;
}
function runName(run, index) { return `Run ${index + 1} · L${run.meta.level} · ${run.meta.opa_lambda_nm} nm`; }
function groupCalls(trajectory) {
  const groups = []; let setup = null;
  trajectory.forEach((call, index) => {
    let phase;
    if (call.tool === 'place') { setup = `Set up ${call.args?.part || 'optic'}`; phase = setup; }
    else if (/read_manual|get_datasheet|list_catalogue/.test(call.tool)) { setup = null; phase = 'Read manuals'; }
    else if (call.tool === 'buy') { setup = null; phase = 'Purchase parts'; }
    else if (/scan|move_stage|measure_path|read_signal/.test(call.tool)) { setup = null; phase = 'Timing and signals'; }
    else if (call.tool === 'submit') { setup = null; phase = 'Submit'; }
    else if (call.tool === 'status') phase = setup || groups.at(-1)?.phase || 'Status';
    else phase = setup || 'Alignment checks';
    const last = groups.at(-1);
    if (last?.phase === phase && call.tool !== 'place') last.end = index;
    else groups.push({ phase, start: index, end: index });
  });
  return groups;
}
function stepsMarkup(trajectory) {
  return groupCalls(trajectory).map(group => {
    const active = state.step >= group.start && state.step <= group.end;
    const count = group.end - group.start + 1, open = state.expanded.has(group.start);
    const heading = `<button class="phase-row ${active ? 'active' : ''}" ${count === 1 ? `data-step="${group.start}"` : `data-group="${group.start}" aria-expanded="${open}"`}><span class="phase-name">${esc(group.phase)}</span><span class="phase-count">${count > 1 ? `${count} calls` : String(group.start + 1).padStart(3, '0')}</span><span class="phase-arrow">${count > 1 ? open ? '⌄' : '›' : ''}</span></button>`;
    if (!open || count === 1) return heading;
    const calls = trajectory.slice(group.start, group.end + 1).map((call, offset) => {
      const index = group.start + offset;
      return `<button class="call-row child ${index === state.step ? 'active' : ''}" data-step="${index}" aria-current="${index === state.step ? 'step' : 'false'}"><span class="number">${String(index + 1).padStart(3, '0')}</span><span class="summary">${esc(cleanTool(call.tool))}${Object.keys(call.args || {}).length ? ` · ${esc(shortArgs(call.args))}` : ''}</span><span class="mark">${call.result?.error ? '!' : index === state.step ? '●' : ''}</span></button>`;
    }).join('');
    return heading + calls;
  }).join('');
}
function menuMarkup(call) {
  if (state.menu === 'run') return `<div class="flyout run-flyout" role="menu" aria-label="Run"><div class="flyout-title">Run</div>${runs.map((run, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}" data-run="${i}"><span class="mini-icon">${i === state.run ? '●' : '○'}</span><span>${esc(runName(run, i))}</span></button>`).join('')}</div>`;
  if (state.menu === 'speed') return `<div class="flyout speed-flyout" role="menu" aria-label="Speed"><div class="flyout-title">Speed</div>${[1, 2, 4].map((speed, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}" data-speed="${speed}"><span class="mini-icon">${speed === state.speed ? '●' : '○'}</span><span>${speed}×</span></button>`).join('')}</div>`;
  if (state.menu === 'parts') {
    const parts = call.snapshot?.parts || [];
    return `<div class="flyout parts-flyout" role="menu" aria-label="Parts"><div class="flyout-title">Parts · ${parts.length}</div>${parts.map((part, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}" data-part="${esc(part.id)}"><span class="mini-icon">${part.id === state.selectedPart ? '●' : part.kind === 'mirror' ? '◉' : part.kind === 'stage' ? '▤' : '◇'}</span><span>${esc(part.id)}</span></button>`).join('')}</div>`;
  }
  if (state.menu === 'view') return `<div class="flyout view-flyout" role="menu" aria-label="View"><div class="flyout-title">Top view</div><button class="flyout-item" role="menuitem" tabindex="0" data-action="close-menu"><span class="mini-icon">▣</span><span>Isometric view</span></button>${mapSvg(call)}</div>`;
  return '';
}
function render() {
  const run = currentRun(), call = currentCall(); if (!run || !call) { app.textContent = 'No run snapshots found.'; return; }
  const trajectory = run.trajectory, score = Number(call.truth?.reward || 0);
  app.innerHTML = `<main class="app ${state.railOpen ? '' : 'rail-closed'}">
    <section class="scene-shell"><div class="scene">${sceneSvg(call)}</div></section>
    <div class="player" aria-label="Playback">
      <button class="run-trigger" data-action="run" aria-label="Choose run" aria-expanded="${state.menu === 'run'}" aria-haspopup="menu">▤</button><span class="run-label">${esc(runName(run, state.run))}</span>
      <button data-action="prev" aria-label="Previous step" title="← or ,">‹</button><button data-action="play" aria-label="${state.playing ? 'Pause' : 'Play'}" aria-pressed="${state.playing}" title="Space">${state.playing ? 'Ⅱ' : '▶'}</button><button data-action="next" aria-label="Next step" title="→ or .">›</button>
      <input class="scrub" type="range" min="0" max="${trajectory.length-1}" value="${state.step}" aria-label="Scrub steps"><span class="counter">${state.step+1}/${trajectory.length}</span><button data-action="speed" aria-label="Playback speed" aria-expanded="${state.menu === 'speed'}" aria-haspopup="menu">${state.speed}×</button>
    </div>
    <aside class="sidebar"><section class="call-panel"><div class="panel-heading">Steps <small>${trajectory.length} calls</small></div><div class="current-call">${state.step + 1}/${trajectory.length} · ${esc(cleanTool(call.tool))}${Object.keys(call.args || {}).length ? ` · ${esc(shortArgs(call.args))}` : ''}</div><div class="call-stack">${stepsMarkup(trajectory)}</div></section>
      <section class="score-panel"><div class="totals"><div><span>Money</span><strong>${money(call.snapshot?.cost_eur)}</strong></div><div><span>Lab time</span><strong>${fmtTime(call.t_s)}</strong></div></div><div class="score-secondary"><span>Score · private replay</span><strong>${score.toFixed(3)}</strong></div>${scoreSvg(run,state.step)}</section></aside>
    <button class="rail-toggle" data-action="rail" aria-label="${state.railOpen ? 'Hide steps' : 'Show steps'}" title="${state.railOpen ? 'Hide steps' : 'Show steps'}">${state.railOpen ? '‹' : '›'}</button>
    <button class="corner-button parts-trigger" data-action="parts" aria-label="Parts" aria-expanded="${state.menu === 'parts'}" aria-haspopup="menu">≡</button><span class="hint">Parts</span>
    <button class="corner-button view-trigger" data-action="view" aria-label="View" aria-expanded="${state.menu === 'view'}" aria-haspopup="menu">▣</button><span class="view-hint">View</span>
    <div class="shortcut-hints">Space play · ← → / , . step</div>${menuMarkup(call)}</main>`;
  const active = app.querySelector('.phase-row.active'); active?.scrollIntoView({ block: 'nearest' });
}
function changeStep(next) { const max = currentRun().trajectory.length - 1; state.step = Math.max(0, Math.min(max, next)); state.selectedPart = null; if (state.step === max && state.playing) stop(); render(); }
function stop() { state.playing = false; clearInterval(state.timer); state.timer = null; }
function togglePlay() { if (state.playing) { stop(); render(); return; } if (state.step >= currentRun().trajectory.length - 1) state.step = 0; state.playing = true; state.timer = setInterval(() => changeStep(state.step + 1), 720 / state.speed); render(); }
function setMenu(menu) { state.menu = state.menu === menu ? null : menu; render(); if (state.menu) app.querySelector('.flyout-item')?.focus(); else app.querySelector(`[data-action="${menu}"]`)?.focus(); }
app.addEventListener('click', e => {
  const button = e.target.closest('button'); if (!button) return;
  if (button.dataset.step !== undefined) { changeStep(Number(button.dataset.step)); return; }
  if (button.dataset.group !== undefined) { const id = Number(button.dataset.group); state.expanded.has(id) ? state.expanded.delete(id) : state.expanded.add(id); render(); app.querySelector(`[data-group="${id}"]`)?.focus(); return; }
  if (button.dataset.part !== undefined) { state.selectedPart = button.dataset.part; state.menu = null; render(); return; }
  if (button.dataset.run !== undefined) { stop(); state.run = Number(button.dataset.run); state.step = currentRun().trajectory.length - 2; state.selectedPart = null; state.expanded.clear(); state.menu = null; render(); return; }
  if (button.dataset.speed !== undefined) { const wasPlaying = state.playing; stop(); state.speed = Number(button.dataset.speed); state.menu = null; wasPlaying ? togglePlay() : render(); return; }
  switch (button.dataset.action) {
    case 'prev': changeStep(state.step - 1); break;
    case 'play': togglePlay(); break;
    case 'next': changeStep(state.step + 1); break;
    case 'run': setMenu('run'); break;
    case 'speed': setMenu('speed'); break;
    case 'parts': setMenu('parts'); break;
    case 'view': setMenu('view'); break;
    case 'rail': state.railOpen = !state.railOpen; state.menu = null; render(); break;
    case 'close-menu': setMenu(state.menu); break;
  }
});
app.addEventListener('change', e => { if (e.target.matches('input[type=range]')) changeStep(Number(e.target.value)); });
document.addEventListener('pointerdown', e => { if (state.menu && !e.target.closest('.flyout,[aria-haspopup="menu"]')) { const menu = state.menu; state.menu = null; render(); app.querySelector(`[data-action="${menu}"]`)?.focus(); } });
document.addEventListener('keydown', e => {
  if (state.menu && e.key === 'Escape') { e.preventDefault(); setMenu(state.menu); return; }
  const items = [...app.querySelectorAll('.flyout-item')];
  if (state.menu && items.length && ['ArrowDown','ArrowUp','ArrowLeft','ArrowRight','Home','End'].includes(e.key)) {
    e.preventDefault(); const current = items.indexOf(document.activeElement);
    const next = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : (current + (e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : -1) + items.length) % items.length;
    items.forEach((item, i) => item.tabIndex = i === next ? 0 : -1); items[next].focus(); return;
  }
  if (state.menu && (e.key === ' ' || e.key === 'Enter')) return;
  if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable) return;
  if (e.key === 'Escape') { state.menu = null; render(); return; }
  if (e.key === 'ArrowLeft' || e.key === ',') changeStep(state.step - 1);
  if (e.key === 'ArrowRight' || e.key === '.') changeStep(state.step + 1);
  if (e.key === ' ') { e.preventDefault(); togglePlay(); }
});
render();
