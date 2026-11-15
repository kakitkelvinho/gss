// v5 = v4 with slides 1-2 redone as Saul Bass-style screen-print posters.
const fs = require('fs');
const IN = __dirname + '/out/pitch-deck-v4.html', OUT = __dirname + '/out/pitch-deck-v5.html';
let html = fs.readFileSync(IN, 'utf8');
const f1 = x => Math.round(x * 10) / 10;
const BLUE = '#2E6F9E', ORANGE = '#E8742A', CREAM = '#EDE3CC', INK = '#16120F';

const filters = `
  <filter id="cut" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="7"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="9" result="n"/>
    <feColorMatrix type="matrix" values="0 0 0 0 .08  0 0 0 0 .06  0 0 0 0 .05  0 0 0 -1.6 1.05"/></filter>
  <filter id="wear" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="3" seed="2"/>
    <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 .97  0 0 0 0 .9  0 0 0 -2.2 1.25"/></filter>`;
const texture = (op = .5) => `<rect width="1920" height="1080" filter="url(#grain)" opacity="${op}"/><rect width="1920" height="1080" filter="url(#wear)" opacity=".1"/>`;

// ---- silhouettes (black cut paper) ----
const rot = ([x, y], [cx, cy], d) => { const a = d * Math.PI / 180, dx = x - cx, dy = y - cy; return [cx + dx * Math.cos(a) - dy * Math.sin(a), cy + dx * Math.sin(a) + dy * Math.cos(a)]; };
const pl = p => 'M' + p.map(q => `${f1(q[0])} ${f1(q[1])}`).join(' L');
const limb = (p, w) => `<path d="${pl(p)}" stroke="${INK}" stroke-width="${w}" fill="none" stroke-linejoin="miter" stroke-linecap="square"/>`;
function robot() {
  const pv = [0, -205], R = p => rot(p, pv, 12);
  const SF = R([52, -322]), SB = R([-52, -322]), HF = R([18, -205]), HB = R([-18, -205]);
  return `<g fill="${INK}">
    ${limb([SB, [-72, -282], [-98, -222]], 24)}${limb([HB, [-48, -112], [-126, -72], [-146, -42]], 30)}
    <g transform="rotate(12 0 -205)">
      <path d="M-40 -190 L40 -190 L32 -232 L-32 -232 Z"/><rect x="-26" y="-266" width="52" height="40"/>
      <path d="M-64 -344 L64 -344 L48 -260 L-48 -260 Z"/><rect x="-12" y="-366" width="24" height="26"/>
      <path d="M-40 -360 L-44 -416 L-22 -436 L22 -436 L44 -416 L40 -360 Z"/>
      <path d="M-30 -404 L30 -404 L28 -388 L-28 -388 Z" fill="${ORANGE}"/>
      <path d="M0 -436 V-462" stroke="${INK}" stroke-width="6"/><rect x="-7" y="-472" width="14" height="14" fill="${ORANGE}"/>
      <circle cx="0" cy="-302" r="13" fill="${CREAM}"/>
    </g>
    ${limb([HF, [86, -126], [72, -20], [124, -8]], 32)}
    ${limb([SF, [150, -298], [214, -330]], 26)}
    ${limb([[214, -330], [246, -350]], 9)}${limb([[214, -330], [252, -330]], 9)}${limb([[214, -330], [244, -308]], 9)}
  </g>`;
}
// scientist: same pose as before, angular black paper; goggles cut out in cream
const scientist = `<g transform="rotate(9 1050 505)" fill="${INK}">
  ${limb([[1040, 400], [1000, 440], [955, 425], [930, 410]], 26)}
  ${limb([[1052, 400], [1092, 445], [1082, 495], [1112, 503]], 26)}
  ${limb([[1022, 302], [985, 282], [972, 226]], 24)}<path d="M962 222 L968 196 L978 200 L984 190 L990 222 Z"/>
  <path d="M1012 288 L1088 288 L1106 418 L1022 420 L976 436 L996 404 L970 410 Z"/>
  ${limb([[1078, 302], [1122, 268], [1138, 210]], 24)}<path d="M1128 206 L1134 180 L1144 186 L1152 176 L1156 210 Z"/>
  <path d="M1012 236 L1018 196 L1033 220 L1043 184 L1056 212 L1069 186 L1075 216 L1094 200 L1090 244 L1092 268 L1072 290 L1030 288 L1010 262 Z"/>
  <path d="M1020 240 L1092 240 L1090 260 L1020 262 Z" fill="${CREAM}"/>
  <path d="M1030 244 L1046 244" stroke="${INK}" stroke-width="3"/>
</g>`;

