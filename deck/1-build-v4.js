// pitch-deck-v4.html: retrofuturist paperback restyle, dark-first. Head/controls from v2.
const fs = require('fs');
const SRC = __dirname + '/base-v2.html';
const OUT = __dirname + '/out/pitch-deck-v4.html';
const src = fs.readFileSync(SRC, 'utf8');
const scans = JSON.parse(fs.readFileSync(__dirname + '/scans.json', 'utf8')).scans;
const f1 = x => Math.round(x * 10) / 10;
let SEED = 11;
const rnd = () => (SEED = (SEED * 16807) % 2147483647) / 2147483647;

// palette (painted plates keep these in both themes)
const NIGHT = '#0D0A1C', INDIGO = '#1C1438', PLUM = '#3B1F4E', ROSE = '#E8637A', PEACH = '#F6B26B',
  AMBER = '#F2A93B', CYAN = '#5FD3E0', CREAM = '#F3E9D7', OUT_ = '#15111F', RED = '#FF4D45', TEALB = '#4FE3D6';

// ---------- global defs ----------
const defs = `
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <linearGradient id="chr" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#3A4049"/><stop offset=".16" stop-color="#C9D2DA"/><stop offset=".3" stop-color="#F8FBFD"/>
    <stop offset=".44" stop-color="#8C96A1"/><stop offset=".62" stop-color="#2E333B"/><stop offset=".8" stop-color="#B7C1CA"/><stop offset="1" stop-color="#5E6670"/></linearGradient>
  <linearGradient id="chrV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F8FBFD"/><stop offset=".35" stop-color="#9AA4AF"/><stop offset=".55" stop-color="#2E333B"/><stop offset=".8" stop-color="#C3CCD4"/><stop offset="1" stop-color="#59616B"/></linearGradient>
  <radialGradient id="jnt" cx=".35" cy=".35"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#A9B3BD"/><stop offset="1" stop-color="#2F353E"/></radialGradient>
  <radialGradient id="coreR"><stop offset="0" stop-color="#FFF"/><stop offset=".35" stop-color="#FF8A80"/><stop offset="1" stop-color="${RED}" stop-opacity="0"/></radialGradient>
  <radialGradient id="coreC"><stop offset="0" stop-color="#FFF"/><stop offset=".35" stop-color="#B8F6FF"/><stop offset="1" stop-color="${CYAN}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gRed"><stop offset="0" stop-color="#fff"/><stop offset=".22" stop-color="#ffd0c8"/><stop offset=".55" stop-color="${RED}" stop-opacity=".9"/><stop offset="1" stop-color="${RED}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gTeal"><stop offset="0" stop-color="#fff"/><stop offset=".22" stop-color="#d0fffa"/><stop offset=".55" stop-color="${TEALB}" stop-opacity=".9"/><stop offset="1" stop-color="${TEALB}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gHit"><stop offset="0" stop-color="#fff"/><stop offset=".25" stop-color="#FFF4C8"/><stop offset=".6" stop-color="${AMBER}" stop-opacity=".75"/><stop offset="1" stop-color="${AMBER}" stop-opacity="0"/></radialGradient>
  <linearGradient id="plateG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A1234"/><stop offset=".7" stop-color="#2A1846"/><stop offset="1" stop-color="#4A2348"/></linearGradient>
  <linearGradient id="coat" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9B3C6"/><stop offset=".45" stop-color="#F4EFE6"/><stop offset="1" stop-color="#D8CFC6"/></linearGradient>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="glowL" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="12" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
</defs></svg>`;

// ---------- helpers ----------
const rot = ([x, y], [cx, cy], deg) => { const a = deg * Math.PI / 180, dx = x - cx, dy = y - cy;
  return [cx + dx * Math.cos(a) - dy * Math.sin(a), cy + dx * Math.sin(a) + dy * Math.cos(a)]; };
const pl = pts => 'M' + pts.map(p => `${f1(p[0])} ${f1(p[1])}`).join(' L');
// chrome tube: dark rim, steel body, highlight
const tube = (pts, w) => { const d = pl(pts), o = (w * 0.2).toFixed(1);
  return `<path d="${d}" stroke="${OUT_}" stroke-width="${w + 7}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="${d}" stroke="#7C8794" stroke-width="${w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="${d}" stroke="#D9E1E8" stroke-width="${(w * 0.38).toFixed(1)}" fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate(-${o},-${o})"/>
  <path d="${d}" stroke="#FFFFFF" stroke-width="${(w * 0.12).toFixed(1)}" fill="none" stroke-linecap="round" stroke-linejoin="round" transform="translate(-${(w * 0.28).toFixed(1)},-${(w * 0.3).toFixed(1)})" opacity=".8"/>`; };
const joint = ([x, y], r) => `<circle cx="${f1(x)}" cy="${f1(y)}" r="${r}" fill="url(#jnt)" stroke="${OUT_}" stroke-width="3"/>`;
const stars = (n, w, h, ymax, op = .8) => Array.from({ length: n }, () =>
  `<circle cx="${f1(rnd() * w)}" cy="${f1(rnd() * ymax)}" r="${f1(0.8 + rnd() * 1.8)}" fill="#fff" opacity="${f1(0.25 + rnd() * op * 0.7)}"/>`).join('');

// ---------- chrome humanoid (local: feet at y=0) ----------
function chromeBot(eye = RED) {
  const lean = 12, pv = [0, -205], R = p => rot(p, pv, lean);
  const SF = R([52, -322]), SB = R([-52, -322]), HF = R([18, -205]), HB = R([-18, -205]);
  const backArm = [SB, [-72, -282], [-98, -222]], frontArm = [SF, [150, -298], [214, -330]];
  const backLeg = [HB, [-48, -112], [-126, -72]], frontLeg = [HF, [86, -126], [72, -20]];
  const coreG = eye === RED ? 'coreR' : 'coreC';
  return `
  <ellipse cx="10" cy="4" rx="150" ry="18" fill="#000" opacity=".45" filter="url(#blur)"/>
  ${tube(backArm, 22)} ${joint(backArm[1], 13)}
  ${tube([[-98, -222], [-112, -196]], 9)} ${tube([[-98, -222], [-92, -192]], 9)}
  ${tube(backLeg, 28)} ${joint(backLeg[1], 16)} ${tube([[-126, -72], [-146, -42]], 20)}
  <g transform="rotate(${lean} ${pv[0]} ${pv[1]})">
    <path d="M-38 -192 L38 -192 L30 -230 L-30 -230 Z" fill="url(#chr)" stroke="${OUT_}" stroke-width="4" stroke-linejoin="round"/>
    <rect x="-24" y="-264" width="48" height="36" rx="10" fill="#2A2F38" stroke="${OUT_}" stroke-width="3"/>
    <rect x="-29" y="-243" width="58" height="9" rx="4" fill="url(#chr)" stroke="${OUT_}" stroke-width="2"/>
    <rect x="-29" y="-259" width="58" height="9" rx="4" fill="url(#chr)" stroke="${OUT_}" stroke-width="2"/>
    <path d="M-60 -342 Q0 -356 60 -342 L46 -262 Q0 -254 -46 -262 Z" fill="url(#chr)" stroke="${OUT_}" stroke-width="4" stroke-linejoin="round"/>
    <path d="M-30 -330 L-22 -276 M30 -330 L22 -276" stroke="${OUT_}" stroke-width="2.5" opacity=".6"/>
    <circle cx="0" cy="-302" r="26" fill="url(#${coreG})"/><circle cx="0" cy="-302" r="9" fill="#fff"/>
    <rect x="-11" y="-364" width="22" height="24" fill="#2A2F38" stroke="${OUT_}" stroke-width="3"/>
    <path d="M-38 -360 Q-44 -430 0 -434 Q44 -430 38 -360 Q0 -350 -38 -360 Z" fill="url(#chr)" stroke="${OUT_}" stroke-width="4" stroke-linejoin="round"/>
    <path d="M-32 -402 Q0 -412 32 -402 L30 -384 Q0 -392 -30 -384 Z" fill="#14060C" stroke="${OUT_}" stroke-width="3"/>
    <path d="M-26 -399 L-6 -392 M26 -399 L6 -392" stroke="${eye}" stroke-width="6" stroke-linecap="round" filter="url(#glow)"/>
    <path d="M-16 -372 H16 M-14 -366 H14" stroke="${OUT_}" stroke-width="2.5"/>
    ${joint([-41, -392], 10)} ${joint([41, -392], 10)}
    <path d="M0 -434 V-454" stroke="${OUT_}" stroke-width="5"/><circle cx="0" cy="-458" r="7" fill="${eye}" filter="url(#glow)"/>
  </g>
  ${joint(SB, 18)}
  ${tube(frontLeg, 30)} ${joint(frontLeg[1], 17)} ${tube([[72, -20], [120, -8]], 20)}
  ${joint(HF, 15)}
  ${tube(frontArm, 24)} ${joint(frontArm[1], 14)} ${joint(SF, 20)}
  ${tube([[214, -330], [242, -348]], 9)} ${tube([[214, -330], [248, -330]], 9)} ${tube([[214, -330], [240, -310]], 9)}`;
}

