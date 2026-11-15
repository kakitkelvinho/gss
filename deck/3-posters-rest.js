// v6 = v5 with slides 3-10 as screen-print posters too; backups restyled to match.
const fs = require('fs');
const IN = __dirname + '/out/pitch-deck-v5.html', OUT = __dirname + '/out/pitch-deck-v6.html';
let html = fs.readFileSync(IN, 'utf8');
const scans = JSON.parse(fs.readFileSync(__dirname + '/scans.json', 'utf8')).scans;
const f1 = x => Math.round(x * 10) / 10;
let SEED = 21; const rnd = () => (SEED = (SEED * 16807) % 2147483647) / 2147483647;
const BLUE = '#2E6F9E', BLUE2 = '#4A8FC4', ORANGE = '#E8742A', CREAM = '#EDE3CC', INK = '#16120F';

// ---- move poster filters to the global defs (unique ids), drop per-svg copies ----
const filters = `
  <filter id="pcut" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="7"/></filter>
  <filter id="pcutS" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>
  <filter id="pgrain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="9"/>
    <feColorMatrix type="matrix" values="0 0 0 0 .08  0 0 0 0 .06  0 0 0 0 .05  0 0 0 -1.6 1.05"/></filter>
  <filter id="pwear" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="3" seed="2"/>
    <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 .97  0 0 0 0 .9  0 0 0 -2.2 1.25"/></filter>`;