// ---- slide 1 poster ----
const poster1 = `
<svg class="poster-art" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <defs>${filters}</defs>
  <rect width="1920" height="1080" fill="${BLUE}"/>
  <g filter="url(#cut)">
    <circle cx="1210" cy="430" r="330" fill="${CREAM}"/>
    <path d="M-40 870 L1210 430 L1240 470 L-40 960 Z" fill="${ORANGE}"/>
    <path d="M1960 120 L1210 430 L1230 452 L1960 168 Z" fill="${CREAM}"/>
    <path d="M1210 430 L1960 330 L1960 352 Z" fill="${ORANGE}" opacity=".9"/>
    <path d="M120 300 L300 300 M90 360 L330 360 M140 420 L280 420" stroke="${CREAM}" stroke-width="12" opacity=".85"/>
  </g>
  <g filter="url(#cut)">
    <g transform="translate(610,800) scale(1.05)">${robot()}</g>
    <g transform="translate(-160,90) scale(1.32)">${scientist}</g>
  </g>
  <g class="pt" filter="url(#cut)">
    <text x="110" y="128" class="pt-kicker">GSS · Junction 2026</text>
    <text x="110" y="176" class="pt-small">An experiment in letting</text>
    <text x="110" y="212" class="pt-small">the agent run the lab</text>
    <text x="960" y="1030" text-anchor="middle" class="pt-title" textLength="1740" lengthAdjust="spacingAndGlyphs">CAN AI TAKE OUR JOBS?</text>
  </g>
  ${texture()}
</svg>`;

// ---- slide 2 poster: the clean schematic, torn ----
const schematic = `
  <rect x="0" y="0" width="980" height="440" fill="${BLUE}"/>
  <g stroke="${CREAM}" stroke-width="2" opacity=".25">${Array.from({ length: 24 }, (_, i) => `<path d="M${i * 42} 0 V440"/>`).join('')}${Array.from({ length: 11 }, (_, i) => `<path d="M0 ${i * 42} H980"/>`).join('')}</g>
  <g fill="none" stroke="${CREAM}" stroke-width="5">
    <rect x="40" y="60" width="140" height="70"/><rect x="40" y="300" width="140" height="70"/>
    <path d="M180 95 H420 V250 H560 V95 H660 L740 200 L860 215"/>
    <path d="M180 335 H760 L860 230"/>
    <path d="M420 250 H560" stroke-dasharray="14 10"/>
  </g>
  <g stroke="${ORANGE}" stroke-width="12" stroke-linecap="square">
    <path d="M405 80 L435 110"/><path d="M405 235 L435 265"/><path d="M545 235 L575 265"/><path d="M545 80 L575 110"/><path d="M745 320 L775 350"/>
  </g>
  <path d="M732 170 Q760 200 732 232" stroke="${CREAM}" stroke-width="8" fill="none"/>
  <rect x="860" y="170" width="26" height="110" fill="${CREAM}"/>
  <circle cx="860" cy="222" r="11" fill="${ORANGE}"/>`;