// chrome bust (local 0..220 x 0..240), expression glyphs inside the visor
const VIS = {
  happy: `<path d="M86 76 Q96 64 106 76 M114 76 Q124 64 134 76" stroke="${CYAN}" stroke-width="5" fill="none" stroke-linecap="round" filter="url(#glow)"/>`,
  smug: `<path d="M84 70 H104 M116 70 H136" stroke="${CYAN}" stroke-width="5" stroke-linecap="round" filter="url(#glow)"/><path d="M104 80 Q120 86 134 76" stroke="${CYAN}" stroke-width="3" fill="none" stroke-linecap="round" filter="url(#glow)"/>`,
  squint: `<path d="M84 72 H104 M116 72 H136" stroke="${CYAN}" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>`,
  sleep: `<path d="M84 74 Q94 80 104 74 M116 74 Q126 80 136 74" stroke="${CYAN}" stroke-width="4" fill="none" stroke-linecap="round" filter="url(#glow)"/>`,
  worried: `<circle cx="94" cy="74" r="5" fill="${CYAN}" filter="url(#glow)"/><circle cx="126" cy="74" r="5" fill="${CYAN}" filter="url(#glow)"/><path d="M84 64 L102 60 M136 64 L118 60" stroke="${CYAN}" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>`,
};
const bust = (x, y, s, mood) => `<g transform="translate(${x},${y}) scale(${s})">
  <path d="M14 240 Q20 168 70 152 H150 Q200 168 206 240 Z" fill="url(#chr)" stroke="${OUT_}" stroke-width="4" stroke-linejoin="round"/>
  <circle cx="110" cy="196" r="22" fill="url(#coreC)"/><circle cx="110" cy="196" r="7" fill="#fff"/>
  <rect x="96" y="124" width="28" height="30" fill="#2A2F38" stroke="${OUT_}" stroke-width="3"/>
  <path d="M60 116 Q54 22 110 18 Q166 22 160 116 Q110 128 60 116 Z" fill="url(#chr)" stroke="${OUT_}" stroke-width="4" stroke-linejoin="round"/>
  <rect x="72" y="54" width="76" height="34" rx="16" fill="#0A0A14" stroke="${OUT_}" stroke-width="3"/>
  ${VIS[mood]}
  <path d="M94 104 H126 M96 110 H124" stroke="${OUT_}" stroke-width="2.5"/>
  ${joint([58, 76], 12)} ${joint([162, 76], 12)}
  <path d="M110 18 V4" stroke="${OUT_}" stroke-width="5"/><circle cx="110" cy="2" r="6" fill="${CYAN}" filter="url(#glow)"/></g>`;

// ---------- scientist (painted; local coords from the old cartoon, feet ~y505) ----------
const SO = '#1A1222';
const limb = (d, col, w = 22) => `<path d="${d}" fill="none" stroke="${SO}" stroke-width="${w + 7}" stroke-linecap="round" stroke-linejoin="round"/><path d="${d}" fill="none" stroke="${col}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
const scientist = `<g transform="rotate(9 1050 505)">
  <ellipse cx="1040" cy="512" rx="110" ry="12" fill="#000" opacity=".45" filter="url(#blur)"/>
  ${limb('M1040 400 L1000 440 L955 425', '#2B2F3A')}<ellipse cx="943" cy="420" rx="22" ry="11" fill="#111" transform="rotate(-25 943 420)"/>
  ${limb('M1052 400 L1092 445 L1082 495', '#343846')}<ellipse cx="1100" cy="500" rx="24" ry="11" fill="#111"/>
  ${limb('M1022 302 L985 282 L972 232', '#D8D0C8')}<circle cx="970" cy="220" r="14" fill="#E9B994" stroke="${SO}" stroke-width="4"/>
  <path d="M1015 290 Q1050 278 1085 290 L1102 415 Q1062 426 1022 418 L982 430 L998 404 L974 408 Z" fill="url(#coat)" stroke="${SO}" stroke-width="5" stroke-linejoin="round"/>
  <path d="M1051 296 L1060 418" stroke="${SO}" stroke-width="2.5" opacity=".7"/>
  <path d="M1034 290 L1050 312 L1066 288" fill="none" stroke="${SO}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M1073 334 V322 M1081 334 V326" stroke="${ROSE}" stroke-width="4" stroke-linecap="round"/>
  ${limb('M1078 302 L1122 268 L1138 216', '#F1ECE3')}<circle cx="1141" cy="204" r="14" fill="#E9B994" stroke="${SO}" stroke-width="4"/>
  <circle cx="1050" cy="246" r="41" fill="#E9B994" stroke="${SO}" stroke-width="4"/>
  <path d="M1050 205 A41 41 0 0 1 1091 246" fill="none" stroke="${ROSE}" stroke-width="4" opacity=".6"/>
  <circle cx="1013" cy="254" r="8" fill="#E2AE88" stroke="${SO}" stroke-width="3"/>
  <path d="M1012 236 L1018 196 L1033 220 L1043 186 L1056 214 L1069 188 L1075 218 L1092 204 L1088 238 Q1052 214 1012 236 Z" fill="#4A2C1A" stroke="${SO}" stroke-width="4" stroke-linejoin="round"/>
  <rect x="1022" y="238" width="68" height="23" rx="11" fill="#BFEFFF" fill-opacity=".85" stroke="${SO}" stroke-width="4"/>
  <path d="M1030 243 L1046 243" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
  <path d="M1022 248 L1008 246" stroke="${SO}" stroke-width="5" stroke-linecap="round"/>
  <circle cx="1038" cy="251" r="4.5" fill="${SO}"/><circle cx="1063" cy="251" r="4.5" fill="${SO}"/>
  <ellipse cx="1066" cy="275" rx="9" ry="11" fill="#6A2420" stroke="${SO}" stroke-width="3"/>
  <path d="M1000 196 q-8 14 0 18 q8 -4 0 -18 Z M988 232 q-7 12 0 16 q7 -4 0 -16 Z" fill="#9FE2FF" stroke="${SO}" stroke-width="2.5"/>