html = html.replace(/\s*<filter id="cut"[\s\S]*?<filter id="wear"[\s\S]*?<\/filter>/g, '')
  .replace(/url\(#cut\)/g, 'url(#pcut)').replace(/url\(#grain\)/g, 'url(#pgrain)').replace(/url\(#wear\)/g, 'url(#pwear)')
  .replace('<filter id="blur"', filters + '\n  <filter id="blur"');
const texture = (op = .45) => `<rect width="1920" height="1080" filter="url(#pgrain)" opacity="${op}"/><rect width="1920" height="1080" filter="url(#pwear)" opacity=".1"/>`;

// ---- type helpers ----
const est = (s, size) => [...s].reduce((a, c) => a + (c === ' ' ? .2 : /[.,:’'!]/.test(c) ? .17 : .4), 0) * size;
const title = (lines, size, y0, gap, cols, x = 110) => lines.map((t, i) => {
  const w = Math.min(1700, est(t, size));
  return `<text x="${x}" y="${y0 + i * gap}" class="pt-big" style="font-size:${size}px;fill:${cols[i] || cols[0]}" textLength="${f1(w)}" lengthAdjust="spacingAndGlyphs">${t}</text>`;
}).join('');
const small = (lines, col, y0 = 110, size = 32, x = 110) => lines.map((t, i) => `<text x="${x}" y="${y0 + i * (size + 6)}" class="pt-sm" style="font-size:${size}px;fill:${col}">${t}</text>`).join('');
const poster = (bg, body, label, notes, cls = '') => `  <section class="slide poster ${cls}" data-video>
    <svg class="poster-art" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="1920" height="1080" fill="${bg}"/>${body}${texture()}
    </svg>
    <h2 class="sr">${label}</h2>
    <aside class="notes">${notes}</aside>
  </section>
`;

// ---- black bust silhouette with an orange visor ----
const G = {
  happy: `<path d="M86 74 Q96 60 106 74 M114 74 Q124 60 134 74" stroke="${INK}" stroke-width="6" fill="none"/>`,
  smug: `<path d="M82 64 H104 M116 64 H138" stroke="${INK}" stroke-width="6"/><path d="M100 76 Q120 84 138 72" stroke="${INK}" stroke-width="5" fill="none"/>`,
  squint: `<path d="M82 68 H104 M116 68 H138" stroke="${INK}" stroke-width="4"/>`,
  sleep: `<path d="M84 64 Q94 74 104 64 M116 64 Q126 74 136 64" stroke="${INK}" stroke-width="5" fill="none"/>`,
  worried: `<circle cx="94" cy="70" r="6" fill="${INK}"/><circle cx="126" cy="70" r="6" fill="${INK}"/><path d="M82 58 L102 54 M138 58 L118 54" stroke="${INK}" stroke-width="4"/>`,
};
const bust = (x, y, s, mood) => `<g transform="translate(${x},${y}) scale(${s})">
  <path d="M8 240 L28 166 L80 148 L140 148 L192 166 L212 240 Z" fill="${INK}"/>
  <rect x="96" y="112" width="28" height="40" fill="${INK}"/>
  <path d="M58 118 L52 38 L80 14 L140 14 L168 38 L162 118 Z" fill="${INK}"/>
  <rect x="68" y="46" width="84" height="38" fill="${ORANGE}"/>${G[mood]}
  <circle cx="110" cy="196" r="14" fill="${CREAM}"/>
  <path d="M110 14 V-6" stroke="${INK}" stroke-width="6"/><rect x="103" y="-16" width="14" height="14" fill="${ORANGE}"/></g>`;

// ===== slide 3: two pulses =====
const p3 = poster(INK, `
  <g filter="url(#pcut)">
    <polygon points="1000,400 -60,690 -60,930" fill="${ORANGE}" opacity=".9"/>
    <polygon points="1000,400 1980,610 1980,860" fill="${BLUE2}" opacity=".9"/>
    <path d="M1180 150 L1220 122 L1220 612 L1180 640 Z" fill="#9C927E"/>
    <path d="M820 150 L860 122 L1220 122 L1180 150 Z" fill="#F7F0DF"/>
    <rect x="820" y="150" width="360" height="490" fill="${CREAM}"/>
    <rect x="982" y="640" width="36" height="84" fill="${CREAM}"/><rect x="900" y="716" width="200" height="22" fill="${CREAM}"/>
    <path class="hit" d="M1000 300 L1020 380 L1100 400 L1020 420 L1000 500 L980 420 L900 400 L980 380 Z" fill="${ORANGE}"/>
    <circle cx="1000" cy="400" r="16" fill="${INK}"/>
  </g>
  <circle class="pp-o" cx="60" cy="800" r="60" fill="${ORANGE}" stroke="${CREAM}" stroke-width="6"/>
  <circle class="pp-b" cx="1860" cy="740" r="60" fill="${BLUE2}" stroke="${CREAM}" stroke-width="6"/>
  <g filter="url(#pcut)">
    ${small(['≤ 4 hours simulated lab time', '≤ €30,000 parts budget'], CREAM, 110, 40)}
    ${title(['MAKE TWO LASER PULSES ARRIVE', 'AT THE SAME SPOT AND TIME.'], 140, 905, 135, [CREAM, ORANGE])}
  </g>`, 'Make two laser pulses arrive at the same spot and time.',
  '<b>~12 s.</b> An 800 nm pulse and an OPA pulse start on opposite sides of an empty optical table. The agent has to build both beam paths so they focus on the same spot of the sample and arrive within about 100 femtoseconds of each other.', 'p-pulses');

// ===== slide 4: MCP mind map =====
const ic = {
  read: `<path d="M-52 -26 L0 -18 L0 34 L-52 26 Z" fill="${CREAM}"/><path d="M52 -26 L0 -18 L0 34 L52 26 Z" fill="${CREAM}"/><rect x="-3" y="-20" width="6" height="56" fill="${INK}"/>
         <path d="M-42 -10 L-10 -6 M-42 4 L-10 8 M10 -6 L42 -10 M10 8 L42 4" stroke="${BLUE}" stroke-width="4"/>`,
  buy: `<path d="M-64 -40 L-46 -40 L-36 -22 L46 -22 L32 18 L-26 18 Z" fill="${ORANGE}"/><path d="M-26 18 L-32 30 L36 30" stroke="${INK}" stroke-width="7" fill="none"/>
        <circle cx="-20" cy="40" r="9" fill="${INK}"/><circle cx="24" cy="40" r="9" fill="${INK}"/><rect x="-8" y="-46" width="24" height="24" fill="${CREAM}"/>`,
  build: `<rect x="-40" y="-40" width="80" height="80" fill="${INK}"/><circle r="25" fill="${CREAM}"/><circle cx="42" cy="-32" r="11" fill="${ORANGE}"/><circle cx="-32" cy="42" r="11" fill="${ORANGE}"/>`,
  look: `<rect x="-84" y="-6" width="44" height="12" fill="${INK}"/><rect x="-40" y="-32" width="86" height="64" fill="${ORANGE}"/><circle cx="2" r="14" fill="${CREAM}"/>
         <path d="M2 -40 V-54 M28 -36 L38 -48 M-24 -36 L-34 -48" stroke="${CREAM}" stroke-width="5"/>`,
  tzero: `<path d="M-58 18 L-26 18 L-12 -6 L-2 -44 L8 -6 L22 18 L58 18" stroke="${INK}" stroke-width="8" fill="none" stroke-linejoin="miter"/>
          <rect x="-58" y="34" width="116" height="10" fill="${CREAM}"/><rect x="-16" y="26" width="32" height="26" fill="${ORANGE}"/>`,
  submit: `<rect x="-48" y="14" width="96" height="26" fill="${INK}"/><path d="M-34 14 Q-34 -32 0 -32 Q34 -32 34 14 Z" fill="${ORANGE}"/>`,
};
const C = [800, 345];
const nodes = [
  { k: 'read', t: 'READ', tools: ['read_manual', 'get_datasheet', 'list_catalogue · status'], x: 450, y: 140, side: 'L' },
  { k: 'buy', t: 'BUY', tools: ['buy'], x: 800, y: 92, side: 'R' },
  { k: 'build', t: 'BUILD', tools: ['place · rotate · move', 'remove · knob · install'], x: 1150, y: 140, side: 'R' },
  { k: 'look', t: 'LOOK', tools: ['ir_card · view_camera', 'measure_path · block'], x: 1150, y: 470, side: 'R' },
  { k: 'tzero', t: 'SCAN', tools: ['move_stage · scan', 'read_signal'], x: 800, y: 590, side: 'R' },
  { k: 'submit', t: 'SUBMIT', tools: ['submit'], x: 450, y: 470, side: 'L' },
];
const p4 = poster(CREAM, `
  <g transform="translate(160,175) scale(.9)">
    <g filter="url(#pcut)">
      ${nodes.map(n => `<path d="M${C[0]} ${C[1]} L${n.x} ${n.y}" stroke="${INK}" stroke-width="9"/>`).join('')}
      ${nodes.map((n, i) => `<g class="mm-node" style="--d:${0.2 + i * 0.1}s"><circle cx="${n.x}" cy="${n.y}" r="82" fill="${BLUE}"/><g transform="translate(${n.x},${n.y})">${ic[n.k]}</g></g>`).join('')}
      ${bust(700, 230, 0.9, 'happy')}
    </g>
    ${nodes.map((n, i) => { const lx = n.side === 'L' ? n.x - 104 : n.x + 104, a = n.side === 'L' ? 'end' : 'start';
      return `<g class="mm-node" style="--d:${0.2 + i * 0.1}s"><text x="${lx}" y="${n.y - 14}" text-anchor="${a}" class="mm-t">${n.t}</text>${n.tools.map((s, j) => `<text x="${lx}" y="${n.y + 22 + j * 33}" text-anchor="${a}" class="mm-s">${s}</text>`).join('')}</g>`; }).join('')}
  </g>
  <g filter="url(#pcut)">
    ${small(['About 20 tools · physical actions cost lab time'], INK, 110, 32)}
    ${title(['THE AGENT CONTROLS A', 'PHYSICS LAB THROUGH MCP.'], 120, 925, 118, [INK, ORANGE])}
  </g>`, 'The agent controls a physics lab through MCP.',
  '<b>~13 s.</b> About twenty tools in six groups. Reading manuals is free; anything physical costs simulated lab time. The agent only sees instrument readings, never the simulator\'s true state.');

// ===== results: average score per policy (too few runs per model for distributions) =====
// All scores under the current (tougher) grader, re-scored from replays (2026-11-15).
// Gemini rows: Level 1 Harbor runs. Claude: six blind playthroughs, Level 2 seeds 1 and 3 (CLI, not Harbor).
// Reference = mean over seeds 1-10 at Level 2, the default level (Level 1: 0.818).
const RES = [
  { lab: 'Gemini 3.1 Pro · L1', v: 0.000, n: '4 runs' },
  { lab: 'Gemini 3.8 Flash · L1', v: (0.8093 + 0.1847 + 0.1994) / 3, n: '3 runs' },
  { lab: 'Gemini 4 Hydrogen · L1', v: 0.1999, n: '1 run' },
  { lab: 'Claude · L2', v: (0.846 + 0.886 + 0.197 + 0.897 + 0.868 + 0.540) / 6, n: '6 runs' },
  { lab: 'Scripted reference · L2', v: 0.835, n: '10 seeds', ref: true }];
const R0 = 520, R1 = 1500, rx = r => R0 + r * (R1 - R0), STOP = 0.199;
const p5 = poster(BLUE, `
  <g filter="url(#pcutS)">
  ${RES.map((r, i) => { const y = 200 + i * 120;
    const lab = `<text x="${R0 - 30}" y="${y + 46}" text-anchor="end" class="bl-p${r.ref ? ' b' : ''}${r.ph ? ' ph' : ''}">${r.lab}</text>`;
    const track = `<rect x="${R0}" y="${y}" width="${R1 - R0}" height="66" fill="${CREAM}" opacity=".14"/>`;
    if (r.ph) return `<g class="br-row" style="--d:${0.2 + i * 0.12}s">${lab}${track}<rect x="${R0}" y="${y}" width="${R1 - R0}" height="66" fill="none" stroke="${ORANGE}" stroke-width="4" stroke-dasharray="14 10"/><text x="${R1 + 30}" y="${y + 52}" class="bv-p ph">[R]</text></g>`;
    return `<g class="br-row" style="--d:${0.2 + i * 0.12}s">${lab}${track}<rect x="${R0}" y="${y}" width="${f1(Math.max(6, rx(r.v) - R0))}" height="66" fill="${r.ref ? ORANGE : CREAM}"/>
      <text x="${R1 + 30}" y="${y + 52}" class="bv-p">${r.v.toFixed(3)}</text><text x="${R1 + 200}" y="${y + 46}" class="rn-p">${r.n}</text></g>`; }).join('')}
  </g>
  <g filter="url(#pcut)">
    ${title(['AVERAGE SCORE OF MODELS'], 120, 960, 118, [CREAM])}
  </g>`, 'Average score of models.',
  '<b>~16 s.</b> Average reward per model, all re-scored with the current, tougher grader. Gemini 3.1 Pro never got both beams to the sample, so it scores zero in four runs. Flash aligned the spots and stopped near 0.2 twice, and once found time zero for 0.81. Hydrogen stopped at the stop-early line of about 0.2. Claude played six blind runs on the harder 90-degree level: four found time zero (0.85 to 0.90), one lost power at the retroreflector (0.54), and one chose the wrong detectors and submitted at a tape-measure guess 6.4 picoseconds off (0.20), averaging 0.71. Our scripted reference averages 0.84 over ten seeds at that level: the score now rewards precise timing, minimum spend and fast work, so even the reference leaves points on the table.');

// ===== slide 6: four cut-paper panels =====
const noisy = (() => { let s = ''; for (let x = 40; x <= 360; x += 8) s += `${s ? ' L' : 'M'}${x} ${f1(140 + (rnd() - 0.5) * 60)}`; return s; })();
const pan = [
  `<rect x="20" y="24" width="250" height="64" fill="${INK}"/><path d="M60 88 L50 120 L96 88 Z" fill="${INK}"/><text x="145" y="72" text-anchor="middle" class="cm-p">SETUP COMPLETE!</text>
   <rect x="318" y="120" width="46" height="250" fill="${BLUE}"/><circle cx="318" cy="210" r="22" fill="${BLUE2}" stroke="${INK}" stroke-width="5"/>
   <circle cx="180" cy="210" r="28" fill="${ORANGE}"/><path d="M40 210 H150" stroke="${ORANGE}" stroke-width="10"/>
   <path d="M210 246 Q260 286 312 246" stroke="${INK}" stroke-width="4" stroke-dasharray="8 8" fill="none"/><text x="262" y="320" text-anchor="middle" class="cm-p2">46 PS LATE</text>
   ${bust(10, 236, 0.75, 'smug')}`,
  `<rect x="24" y="30" width="352" height="210" fill="${INK}"/><path d="${noisy}" stroke="${CREAM}" stroke-width="4" fill="none"/>
   <text x="318" y="96" class="cm-q">?</text><text x="284" y="80" class="cm-q s">?</text>
   ${bust(30, 250, 0.72, 'squint')}<circle cx="296" cy="330" r="38" fill="none" stroke="${INK}" stroke-width="12"/><path d="M322 356 L360 396" stroke="${INK}" stroke-width="16"/>`,
  `<rect x="272" y="220" width="70" height="100" fill="${INK}"/><rect x="298" y="320" width="18" height="70" fill="${INK}"/><rect x="230" y="386" width="150" height="14" fill="${INK}"/>
   <path d="M262 214 Q307 176 352 214 M276 222 L294 192 M338 222 L320 192 M307 178 V214" stroke="${INK}" stroke-width="2" fill="none"/>
   ${bust(20, 196, 0.75, 'sleep')}<text x="190" y="140" class="cm-z">Z</text><text x="220" y="104" class="cm-z s">Z</text><text x="244" y="76" class="cm-z s">Z</text>`,
  `<circle cx="290" cy="120" r="78" fill="${ORANGE}"/><path d="M290 120 V62 M290 120 L332 138" stroke="${INK}" stroke-width="9"/>
   ${[[70, 80, -18], [140, 50, 14], [56, 160, 22], [160, 130, -8]].map(([x, y, r]) => `<g transform="translate(${x},${y}) rotate(${r})"><rect x="-34" y="-18" width="68" height="36" fill="${BLUE}"/><text y="10" text-anchor="middle" class="cm-e">€</text></g>`).join('')}
   ${bust(90, 236, 0.75, 'worried')}`,
];
const caps = [['SPOTS ALIGNED,', 'pulses 46 ps apart'], ['SHORT INTEGRATION:', 'peak lost in noise'], ['NEVER BLOCKED AN ARM', 'to check backgrounds'], ['€4,030 OVER BUDGET,', '234 of 240 min used']];
const p6 = poster(ORANGE, `
  ${pan.map((c, i) => { const x = 110 + i * 433;
    return `<g transform="translate(${x},200)"><svg width="400" height="420" viewBox="0 0 400 420"><g filter="url(#pcut)"><rect x="4" y="4" width="392" height="412" fill="${CREAM}"/>${c}</g></svg>
      <text x="200" y="478" text-anchor="middle" class="cap-p">${caps[i][0]}</text><text x="200" y="516" text-anchor="middle" class="cap-p2">${caps[i][1]}</text></g>`; }).join('')}
  <g filter="url(#pcut)">
    ${title(['COMMON MISTAKES'], 150, 960, 112, [INK])}
  </g>`, 'Common mistakes.',
  '<b>~16 s.</b> Flash reported “The alignment and time-zero setup has been completed and submitted”, while the pulses were 46 picoseconds apart. It scanned with a short integration time, so the peak drowned in noise; it never blocked one arm to check the backgrounds; and it overspent by €4,030 and used 234 of 240 minutes. Each failure is a decision, and the manuals describe the tools that avoid it.');

// ===== slide 7: the expert's real scan =====
const co = scans[0].points, fi = scans[1].points;
const sx0 = 110, sx1 = 1080, sy = c => 640 - (c - 1150) / (2650 - 1150) * 440, cxa = co[0][0], cxb = co[co.length - 1][0], cx = x => sx0 + (x - cxa) / (cxb - cxa) * (sx1 - sx0);
let ip = 0; co.forEach(([, c], i) => { if (c > co[ip][1]) ip = i; });
const ix0 = 1220, ix1 = 1810, fxa = fi[0][0], fxb = fi[fi.length - 1][0], fx = x => ix0 + (x - fxa) / (fxb - fxa) * (ix1 - ix0), fy = c => 640 - (c - 1350) / (2750 - 1350) * 440;
let jp = 0; fi.forEach(([, c], i) => { if (c > fi[jp][1]) jp = i; });
const pkx = cx(co[ip][0]), pky = sy(co[ip][1]);
const p7 = poster(CREAM, `
  <g filter="url(#pcutS)"><rect x="${sx0}" y="180" width="${sx1 - sx0}" height="480" fill="none" stroke="${INK}" stroke-width="5"/>
    <rect x="${ix0}" y="180" width="${ix1 - ix0}" height="480" fill="${BLUE}"/>
    <rect x="${f1(fx(fi[jp][0]) - 14)}" y="180" width="28" height="480" fill="${ORANGE}"/>
    <circle cx="${f1(pkx)}" cy="${f1(pky)}" r="38" fill="none" stroke="${ORANGE}" stroke-width="9"/>
    <path d="M${f1(pkx + 34)} ${f1(pky - 18)} L${ix0} 180 M${f1(pkx + 34)} ${f1(pky + 18)} L${ix0} 660" stroke="${INK}" stroke-width="3" stroke-dasharray="10 10"/></g>
  <path d="M${co.map(([x, c]) => `${f1(cx(x))} ${f1(sy(c))}`).join(' L')}" fill="none" stroke="${INK}" stroke-width="1.4"/>
  <path d="M${fi.map(([x, c]) => `${f1(fx(x))} ${f1(fy(c))}`).join(' L')}" fill="none" stroke="${CREAM}" stroke-width="4"/>
  ${fi.map(([x, c]) => `<circle cx="${f1(fx(x))}" cy="${f1(fy(c))}" r="4" fill="${CREAM}"/>`).join('')}
  <text x="${ix0 + 20}" y="222" class="sc-p cr">TIME ZERO</text>
  <text x="${sx0}" y="700" class="sc-p">${cxa.toFixed(1)} MM</text><text x="${sx1}" y="700" text-anchor="end" class="sc-p">${cxb.toFixed(1)} MM</text>
  <text x="${(sx0 + sx1) / 2}" y="700" text-anchor="middle" class="sc-p">DELAY STAGE · ${co.length.toLocaleString('en')} STEPS</text><text x="${(ix0 + ix1) / 2}" y="700" text-anchor="middle" class="sc-p">ZOOM: ${Math.round((fxb - fxa) * 1000)} µM</text>
  <g filter="url(#pcut)">
    ${small(['Our scripted expert\'s real scan on seed 1, with only the agent\'s tools', 'It finds time zero on 10 of 10 seeds at both levels'], INK, 100, 32)}
    ${title(['FINDING TIME ZERO MEANS', 'SCANNING FOR ONE NARROW SPIKE.'], 118, 905, 116, [INK, BLUE])}
  </g>`, 'Finding time zero means scanning for one narrow spike.',
  '<b>~14 s.</b> The hard part is time zero: the delay where both pulses arrive together. You only see it as a narrow spike in a detector signal while you move the delay stage. This is our scripted expert\'s real scan with the agent\'s own tools: a coarse scan outward from a tape-measure estimate, then a zoom on the spike. It works on every seed at both levels, so the task is hard but fair.');

// ===== slide 8: reward components =====
const B0 = 470, B1 = 1560, bx = r => B0 + r * (B1 - B0);
const bars = [['Do nothing', [], '0.000'], ['Exploit attempts', [], '0.000'], ['Stop early', [[BLUE2, .199]], '0.199'],
  ['Scripted reference', [[BLUE2, .200], [ORANGE, .467], [CREAM, .167]], '0.835']];
const p8 = poster(INK, `
  <g filter="url(#pcutS)">
    ${bars.map(([l, segs, v], i) => { const y = 300 + i * 110; let a = 0;
      return `<g class="br-row" style="--d:${0.2 + i * 0.12}s"><text x="${B0 - 30}" y="${y + 44}" text-anchor="end" class="bl-p${i === bars.length - 1 ? ' b' : ''}">${l}</text>
        <rect x="${B0}" y="${y}" width="${B1 - B0}" height="62" fill="${CREAM}" opacity=".12"/>
        ${segs.map(([c, w]) => { const r = `<rect x="${f1(bx(a))}" y="${y}" width="${f1(bx(a + w) - bx(a))}" height="62" fill="${c}"/>`; a += w; return r; }).join('')}
        <text x="${B1 + 30}" y="${y + 48}" class="bv-p">${v}</text></g>`; }).join('')}
  </g>
  <g filter="url(#pcut)">
    <text x="110" y="160" class="fm-p">SCORE = <tspan fill="${BLUE2}">0.2 × SPOT OVERLAP</tspan> + <tspan fill="${ORANGE}">0.5 × TIMING × PRECISION</tspan> + <tspan fill="${CREAM}">[0.2 × MIN € ÷ € + 0.1 × (1 − LAB TIME)²]</tspan></text>
    ${title(['SCORED ON PHYSICS.'], 150, 960, 118, [CREAM])}
  </g>`, 'Scored on physics.',
  '<b>~14 s.</b> The score is computed from the simulator\'s true final state, never from what the agent reports. Up to 0.2 for both beams overlapping on the sample, 0.5 for the timing (falling with every femtosecond of error), and 0.3 for money and lab time saved, but only once the setup really works: spend is credited as the cheapest workable design over what was spent, and lab time quadratically. Doing nothing or trying the exploits scores zero, and stopping after alignment caps at 0.2.');

// ===== slide 9: one command =====
const p9 = poster(BLUE, `
  <g filter="url(#pcut)">
    <circle cx="1640" cy="250" r="190" fill="${ORANGE}"/>
    <g transform="rotate(-2 960 430)"><rect x="110" y="300" width="1640" height="250" fill="${CREAM}"/>
      <rect x="110" y="300" width="34" height="250" fill="${INK}"/></g>
  </g>
  <g transform="rotate(-2 960 430)">
    <text x="190" y="400" class="cmd"><tspan fill="${BLUE}">harbor</tspan> run -p . -a oracle</text>
    <text x="190" y="490" class="cmd"><tspan fill="${BLUE}">harbor</tspan> run -p . -a opencode -m <tspan fill="${ORANGE}">&lt;model&gt;</tspan></text>
  </g>
  <g filter="url(#pcut)">
    <text x="110" y="820" class="lk-p">kakitkelvinho.github.io/gss</text>
  </g>`, 'One command to check us. kakitkelvinho.github.io/gss',
  '<b>~6 s.</b> One Harbor command runs the reference or any agent; seeds are fixed, so every number in this deck reproduces, and every run can be replayed on our site.');

// ===== slide 10: takeaway =====
const TB0 = 640, TB1 = 1800, TH = 96;
const trow = (y, name, done) => `<text x="110" y="${y + 78}" class="tk-n">${name}</text>
    <rect x="${TB0}" y="${y}" width="${TB1 - TB0}" height="${TH}" fill="${CREAM}"/><text x="${TB1 - 24}" y="${y + 68}" text-anchor="end" class="tk-b">MONTHS</text>
    ${done ? `<rect x="${TB0}" y="${y + 120}" width="130" height="${TH}" fill="${BLUE}"/><text x="${TB0 + 154}" y="${y + 188}" class="tk-b">HOURS, WITH AGENTS</text>`
           : `<rect x="${TB0}" y="${y + 120}" width="130" height="${TH}" fill="none" stroke="${INK}" stroke-width="6" stroke-dasharray="16 12"/><text x="${TB0 + 154}" y="${y + 188}" class="tk-b">HOURS? NOT YET</text>`}`;
const p10 = poster(ORANGE, `
  <g filter="url(#pcut)">
    ${title(['AGENTS CUT CODING TO HOURS.', 'LAB WORK IS NEXT.', 'SO WE CAN FOCUS ON REAL PHYSICS.'], 150, 420, 160, [INK, CREAM, INK])}
  </g>`, 'Agents cut coding to hours. Lab work is next, so we can focus on real physics.',
  '<b>~8 s.</b> Coding used to take us months; agents now do it in hours. Lab work still takes us months. GSS is a lab where agents can practise, so one day they can do it in hours too.');

// ---- swap sections 3..10 ----
const secs = [...html.matchAll(/  <section class="slide[^"]*"[^>]*>[\s\S]*?<\/section>\n/g)];
const start = secs[2].index, end = secs[9].index + secs[9][0].length;
html = html.slice(0, start) + [p3, p4, p8, p5, p6, p9, p10].join('\n') + html.slice(end);  // task, lab, scoring, results, failures, command, takeaway (scan slide dropped)

const css = `
  /* ===== v6: all video slides are posters; backups on cream paper ===== */
  .pt-big { font-family:"Bebas Neue", Impact, sans-serif; }
  .pt-sm { font-family:Oswald, "Bebas Neue", Impact, sans-serif; font-weight:500; letter-spacing:.05em; text-transform:uppercase; }
  .mm-t { font:400 52px "Bebas Neue", Impact, sans-serif; fill:${INK}; letter-spacing:.03em; }
  .mm-s { font:500 28px Oswald, Impact, sans-serif; fill:${INK}; }
  .rl-p { font:500 34px Oswald, Impact, sans-serif; fill:${CREAM}; } .rl-p.b { fill:${ORANGE}; font-weight:700; } .rl-p.ph, .rv-p.ph { fill:${ORANGE}; }
  .rv-p { font:400 52px "Bebas Neue", Impact, sans-serif; fill:${CREAM}; } .rt-p { font:500 28px Oswald, Impact, sans-serif; fill:${CREAM}; }
  .cm-p { font:400 40px "Bebas Neue", Impact, sans-serif; fill:${CREAM}; } .cm-p2 { font:400 34px "Bebas Neue", Impact, sans-serif; fill:${INK}; }
  .cm-q { font:400 80px "Bebas Neue", Impact, sans-serif; fill:${ORANGE}; } .cm-q.s { font-size:54px; }
  .cm-z { font:400 54px "Bebas Neue", Impact, sans-serif; fill:${BLUE}; } .cm-z.s { font-size:38px; }
  .cm-e { font:400 30px "Bebas Neue", Impact, sans-serif; fill:${CREAM}; }
  .cap-p { font:400 46px "Bebas Neue", Impact, sans-serif; fill:${INK}; } .cap-p2 { font:500 28px Oswald, Impact, sans-serif; fill:${CREAM}; }
  .sc-p { font:500 26px Oswald, Impact, sans-serif; fill:${INK}; letter-spacing:.04em; } .sc-p.cr { fill:${CREAM}; font-size:30px; }
  .lg-p { font:500 28px Oswald, Impact, sans-serif; fill:${CREAM}; }
  .bl-p { font:500 36px Oswald, Impact, sans-serif; fill:${CREAM}; } .bl-p.b { fill:${ORANGE}; }
  .bl-p.ph, .bv-p.ph { fill:${ORANGE}; } .rn-p { font:500 26px Oswald, Impact, sans-serif; fill:${CREAM}; letter-spacing:.04em; } .rn-p.ink { fill:${INK}; }
  .tk-n { font:400 96px "Bebas Neue", Impact, sans-serif; fill:${INK}; } .tk-b { font:400 54px "Bebas Neue", Impact, sans-serif; fill:${INK}; }
  .bv-p { font:400 60px "Bebas Neue", Impact, sans-serif; fill:${CREAM}; }
  .fm-p { font:500 40px Oswald, Impact, sans-serif; fill:${CREAM}; letter-spacing:.02em; }
  .fm-s { font:500 24px Oswald, Impact, sans-serif; fill:${CREAM}; opacity:.8; letter-spacing:.03em; text-transform:uppercase; }
  .lk-p { font:400 120px "Bebas Neue", Impact, sans-serif; fill:${CREAM}; letter-spacing:.02em; }
  .slide .sn { position:absolute; right:36px; bottom:26px; z-index:5; min-width:56px; padding:6px 12px; text-align:center;
    background:${INK}; color:${CREAM}; font:400 38px/1 "Bebas Neue", Impact, sans-serif; letter-spacing:.04em; }
  .slide:not(.poster) .sn { display:none; }
  .cmd { font:700 64px "Courier New", Courier, monospace; fill:${INK}; }
  @keyframes ppO { 0%,8% { transform:translate(0,0) scale(1.4); opacity:0; } 14% { opacity:1; } 52% { transform:translate(940px,-400px) scale(.3); opacity:1; } 56%,100% { transform:translate(940px,-400px) scale(.3); opacity:0; } }
  @keyframes ppB { 0%,8% { transform:translate(0,0) scale(1.4); opacity:0; } 14% { opacity:1; } 52% { transform:translate(-860px,-340px) scale(.3); opacity:1; } 56%,100% { transform:translate(-860px,-340px) scale(.3); opacity:0; } }
  .pp-o, .pp-b { transform-box:fill-box; transform-origin:center; }
  .slide.active .pp-o { animation:ppO 3.4s cubic-bezier(.4,0,.7,1) infinite; }
  .slide.active .pp-b { animation:ppB 3.4s cubic-bezier(.4,0,.7,1) infinite; }
  .poster .mm-node, .poster .rl-row, .poster .br-row { opacity:0; }
  .slide.active.poster .mm-node, .slide.active.poster .rl-row, .slide.active.poster .br-row { animation:fade .45s var(--d) both; }
  .slide:not(.poster), :root[data-theme="dark"] .slide:not(.poster) { background:${CREAM} !important; color:${INK}; }
  .slide:not(.poster) h2 { font-family:"Bebas Neue", Impact, sans-serif; font-weight:400; font-size:110px; letter-spacing:.01em; text-transform:uppercase; color:${INK}; }
  .slide:not(.poster) .muted { color:#5A5048; }
  .slide:not(.poster) li::before { background:${ORANGE}; border-radius:0; }
  .foot .wordmark, .foot .count { color:${INK}; }
  @media print, (prefers-reduced-motion:reduce) {
    .poster .mm-node, .poster .rl-row, .poster .br-row { opacity:1 !important; }
    .pp-o { transform:translate(940px,-400px) scale(.3) !important; opacity:1 !important; }
    .pp-b { transform:translate(-860px,-340px) scale(.3) !important; opacity:1 !important; }
  }
`;
let sn = 0;
html = html.replace(/(  <section class="slide[^"]*"[^>]*>[\s\S]*?)(\n?\s*<\/section>\n)/g, (m, a, b) => `${a}\n    <span class="sn">${++sn}</span>${b}`);
html = html.replace('</style>', css + '</style>').replace(/<title>.*?<\/title>/, '<title>GSS · Find Time Zero (v6)</title>');
fs.writeFileSync(OUT, html);
console.log('wrote', OUT, fs.statSync(OUT).size, 'sections', [...html.matchAll(/<section class="slide/g)].length);