const tear = 'M470 -10 L492 40 L462 92 L500 150 L470 210 L508 262 L476 318 L502 372 L480 450';
const poster2 = `
<svg class="poster-art" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
  <defs>${filters}
    <clipPath id="tl"><path d="M-10 -10 ${tear.replace('M', 'L')} L-10 450 Z"/></clipPath>
    <clipPath id="tr"><path d="${tear} L990 450 L990 -10 Z"/></clipPath></defs>
  <rect width="1920" height="1080" fill="${CREAM}"/>
  <g filter="url(#cut)">
    <circle cx="1560" cy="300" r="220" fill="${ORANGE}"/>
    <g transform="translate(80,40) scale(.82)">
    <g transform="translate(250,250) rotate(-3)">
      <rect x="12" y="16" width="${470}" height="440" fill="${INK}" opacity=".9" clip-path="url(#tl)"/>
      <g clip-path="url(#tl)">${schematic}</g>
    </g>
    <g transform="translate(330,330) rotate(9 480 220)">
      <rect x="12" y="16" width="980" height="440" fill="${INK}" opacity=".9" clip-path="url(#tr)"/>
      <g clip-path="url(#tr)">${schematic}</g>
    </g>
    <path d="M770 690 L812 660 L800 712 Z M846 724 L880 712 L866 748 Z M720 742 L748 728 L744 760 Z" fill="${INK}"/>
    <path d="M800 640 L830 628 L822 656 Z M900 680 L930 690 L908 708 Z" fill="${ORANGE}"/>
    </g>
  </g>
  <g class="pt" filter="url(#cut)">
    <text x="110" y="118" class="pt-small dk">Knowing pump–probe optics is the beginning.</text>
    <text x="110" y="156" class="pt-small dk">The agent still has to build, align, measure</text>
    <text x="110" y="194" class="pt-small dk">and recover when its first plan fails.</text>
    <text x="110" y="905" class="pt-title2" textLength="1700" lengthAdjust="spacingAndGlyphs">A KNOWN DESIGN IS</text>
    <text x="110" y="1040" class="pt-title2 or" textLength="1700" lengthAdjust="spacingAndGlyphs">NOT A WORKING SETUP.</text>
  </g>
  ${texture(.45)}
</svg>`;

const s1 = `  <section class="slide poster" data-video>
    ${poster1}
    <h1 class="sr">Can AI take our jobs?</h1>
    <aside class="notes"><b>~6 s.</b> We're experimental physicists. Instead of asking whether AI can take our job, we gave an agent a lab and measured what happened.</aside>
  </section>
`;
const s2 = `  <section class="slide poster" data-video>
    ${poster2}
    <h1 class="sr">A known design is not a working setup.</h1>
    <aside class="notes"><b>~10 s.</b> The task tests execution in a physical loop. Manuals and datasheets contain the needed information; success requires decisions under a time budget.</aside>
  </section>
`;
const secs = [...html.matchAll(/  <section class="slide[^"]*"[^>]*>[\s\S]*?<\/section>\n/g)];
html = html.slice(0, secs[0].index) + s1 + '\n' + s2 + html.slice(secs[1].index + secs[1][0].length);

const css = `
  /* ===== v5: screen-print posters ===== */
  .poster { padding:0 !important; background:${BLUE} !important; }
  .poster-art { position:absolute; inset:0; width:100%; height:100%; animation:none !important; }
  .poster .sr { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
  .stage:has(.poster.active) .foot { display:none; }
  .pt-kicker { font:400 64px "Bebas Neue", Oswald, Impact, sans-serif; fill:${INK}; letter-spacing:.04em; }
  .pt-small { font:500 34px Oswald, "Bebas Neue", Impact, sans-serif; fill:${INK}; letter-spacing:.06em; text-transform:uppercase; }
  .pt-title { font:400 250px "Bebas Neue", Impact, sans-serif; fill:${INK}; }
  .pt-title2 { font:400 170px "Bebas Neue", Impact, sans-serif; fill:${INK}; }
  .pt-title2.or { fill:${ORANGE}; }
  @keyframes inkIn { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:none; } }
  .slide.active .poster-art .pt { animation:inkIn .6s .2s both; }
  @media print { .poster { background:${BLUE} !important; } }
`;
html = html.replace('</style>', css + '</style>')
  .replace('family=Cinzel:wght@600;700', 'family=Cinzel:wght@600;700&family=Bebas+Neue&family=Oswald:wght@500')
  .replace(/<title>.*?<\/title>/, '<title>GSS · Find Time Zero (v5)</title>');
fs.writeFileSync(OUT, html);
console.log('wrote', OUT, fs.statSync(OUT).size);