</g>`;

// ---------- skyline ----------
function skyline(x0, x1, base, hmin, hmax, fill, edge, win) {
  let s = '', x = x0;
  while (x < x1) {
    const w = 26 + rnd() * 70, h = hmin + rnd() * (hmax - hmin), t = base - h, kind = rnd();
    s += `<rect x="${f1(x)}" y="${f1(t)}" width="${f1(w)}" height="${f1(h)}" fill="${fill}"/>`;
    s += `<rect x="${f1(x)}" y="${f1(t)}" width="2" height="${f1(h)}" fill="${edge}"/>`;
    if (kind < 0.3) s += `<ellipse cx="${f1(x + w / 2)}" cy="${f1(t + h * 0.12)}" rx="${f1(w * 1.1)}" ry="${f1(7 + w * 0.08)}" fill="${fill}"/><ellipse cx="${f1(x + w / 2)}" cy="${f1(t + h * 0.12 - 3)}" rx="${f1(w * 1.1)}" ry="2" fill="${edge}"/>`;
    else if (kind < 0.55) s += `<rect x="${f1(x + w * 0.3)}" y="${f1(t - h * 0.18)}" width="${f1(w * 0.4)}" height="${f1(h * 0.18)}" fill="${fill}"/><path d="M${f1(x + w / 2)} ${f1(t - h * 0.18)} V${f1(t - h * 0.3)}" stroke="${fill}" stroke-width="3"/>`;
    else if (kind < 0.7) s += `<ellipse cx="${f1(x + w / 2)}" cy="${f1(t)}" rx="${f1(w / 2)}" ry="${f1(w / 3)}" fill="${fill}"/>`;
    if (win) for (let k = 0; k < 6; k++) s += `<rect x="${f1(x + 6 + rnd() * (w - 12))}" y="${f1(t + 10 + rnd() * (h - 20))}" width="3" height="3" fill="${PEACH}" opacity="${f1(0.4 + rnd() * 0.6)}"/>`;
    x += w + 6 + rnd() * 50;
  }
  return s;
}

// ---------- slide 1: full-bleed cover ----------
const HZ = 760;
const grid = (() => { let s = '';
  for (let k = 1; k < 16; k++) { const y = HZ + k * k * 1.4 + k * 4; if (y > 1080) break; s += `<path d="M0 ${f1(y)} H1920"/>`; }
  for (let i = -16; i <= 16; i++) s += `<path d="M960 ${HZ} L${960 + i * 170} 1080"/>`; return s; })();
const hero = `
<svg class="hero-bg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <defs>
    <linearGradient id="hSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0B0820"/><stop offset=".32" stop-color="#22143F"/><stop offset=".55" stop-color="#5E2758"/><stop offset=".66" stop-color="#C2577A"/><stop offset=".705" stop-color="${PEACH}"/></linearGradient>
    <linearGradient id="hGround" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A1D44"/><stop offset=".4" stop-color="#1A0F2A"/><stop offset="1" stop-color="#08060F"/></linearGradient>
    <radialGradient id="hSun"><stop offset="0" stop-color="#FFF3D6"/><stop offset=".35" stop-color="${PEACH}"/><stop offset="1" stop-color="${ROSE}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="1920" height="${HZ}" fill="url(#hSky)"/>
  ${stars(110, 1920, 1080, 420, 1)}
  <circle cx="960" cy="${HZ}" r="300" fill="url(#hSun)" opacity=".85"/>
  <g opacity=".75">${skyline(-20, 1940, HZ, 120, 300, '#6A3466', '#A2507A', false)}</g>
  ${skyline(-20, 1940, HZ, 60, 230, '#2A1438', '#7A3A6A', true)}
  <rect y="${HZ}" width="1920" height="${1080 - HZ}" fill="url(#hGround)"/>
  <g stroke="${ROSE}" stroke-width="2" opacity=".35">${grid}</g>
  <rect x="0" y="${HZ - 2}" width="1920" height="4" fill="${PEACH}" opacity=".7"/>
  <g stroke="${ROSE}" stroke-width="5" stroke-linecap="round" opacity=".45"><path d="M300 700 H520 M260 760 H500 M320 820 H530"/></g>
  <g class="chase-bot"><g transform="translate(700,1010) scale(1.02)">${chromeBot(RED)}</g></g>
  <g class="chase-sci"><g transform="translate(-60,345) scale(1.3)">${scientist}</g></g>
  <rect x="26" y="26" width="1868" height="1028" fill="none" stroke="${AMBER}" stroke-width="3" opacity=".55"/>
</svg>`;

// ---------- slide 3: pulses converge on a vertical sample (plate) ----------
const wall = `
<svg class="wall-art" viewBox="0 0 1100 660" role="img" aria-label="Two glowing pulses travel out of the page toward a vertical sample and hit the same spot at the same time">
  <defs>
    <radialGradient id="wBg" cx=".55" cy=".45" r=".75"><stop offset="0" stop-color="#2E1C52"/><stop offset=".6" stop-color="#160F2C"/><stop offset="1" stop-color="#0A0716"/></radialGradient>
    <linearGradient id="wFace" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4A5468"/><stop offset=".5" stop-color="#252B3B"/><stop offset="1" stop-color="#121521"/></linearGradient>
    <clipPath id="wClip"><rect width="1100" height="660" rx="26"/></clipPath>
  </defs>
  <g clip-path="url(#wClip)">
  <rect width="1100" height="660" fill="url(#wBg)"/>
  ${stars(70, 1100, 660, 660, .8)}
  <path d="M600 520 h40 v90 h-40 Z" fill="url(#chr)" stroke="${OUT_}" stroke-width="3"/>
  <ellipse cx="620" cy="612" rx="96" ry="18" fill="url(#chrV)" stroke="${OUT_}" stroke-width="3"/>
  <path d="M770 92 L800 70 L800 498 L770 522 Z" fill="#596377" stroke="${OUT_}" stroke-width="3" stroke-linejoin="round"/>
  <path d="M440 92 L470 70 L800 70 L770 92 Z" fill="#8994A8" stroke="${OUT_}" stroke-width="3" stroke-linejoin="round"/>
  <rect x="440" y="92" width="330" height="430" fill="url(#wFace)" stroke="${OUT_}" stroke-width="4"/>
  <rect x="440" y="92" width="330" height="430" fill="none" stroke="${CYAN}" stroke-width="2" opacity=".5"/>
  <path d="M462 118 L560 118 M462 118 L462 210" stroke="#fff" stroke-opacity=".35" stroke-width="5" stroke-linecap="round"/>
  <polygon points="605,300 -20,560 90,690" fill="${RED}" fill-opacity=".14"/>
  <polygon points="605,300 1130,520 1040,690" fill="${TEALB}" fill-opacity=".14"/>
  <path d="M605 300 L35 625" stroke="${RED}" stroke-width="5" filter="url(#glow)" opacity=".9"/>
  <path d="M605 300 L1085 605" stroke="${TEALB}" stroke-width="5" filter="url(#glow)" opacity=".9"/>
  <ellipse class="hit" cx="605" cy="300" rx="120" ry="120" fill="url(#gHit)"/>
  <path class="hit" d="M605 220 L611 294 L685 300 L611 306 L605 380 L599 306 L525 300 L599 294 Z" fill="#FFF8E0"/>
  <g class="p-red"><ellipse cx="35" cy="625" rx="70" ry="70" fill="url(#gRed)"/></g>
  <g class="p-teal"><ellipse cx="1085" cy="605" rx="70" ry="70" fill="url(#gTeal)"/></g>
  </g>
  <rect x="2" y="2" width="1096" height="656" rx="26" fill="none" stroke="${AMBER}" stroke-width="3" opacity=".6"/>
</svg>`;

// ---------- slide 4: MCP mind map (plate, neon icons) ----------
const nS = (c, w = 4) => `fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"`;
const icon = {
  read: `<path d="M-52 -22 Q-26 -36 0 -22 L0 32 Q-26 18 -52 32 Z M52 -22 Q26 -36 0 -22 L0 32 Q26 18 52 32 Z" ${nS(CYAN)}/><path d="M-42 -10 L-12 -16 M-42 2 L-12 -4 M12 -16 L42 -10 M12 -4 L42 2" ${nS(CYAN, 2.5)}/>`,
  buy: `<path d="M-62 -38 H-46 L-36 -22 H44 L32 16 H-26 Z M-26 16 L-30 26 H34" ${nS(AMBER)}/><circle cx="-20" cy="36" r="7" ${nS(AMBER)}/><circle cx="24" cy="36" r="7" ${nS(AMBER)}/><circle cx="2" cy="-36" r="11" ${nS(CYAN, 3)}/>`,
  build: `<rect x="-38" y="-38" width="76" height="76" rx="8" ${nS(CYAN)}/><circle cx="0" cy="0" r="22" ${nS(CYAN)}/><circle cx="40" cy="-30" r="9" ${nS(AMBER)}/><circle cx="-30" cy="40" r="9" ${nS(AMBER)}/><path d="M58 -42 A22 22 0 0 1 52 -6 M44 -10 L52 -4 L58 -14" ${nS(ROSE)}/>`,
  look: `<path d="M-78 0 H-42" ${nS(RED, 5)}/><rect x="-40" y="-30" width="84" height="60" rx="8" ${nS(AMBER)}/><circle cx="2" cy="0" r="10" fill="#FFF4C8" filter="url(#glowL)"/><path d="M2 -24 V-38 M22 -16 L32 -26 M-18 -16 L-28 -26" ${nS(AMBER, 3)}/>`,
  tzero: `<path d="M-56 18 L-44 15 L-36 19 L-26 14 L-16 18 L-9 -8 L-2 -38 L5 -10 L12 17 L22 14 L32 19 L44 15 L56 18" ${nS(RED)}/><path d="M-56 36 H56 M-14 28 h28 v14 h-28 Z M-32 54 H32 M-32 54 l8 -5 M-32 54 l8 5 M32 54 l-8 -5 M32 54 l-8 5" ${nS(CYAN, 3)}/>`,
  submit: `<path d="M-44 16 H44 V36 H-44 Z" ${nS(CYAN)}/><path d="M-32 16 Q-32 -28 0 -28 Q32 -28 32 16 Z" fill="${RED}" fill-opacity=".85" stroke="${RED}" stroke-width="4" filter="url(#glowL)"/><path d="M-16 -8 Q-12 -18 -2 -19" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" opacity=".8"/>`,
};
const C = [800, 345];
const nodes = [
  { k: 'read', t: 'Read', tools: ['read_manual', 'get_datasheet', 'list_catalogue · status'], x: 450, y: 140, side: 'L' },
  { k: 'buy', t: 'Buy', tools: ['buy'], x: 800, y: 92, side: 'R' },
  { k: 'build', t: 'Build', tools: ['place · rotate · move', 'remove · knob · install'], x: 1150, y: 140, side: 'R' },
  { k: 'look', t: 'Look', tools: ['ir_card · view_camera', 'measure_path · block'], x: 1150, y: 470, side: 'R' },
  { k: 'tzero', t: 'Find time zero', tools: ['move_stage · scan', 'read_signal'], x: 800, y: 590, side: 'R' },
  { k: 'submit', t: 'Submit', tools: ['submit'], x: 450, y: 470, side: 'L' },
];
const mindmap = `
<svg class="mcp-art" viewBox="0 0 1600 690" role="img" aria-label="Mind map of the agent's MCP tools: read, buy, build, look, find time zero, submit">
  <defs><radialGradient id="mBg" cx=".5" cy=".5" r=".7"><stop offset="0" stop-color="#2B1A4C"/><stop offset=".7" stop-color="#150F2A"/><stop offset="1" stop-color="#0B0818"/></radialGradient>
  <clipPath id="mClip"><rect width="1600" height="690" rx="26"/></clipPath></defs>
  <g clip-path="url(#mClip)"><rect width="1600" height="690" fill="url(#mBg)"/>${stars(90, 1600, 690, 690, .7)}</g>
  <rect x="2" y="2" width="1596" height="686" rx="26" fill="none" stroke="${AMBER}" stroke-width="3" opacity=".6"/>
  ${nodes.map(n => `<path d="M${C[0]} ${C[1]} Q${(C[0] + n.x) / 2} ${(C[1] + n.y) / 2 + 30} ${n.x} ${n.y}" stroke="${AMBER}" stroke-width="3" fill="none" opacity=".55" filter="url(#glow)"/>`).join('')}
  ${nodes.map((n, i) => {
    const lx = n.side === 'L' ? n.x - 96 : n.x + 96, a = n.side === 'L' ? 'end' : 'start';
    const tl = n.tools.map((s, j) => `<text x="${lx}" y="${n.y + 18 + j * 28}" class="mm-tool" text-anchor="${a}">${s}</text>`).join('');
    return `<g class="mm-node" style="--d:${0.25 + i * 0.12}s"><circle cx="${n.x}" cy="${n.y}" r="76" fill="#140E26" stroke="${AMBER}" stroke-width="3"/>
    <circle cx="${n.x}" cy="${n.y}" r="66" fill="none" stroke="${CYAN}" stroke-width="1.5" opacity=".45"/>
    <g transform="translate(${n.x},${n.y})">${icon[n.k]}</g>
    <text x="${lx}" y="${n.y - 16}" class="mm-title" text-anchor="${a}">${n.t}</text>${tl}</g>`;
  }).join('\n  ')}
  ${bust(718, 262, 0.75, 'happy')}
</svg>`;

// ---------- slide 5: ridgeline ----------
const L1 = {
  ref: [.9173, .9218, .9263, .9210, .9278, .9196, .9227, .9190, .9170, .9264],
  stop: [.1994, .1976, .1995, .1994, .1993, .1997, .1998, .1974, .1996, .2000],
  none: Array(10).fill(0), flash: [.185],
};
const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
const X0 = 380, X1 = 1380, H = 170, BW = 0.018, xr = r => X0 + r * (X1 - X0);
function ridge(vals, y0) {
  const ys = [];
  for (let r = 0; r <= 1.0001; r += 0.002) ys.push([r, vals.reduce((s, v) => s + Math.exp(-0.5 * ((r - v) / BW) ** 2), 0)]);
  const m = Math.max(...ys.map(p => p[1]));
  return 'M' + ys.map(([r, d]) => `${f1(xr(r))} ${f1(y0 - H * d / m)}`).join(' L');
}
const rows = [
  { lab: 'Do nothing', v: L1.none, val: '0.000', n: 'n = 10' },
  { lab: 'Stop early', v: L1.stop, val: mean(L1.stop).toFixed(3), n: 'n = 10' },
  { lab: 'Gemini 3.8 Flash*', v: L1.flash, val: '0.185', n: 'n = 1', cls: 'one' },
  { lab: '[Model A]', ph: true }, { lab: '[Model B]', ph: true },
  { lab: 'Scripted reference', v: L1.ref, val: mean(L1.ref).toFixed(3), n: 'n = 10', cls: 'ref' },
];
const ridgeSvg = `
<svg class="ridge-art" viewBox="0 0 1560 650" role="img" aria-label="Ridgeline plot of reward over seeds 1 to 10: do nothing at 0, stop early near 0.2, Flash single run 0.185, two pending models, reference near 0.92">
  ${rows.map((r, i) => {
    const y = 215 + i * 72;
    const lab = `<text x="340" y="${y - 6}" text-anchor="end" class="rl-lab${r.cls === 'ref' ? ' b' : ''}">${r.ph ? `<tspan class="ph-t">${r.lab}</tspan>` : r.lab}</text>`;
    if (r.ph) return `<g class="rl-row" style="--d:${0.2 + i * 0.12}s">${lab}<path d="M${X0} ${y} H${X1}" class="rl-ph"/><text x="${X1 + 30}" y="${y - 6}" class="rl-val"><tspan class="ph-t">[R]</tspan></text></g>`;
    const d = ridge(r.v, y);
    return `<g class="rl-row" style="--d:${0.2 + i * 0.12}s">${lab}<path d="${d} L${X1} ${y} L${X0} ${y} Z" class="rl-fill ${r.cls || ''}"/><path d="${d}" class="rl-line ${r.cls || ''}"/>
      <text x="${X1 + 30}" y="${y - 6}" class="rl-val${r.cls === 'ref' ? ' b' : ''}">${r.val}</text><text x="${X1 + 30}" y="${y + 22}" class="rl-n">${r.n}</text></g>`;
  }).join('\n  ')}
  <path d="M${X0} 600 H${X1}" class="rl-axis"/>
  ${[0, 0.25, 0.5, 0.75, 1].map(t => `<path d="M${xr(t)} 600 v12" class="rl-axis"/><text x="${xr(t)}" y="642" text-anchor="middle" class="rl-tick">${t}</text>`).join('')}
</svg>`;

// ---------- slide 6: four painted panels ----------
const P = (x, i, inner, cap) => `<g transform="translate(${x},0)">
  <svg x="6" y="6" width="348" height="400" viewBox="0 0 348 400">
    <defs><clipPath id="pc${i}"><rect width="348" height="400" rx="18"/></clipPath></defs>
    <g clip-path="url(#pc${i})"><rect width="348" height="400" fill="url(#plateG)"/>${stars(18, 348, 400, 220, .7)}
    <ellipse cx="174" cy="430" rx="260" ry="90" fill="${ROSE}" opacity=".25" filter="url(#blur)"/>${inner}</g>
    <rect x="1.5" y="1.5" width="345" height="397" rx="18" fill="none" stroke="${AMBER}" stroke-width="3" opacity=".7"/>
  </svg>
  <text x="180" y="452" text-anchor="middle" class="cm-cap">${cap[0]}</text><text x="180" y="486" text-anchor="middle" class="cm-cap2">${cap[1]}</text></g>`;
const bubble = (x, y, w, h, txt) => `<path d="M${x} ${y} h${w} a14 14 0 0 1 14 14 v${h} a14 14 0 0 1 -14 14 h-${w - 60} l-26 26 l4 -26 h-34 a14 14 0 0 1 -14 -14 v-${h} a14 14 0 0 1 14 -14 Z" fill="${CREAM}" stroke="${OUT_}" stroke-width="3" stroke-linejoin="round"/>
  <text x="${x + w / 2 + 7}" y="${y + h / 2 + 22}" text-anchor="middle" class="cm-say">${txt}</text>`;
const panel1 = `
  ${bubble(26, 22, 226, 44, 'Setup complete!')}
  <rect x="266" y="120" width="44" height="240" fill="#2A3142" stroke="${CYAN}" stroke-width="2" stroke-opacity=".6"/>
  <circle cx="266" cy="200" r="20" fill="url(#gTeal)"/>
  <circle cx="150" cy="200" r="26" fill="url(#gRed)"/>
  <path d="M40 200 H124" stroke="${RED}" stroke-width="4" filter="url(#glow)" opacity=".8"/>
  <path d="M174 232 Q212 262 258 232" fill="none" stroke="${AMBER}" stroke-width="3" stroke-dasharray="5 6"/>
  <text x="214" y="284" text-anchor="middle" class="cm-small">46 ps late</text>
  ${bust(14, 230, 0.68, 'smug')}`;
const noisy = (() => { let s = ''; for (let x = 36; x <= 312; x += 6) s += `${s ? ' L' : 'M'}${x} ${f1(140 + (rnd() - 0.5) * 50)}`; return s; })();
const panel2 = `
  <rect x="22" y="40" width="304" height="190" rx="22" fill="#08140F" stroke="url(#chr)" stroke-width="8"/>
  <path d="M36 140 H312" stroke="${CYAN}" stroke-opacity=".15"/>
  <path d="${noisy}" fill="none" stroke="#8BF7B0" stroke-width="3" filter="url(#glow)"/>
  <text x="282" y="94" class="cm-q">?</text><text x="250" y="76" class="cm-q s">?</text>
  ${bust(30, 238, 0.68, 'squint')}
  <circle cx="250" cy="310" r="34" fill="#BFEFFF" fill-opacity=".18" stroke="url(#chr)" stroke-width="9"/><path d="M274 334 L306 366" stroke="url(#chr)" stroke-width="13" stroke-linecap="round"/>`;
const panel3 = `
  <path d="M20 360 H330" stroke="${AMBER}" stroke-width="3" opacity=".6"/>
  <rect x="232" y="226" width="62" height="92" rx="6" fill="#0B0A12" stroke="${CYAN}" stroke-width="2" stroke-opacity=".5"/>
  <rect x="256" y="318" width="14" height="42" fill="url(#chr)"/>
  <path d="M226 222 Q263 186 300 222 M238 230 L254 202 M288 230 L272 202 M263 188 V220" fill="none" stroke="#C9C2D6" stroke-width="2" opacity=".7"/>
  <text x="263" y="280" text-anchor="middle" class="cm-block">BLOCK</text>
  ${bust(14, 196, 0.68, 'sleep')}
  <text x="168" y="120" class="cm-z">z</text><text x="192" y="92" class="cm-z s">z</text><text x="210" y="70" class="cm-z s">z</text>`;
const panel4 = `
  <circle cx="250" cy="118" r="66" fill="#140E26" stroke="${RED}" stroke-width="6" filter="url(#glow)"/>
  <path d="M250 118 L250 118 L250 54 A64 64 0 1 1 238 55 Z" fill="${RED}" fill-opacity=".3"/>
  <path d="M250 118 V68 M250 118 L284 132" stroke="${CREAM}" stroke-width="6" stroke-linecap="round"/>
  ${[[60, 80, -18], [124, 46, 14], [44, 160, 22], [140, 120, -8]].map(([x, y, r]) => `<g transform="translate(${x},${y}) rotate(${r})"><rect x="-30" y="-16" width="60" height="32" rx="4" fill="#7FCB8E" stroke="${OUT_}" stroke-width="3"/><text x="0" y="9" text-anchor="middle" class="cm-eur">€</text></g>`).join('')}
  ${bust(70, 228, 0.68, 'worried')}
  <path d="M72 244 q-8 14 0 18 q8 -4 0 -18 Z" fill="#9FE2FF" stroke="${OUT_}" stroke-width="2"/>`;
const comic = `
<svg class="comic-art" viewBox="0 0 1460 500" role="img" aria-label="Four painted panels of the Flash run's failures">
  ${P(0, 1, panel1, ['Spots aligned,', 'pulses 46 ps apart'])}
  ${P(366, 2, panel2, ['Short integration:', 'peak lost in noise'])}
  ${P(732, 3, panel3, ['Never blocked an arm', 'to check backgrounds'])}
  ${P(1098, 4, panel4, ['€4,030 over budget,', '234 of 240 min used'])}
</svg>`;

// ---------- slide 7: the expert's real delay scan ----------
const co = scans[0].points, fi = scans[1].points;
const sx0 = 120, sx1 = 960, sy = c => 520 - (c - 1150) / (2650 - 1150) * 440, cx = x => sx0 + (x - 7.4) / 12 * (sx1 - sx0);
const coarseD = 'M' + co.map(([x, c]) => `${f1(cx(x))} ${f1(sy(c))}`).join(' L');
let ip = 0; co.forEach(([, c], i) => { if (c > co[ip][1]) ip = i; });
const pkx = cx(co[ip][0]), pky = sy(co[ip][1]);
const ix0 = 1080, ix1 = 1520, fx = x => ix0 + (x - 14.053) / (14.137 - 14.053) * (ix1 - ix0), fy = c => 520 - (c - 1350) / (2750 - 1350) * 440;
const fineD = 'M' + fi.map(([x, c]) => `${f1(fx(x))} ${f1(fy(c))}`).join(' L');
let jp = 0; fi.forEach(([, c], i) => { if (c > fi[jp][1]) jp = i; });
const scanSvg = `
<svg class="scan-art" viewBox="0 0 1560 600" role="img" aria-label="The scripted expert's real delay scans on seed 1: a 12 mm coarse scan where one narrow spike rises above the noise, and a fine scan of that spike showing a clean cross-correlation peak">
  <rect x="${sx0}" y="60" width="${sx1 - sx0}" height="460" class="sc-frame"/>
  <path d="${coarseD}" class="sc-coarse"/>
  <circle cx="${f1(pkx)}" cy="${f1(pky)}" r="34" class="sc-ring"/>
  <path d="M${f1(pkx + 30)} ${f1(pky - 16)} L${ix0} 60 M${f1(pkx + 30)} ${f1(pky + 16)} L${ix0} 520" class="sc-zoom"/>
  <rect x="${ix0}" y="60" width="${ix1 - ix0}" height="460" class="sc-frame inset"/>
  <path d="M${f1(fx(fi[jp][0]))} 60 V520" class="sc-t0"/>
  <path d="${fineD}" class="sc-fine"/>
  ${fi.map(([x, c]) => `<circle cx="${f1(fx(x))}" cy="${f1(fy(c))}" r="3.4" class="sc-dot"/>`).join('')}
  <text x="${sx0}" y="560" class="sc-tick">7.4 mm</text><text x="${sx1}" y="560" text-anchor="end" class="sc-tick">19.4 mm</text>
  <text x="${(sx0 + sx1) / 2}" y="560" text-anchor="middle" class="sc-tick">delay stage · 2,401 steps</text>
  <text x="${(ix0 + ix1) / 2}" y="560" text-anchor="middle" class="sc-tick">zoom: 84 µm</text>
  <text x="${ix0 + 16}" y="96" class="sc-t0l">time zero</text>
</svg>`;

// ---------- slide 8: reward components ----------
const B0 = 380, B1 = 1380, bx = r => B0 + r * (B1 - B0);
const bars = [
  { lab: 'Do nothing', seg: [], val: '0.000' },
  { lab: 'Exploit attempts†', seg: [], val: '0.000' },
  { lab: 'Stop early', seg: [['sp', .199]], val: '0.199' },
  { lab: 'Gemini 3.8 Flash*', seg: [['sp', .185]], val: '0.185' },
  { lab: 'Scripted reference', seg: [['sp', .199], ['tm', .498], ['ef', .220]], val: '0.917', b: true },
];
const barSvg = `
<svg class="bar-art" viewBox="0 0 1560 560" role="img" aria-label="Reward split into spatial, timing and efficiency parts: do nothing and exploit attempts score 0, stop early and Flash get only spatial credit, the reference gets all three">
  <g class="lg"><rect x="${B0}" y="0" width="30" height="30" class="seg sp"/><text x="${B0 + 44}" y="25">spatial ≤ 0.2</text>
  <rect x="${B0 + 290}" y="0" width="30" height="30" class="seg tm"/><text x="${B0 + 334}" y="25">timing ≤ 0.5</text>
  <rect x="${B0 + 560}" y="0" width="30" height="30" class="seg ef"/><text x="${B0 + 604}" y="25">efficiency ≤ 0.3, only if η ≥ 0.9</text></g>
  ${bars.map((b, i) => {
    const y = 80 + i * 92; let acc = 0;
    const segs = b.seg.map(([c, w]) => { const r = `<rect x="${f1(bx(acc))}" y="${y}" width="${f1(bx(acc + w) - bx(acc))}" height="60" class="seg ${c}"/>`; acc += w; return r; }).join('');
    return `<g class="br-row" style="--d:${0.2 + i * 0.12}s"><text x="340" y="${y + 41}" text-anchor="end" class="br-lab${b.b ? ' b' : ''}">${b.lab}</text>
      <rect x="${B0}" y="${y}" width="${B1 - B0}" height="60" class="br-track"/>${segs}<path d="M${B0} ${y - 6} V${y + 66}" class="br-zero"/>
      <text x="${B1 + 30}" y="${y + 41}" class="br-val${b.b ? ' b' : ''}">${b.val}</text></g>`;
  }).join('\n  ')}
</svg>`;

// closing strip
const strip = `<svg class="strip" viewBox="0 0 1920 260" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
  <defs><linearGradient id="sG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${ROSE}" stop-opacity="0"/><stop offset="1" stop-color="${ROSE}" stop-opacity=".35"/></linearGradient></defs>
  <rect width="1920" height="260" fill="url(#sG)"/>${skyline(-20, 1940, 260, 40, 200, '#24132F', '#6A3466', true)}</svg>`;

// ---------- slides ----------
const slides = `
  <section class="slide hero" data-video>
    ${hero}
    <div class="band">The GSS Series <span>✦</span> Junction 2026</div>
    <h1>Can AI take <mark>our jobs?</mark></h1>
    <aside class="notes"><b>~6 s.</b> We're experimental physicists. Instead of asking whether AI can take our job, we gave an agent a lab and measured what happened.</aside>
  </section>

  <section class="slide section" data-video>
    <h1>A known design is not a working setup.</h1>
    <p>Knowing pump–probe optics is the beginning. The agent still has to build, align, measure, and recover when its first plan fails.</p>
    <aside class="notes"><b>~10 s.</b> The task tests execution in a physical loop. Manuals and datasheets contain the needed information; success requires decisions under a time budget.</aside>
  </section>

  <section class="slide wall-slide" data-video>
    <h2>Make two laser pulses arrive at the same spot and time.</h2>
    <div class="wall-layout">
      <div class="scene-facts"><strong>≤ 4 hours</strong><span>simulated lab time</span><strong>≤ €30,000</strong><span>parts budget</span></div>
      ${wall}
    </div>
    <aside class="notes"><b>~12 s.</b> An 800 nm pulse and an OPA pulse start on opposite sides of an empty optical table. The agent has to build both beam paths so they focus on the same spot of the sample and arrive within about 100 femtoseconds of each other.</aside>
  </section>

  <section class="slide mcp-slide" data-video>
    <h2>The agent controls a physics lab through MCP.</h2>
    ${mindmap}
    <aside class="notes"><b>~13 s.</b> About twenty tools in six groups. Reading manuals is free; anything physical costs simulated lab time. The agent only sees instrument readings, never the simulator's true state.</aside>
  </section>

  <section class="slide ridge-slide" data-video>
    <h2>The agent scored below our stop-early baseline.</h2>
    ${ridgeSvg}
    <p class="muted fig-note">Reward over seeds 1–10, Level 1; each ridge is scaled to the same height. *One saved Flash run, rescored under the current rubric.</p>
    <!-- PLACEHOLDER rows [Model A]/[Model B]: add per-seed rewards to L1 in build4.js and rebuild -->
    <aside class="notes"><b>~15 s.</b> Each ridge is how a policy scores across seeds. Doing nothing sits at zero, stopping after spatial alignment at 0.2, and the scripted reference at 0.92 on every seed. Flash spent the whole budget and landed just below stop-early. [Add one sentence on the new frontier runs.]</aside>
  </section>

  <section class="slide comic-slide" data-video>
    <h2>It aligned the spots. It never verified the timing.</h2>
    ${comic}
    <aside class="notes"><b>~16 s.</b> Flash reported “The alignment and time-zero setup has been completed and submitted”, while the pulses were 46 picoseconds apart. It scanned with a short integration time, so the peak drowned in noise; it never blocked one arm to check the backgrounds; and it overspent by €4,030 and used 234 of 240 minutes. Each failure is a decision, and the manuals describe the tools that avoid it.</aside>
  </section>

  <section class="slide scan-slide" data-video>
    <h2>Time zero is findable: our scripted expert finds it every time.</h2>
    ${scanSvg}
    <p class="muted fig-note">The expert's real scans on seed 1, using only the agent's tools. It solves 10 of 10 seeds at both levels.</p>
    <aside class="notes"><b>~14 s.</b> Is a zero just unfair? No. This is the scripted expert's real delay scan with the same tools: a 12 mm coarse scan where one narrow spike stands out of the noise, then a fine scan of it. It succeeds on every seed at both levels, with the OPA wavelength randomised per seed.</aside>
  </section>

  <section class="slide bar-slide" data-video>
    <h2>No shortcut beats real play.</h2>
    ${barSvg}
    <p class="muted fig-note">†Absurd arguments, 100,000 mirrors, status-call spam and calls to the verifier without its token, all in the test suite. Grader and simulator run outside the agent's container.</p>
    <aside class="notes"><b>~12 s.</b> The reward has three parts, all computed from the simulator's true final state. Doing nothing or trying the exploits scores zero; spatial alignment alone gets at most 0.2; only a working setup unlocks timing and efficiency. [Update if the stop-early credit changes in the reward code.]</aside>
  </section>

  <section class="slide craft-slide" data-video>
    <h2>One command to check us.</h2>
    <pre class="code"><span class="k">harbor</span> run -p . -a oracle               <span class="c"># reference</span>
<span class="k">harbor</span> run -p . -a opencode -m <span class="s">&lt;model&gt;</span>  <span class="c"># any agent</span></pre>
    <p class="muted craft-note">Fixed seeds · 77 tests · baselines regenerate docs/results.md</p>
    <aside class="notes"><b>~6 s.</b> One Harbor command runs the reference or any agent; seeds are fixed, so every number in this deck reproduces.</aside>
  </section>

  <section class="slide closing" data-video>
    ${strip}
    <h2>Can an agent build a working experiment?</h2>
    <p class="closing-line">GSS measures the gap between knowing the physics and making it work.</p>
    <p class="muted" style="margin-top:58px">Source and setup: github.com/kakitkelvinho/gss</p>
    <aside class="notes"><b>~6 s.</b> Run your own agent and see if it finds time zero.</aside>
  </section>
`;
const backupTitles = ['Why the difficulty is meaningful', 'What the current score measures', 'Evidence still to collect'];
const backups = [...src.matchAll(/  <section class="slide[^"]*"[^>]*>[\s\S]*?<\/section>\n/g)].map(m => m[0])
  .filter(s => backupTitles.some(t => s.includes(t))).join('\n');

// starfield tile for slide backgrounds
SEED = 5;
const tile = `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='420'>${Array.from({ length: 46 }, () =>
  `<circle cx='${f1(rnd() * 640)}' cy='${f1(rnd() * 420)}' r='${f1(0.6 + rnd() * 1.3)}' fill='white' opacity='${f1(0.15 + rnd() * 0.5)}'/>`).join('')}</svg>`;
const STARS = `url("data:image/svg+xml,${encodeURIComponent(tile)}")`;

const css = `
  /* ===== v4: retrofuturist paperback, dark-first ===== */
  :root { --bg:#F2E8D5; --fg:#1E1828; --muted:#6A5F70; --accent:#C46A1C; --ring:#1E1828; --line:#CDBFA6;
    --sp:#2E8C95; --tm:#C8475E; --ef:#D98A1E; }
  :root[data-theme="dark"] { --bg:#120E22; --fg:#F3E9D7; --muted:#A79DB8; --accent:${AMBER}; --ring:${AMBER}; --line:#3A2F52;
    --sp:${CYAN}; --tm:${ROSE}; --ef:${AMBER}; }
  html, body { background:#07050F; }
  .slide { background:radial-gradient(ellipse 120% 90% at 50% 40%, #F7F0E2 0%, #E7D8BC 100%); }
  :root[data-theme="dark"] .slide { background-image:${STARS}, radial-gradient(ellipse 80% 45% at 50% 112%, rgba(232,99,122,.45), rgba(232,99,122,0) 70%), linear-gradient(180deg, #0D0A1C 0%, #171030 60%, #25163C 100%);
    background-size:640px 420px, 100% 100%, 100% 100%; }
  .slide h1, .slide h2 { font-family:"Playfair Display", Georgia, serif; font-weight:800; letter-spacing:-.005em; }
  .slide h2 { font-size:74px; line-height:1.12; }
  .slide mark { background:none !important; color:var(--accent); padding:0; animation:none !important; }
  .wordmark { font-family:Cinzel, Georgia, serif; letter-spacing:.08em; font-weight:700; }
  .slide pre.code { border:2px solid rgba(242,169,59,.45); background:#120E1E; }
  .section h1 { font-size:128px; max-width:1300px; }
  .hero { padding:70px 130px 150px; justify-content:flex-start; align-items:center; background:#0B0820 !important; }
  .hero-bg { position:absolute; inset:0; width:100%; height:100%; z-index:0; animation:none !important; }
  .hero > :not(.hero-bg):not(aside) { position:relative; z-index:1; }
  .band { font-family:Cinzel, Georgia, serif; font-weight:700; font-size:30px; letter-spacing:.32em; text-transform:uppercase; color:${AMBER};
    display:flex; align-items:center; gap:30px; width:1200px; margin-top:20px; }
  .band::before, .band::after { content:""; flex:1; height:2px; background:currentColor; opacity:.7; }
  .band span { letter-spacing:0; }
  .hero h1 { font-size:150px; color:#F7E6C4; text-align:center; margin-top:14px; text-shadow:0 6px 0 rgba(0,0,0,.35), 0 0 40px rgba(232,99,122,.35); }
  .hero h1 mark { color:${AMBER} !important; }
  .stage:has(.hero.active) .foot { display:none; }
  @keyframes bob { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-10px); } }
  @keyframes run { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-16px); } }
  .slide.active .chase-bot { animation:bob .55s ease-in-out infinite; }
  .slide.active .chase-sci { animation:run .32s ease-in-out infinite; }
  .wall-slide { padding:96px 160px 150px; } .wall-slide h2 { margin-bottom:24px; }
  .wall-slide .scene-facts { grid-template-columns:1fr; gap:4px; } .wall-slide .scene-facts span { margin-bottom:34px; }
  .scene-facts strong { font-family:"Playfair Display", Georgia, serif; font-size:52px; color:var(--accent); }
  .wall-layout { display:grid; grid-template-columns:360px 1fr; gap:40px; align-items:center; flex:1; min-height:0; }
  .wall-art { width:100%; max-height:700px; }
  @keyframes pRed  { 0%,8% { transform:translate(0,0) scale(1.5); opacity:0; } 14% { opacity:1; } 52% { transform:translate(570px,-325px) scale(.28); opacity:1; } 56%,100% { transform:translate(570px,-325px) scale(.28); opacity:0; } }
  @keyframes pTeal { 0%,8% { transform:translate(0,0) scale(1.5); opacity:0; } 14% { opacity:1; } 52% { transform:translate(-480px,-305px) scale(.28); opacity:1; } 56%,100% { transform:translate(-480px,-305px) scale(.28); opacity:0; } }
  @keyframes hit { 0%,48% { opacity:0; transform:scale(.2); } 53% { opacity:1; transform:scale(1); } 78%,100% { opacity:0; transform:scale(1.6); } }
  .p-red, .p-teal, .hit { transform-box:fill-box; transform-origin:center; }
  .slide.active .p-red { animation:pRed 3.4s cubic-bezier(.4,0,.7,1) infinite; }
  .slide.active .p-teal { animation:pTeal 3.4s cubic-bezier(.4,0,.7,1) infinite; }
  .slide.active .hit { animation:hit 3.4s ease-out infinite; }
  .mcp-slide h2, .ridge-slide h2, .comic-slide h2, .scan-slide h2, .bar-slide h2 { margin-bottom:28px; }
  .mcp-art, .ridge-art, .comic-art, .scan-art, .bar-art { width:100%; flex:1; min-height:0; }
  .mm-title { font:700 32px Cinzel, Georgia, serif; fill:${CREAM}; letter-spacing:.04em; }
  .mm-tool { font:22px Consolas,"SF Mono",Menlo,monospace; fill:#B9AFCB; }
  .mm-node, .rl-row, .br-row { opacity:0; }
  .slide.active .mm-node, .slide.active .rl-row, .slide.active .br-row { animation:fade .45s var(--d) both; }
  .rl-lab, .br-lab { font:36px Inter,Arial,sans-serif; fill:var(--fg); }
  .rl-lab.b, .rl-val.b, .br-lab.b, .br-val.b { font-weight:700; }
  .rl-val, .br-val { font:700 36px Inter,Arial,sans-serif; fill:var(--fg); font-variant-numeric:tabular-nums; }
  .rl-n { font:24px Inter,Arial,sans-serif; fill:var(--muted); }
  .rl-fill { fill:var(--bg); fill-opacity:.92; } .rl-fill.ref { fill:var(--accent); fill-opacity:1; }
  .rl-line { fill:none; stroke:var(--fg); stroke-width:3.5; stroke-linejoin:round; } .rl-line.one { stroke-dasharray:10 8; }
  .rl-line.ref { filter:url(#glow); }
  .rl-ph { stroke:var(--muted); stroke-width:3; stroke-dasharray:10 10; }
  .ph-t { fill:#ff5a4e; }
  .rl-axis { stroke:var(--fg); stroke-width:3; } .rl-tick { font:28px Inter,Arial,sans-serif; fill:var(--muted); }
  .fig-note { font-size:26px !important; margin-top:8px; }
  .cm-cap { font:700 30px "Playfair Display",Georgia,serif; fill:var(--fg); } .cm-cap2 { font:28px Inter,Arial,sans-serif; fill:var(--muted); }
  .cm-say { font:700 26px "Playfair Display",Georgia,serif; fill:${OUT_}; } .cm-small { font:700 22px Inter,Arial,sans-serif; fill:${AMBER}; }
  .cm-q { font:700 64px "Playfair Display",Georgia,serif; fill:${AMBER}; } .cm-q.s { font-size:44px; }
  .cm-z { font:700 40px "Playfair Display",Georgia,serif; fill:${CYAN}; } .cm-z.s { font-size:28px; }
  .cm-block { font:700 15px Cinzel,Georgia,serif; fill:${CREAM}; letter-spacing:.06em; } .cm-eur { font:700 22px Inter,Arial,sans-serif; fill:${OUT_}; }
  .sc-frame { fill:none; stroke:var(--line); stroke-width:3; } .sc-frame.inset { stroke:var(--accent); }
  .sc-coarse { fill:none; stroke:var(--fg); stroke-width:1.3; stroke-linejoin:round; opacity:.85; }
  .sc-fine { fill:none; stroke:var(--fg); stroke-width:3; stroke-linejoin:round; } .sc-dot { fill:var(--fg); }
  .sc-ring { fill:none; stroke:var(--tm); stroke-width:5; } .sc-zoom { stroke:var(--muted); stroke-width:2; stroke-dasharray:8 8; fill:none; }
  .sc-t0 { stroke:var(--accent); stroke-width:14; stroke-opacity:.35; } .sc-t0l { font:700 28px Cinzel,Georgia,serif; fill:var(--fg); }
  .sc-tick { font:26px Inter,Arial,sans-serif; fill:var(--muted); }
  .lg text { font:28px Inter,Arial,sans-serif; fill:var(--fg); }
  .br-track { fill:var(--line); fill-opacity:.6; } .br-zero { stroke:var(--fg); stroke-width:4; }
  .seg.sp { fill:var(--sp); } .seg.tm { fill:var(--tm); } .seg.ef { fill:var(--ef); }
  .craft-slide { justify-content:center; } .craft-slide pre.code { font-size:40px; }
  .craft-note { margin-top:40px; font-size:34px !important; }
  .closing { justify-content:center; } .closing .closing-line { font-family:"Playfair Display",Georgia,serif; font-style:italic; }
  .strip { position:absolute; left:0; right:0; bottom:0; width:100%; height:260px; z-index:0; animation:none !important; opacity:.9; }
  .closing > :not(.strip):not(aside) { position:relative; z-index:1; }
  @media print {
    :root, :root[data-theme="dark"] { --bg:#F2E8D5; --fg:#1E1828; --muted:#6A5F70; --accent:#C46A1C; --ring:#1E1828; --line:#CDBFA6; --sp:#2E8C95; --tm:#C8475E; --ef:#D98A1E; }
    .slide, :root[data-theme="dark"] .slide { background:#F2E8D5 !important; }
    .hero { background:#0B0820 !important; }
  }
  @media print, (prefers-reduced-motion:reduce) {
    .mm-node, .rl-row, .br-row { opacity:1 !important; }
    .p-red { transform:translate(570px,-325px) scale(.28) !important; opacity:1 !important; }
    .p-teal { transform:translate(-480px,-305px) scale(.28) !important; opacity:1 !important; }
    .hit { opacity:.9 !important; transform:none !important; }
  }
`;

let head = src.slice(0, src.indexOf('<div class="stage" id="stage">'))
  .replace('</style>', css + '</style>')
  .replace(/<title>.*?<\/title>/, '<title>GSS · Find Time Zero (v4)</title>')
  .replace(/<link href="https:\/\/fonts\.googleapis\.com[^>]+>/, '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=Cinzel:wght@600;700&display=swap" rel="stylesheet">')
  .replace('<body>', '<body>' + defs)
  .replace('  .slide.active svg g { animation:fade .4s 1.6s both; }\n', '');
let tail = src.slice(src.indexOf('  <div class="foot">'))
  .replace(/'pitch-theme'/g, "'pitch-theme-v4'")
  .replace(/setTheme\(saved \|\| \([^;]*\);/, "setTheme(saved || 'dark');");
fs.writeFileSync(OUT, head + '<div class="stage" id="stage">\n' + slides + '\n' + backups + '\n' + tail);
console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
console.log('theme default patched:', tail.includes("setTheme(saved || 'dark')"));
