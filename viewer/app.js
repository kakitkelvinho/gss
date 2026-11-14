(function () {
  "use strict";

  const bundle = window.GSS_RUNS_BUNDLE || { runs: [] };
  const runs = Array.isArray(bundle.runs) ? bundle.runs : [];

  const elRunSelect = document.getElementById("runSelect");
  const elPrevBtn = document.getElementById("prevBtn");
  const elNextBtn = document.getElementById("nextBtn");
  const elSlider = document.getElementById("stepSlider");
  const elStepLabel = document.getElementById("stepLabel");
  const elLeg800 = document.getElementById("leg800");
  const elLegOpa = document.getElementById("legOpa");
  const elCursor = document.getElementById("cursorReadout");
  const elFitBtn = document.getElementById("fitBtn");
  const elCanvas = document.getElementById("tableCanvas");
  const elTooltip = document.getElementById("partTooltip");
  const elCallTime = document.getElementById("callTime");
  const elCallBody = document.getElementById("callBody");
  const elEndedBadge = document.getElementById("endedBadge");
  const elDiagMetrics = document.getElementById("diagMetrics");
  const elDiagMeta = document.getElementById("diagMeta");
  const elDiagTags = document.getElementById("diagTags");

  const ctx = elCanvas.getContext("2d");

  const state = {
    runIdx: 0,
    stepPos: 0, // 0 = empty table before any tool call; 1..N = trajectory[stepPos - 1]
    cam: { scale: 0.3, panX: 0, panY: 0, fitted: false },
    drag: null,
    hoverPart: null,
  };

  // World bounds including desk at (-300, 600) and 2400 x 1200 mm table
  const WORLD = { minX: -390, maxX: 2510, minZ: -110, maxZ: 1310 };

  function fmtClock(sec) {
    const s = Math.max(0, Math.round(Number(sec) || 0));
    const hh = String(Math.floor(s / 3600)).padStart(2, "0");
    const mm = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
    const ss = String(s % 60).padStart(2, "0");
    return `${hh}:${mm}:${ss}`;
  }

  function fmtDt(fs) {
    if (fs === null || fs === undefined || Number.isNaN(Number(fs))) return "—";
    const v = Number(fs);
    const a = Math.abs(v);
    if (a >= 10000) return `${(v / 1000).toFixed(2)} ps`;
    if (a >= 100) return `${v.toFixed(0)} fs`;
    return `${v.toFixed(1)} fs`;
  }

  function esc(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function currentRun() {
    return runs[state.runIdx] || null;
  }

  function currentStep() {
    const run = currentRun();
    if (!run || state.stepPos <= 0) return null;
    return run.trajectory[state.stepPos - 1] || null;
  }

  // ---------------------------------------------------------------------------
  // Camera & Coordinate Transforms (World mm -> Screen px)
  // ---------------------------------------------------------------------------

  function fitCamera() {
    const rect = elCanvas.getBoundingClientRect();
    const w = Math.max(100, rect.width);
    const h = Math.max(100, rect.height);
    const pad = 26;
    const spanX = WORLD.maxX - WORLD.minX;
    const spanZ = WORLD.maxZ - WORLD.minZ;
    const scale = Math.min((w - pad * 2) / spanX, (h - pad * 2) / spanZ);
    state.cam.scale = scale;
    state.cam.panX = (w - spanX * scale) * 0.5 - WORLD.minX * scale;
    state.cam.panY = (h - spanZ * scale) * 0.5 - WORLD.minZ * scale;
    state.cam.fitted = true;
  }

  function w2s(x, z) {
    return [x * state.cam.scale + state.cam.panX, z * state.cam.scale + state.cam.panY];
  }

  function s2w(px, py) {
    return [(px - state.cam.panX) / state.cam.scale, (py - state.cam.panY) / state.cam.scale];
  }

  function resizeCanvas() {
    const rect = elCanvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = Math.max(1, Math.floor(rect.width * dpr));
    const h = Math.max(1, Math.floor(rect.height * dpr));
    if (elCanvas.width !== w || elCanvas.height !== h) {
      elCanvas.width = w;
      elCanvas.height = h;
    }
    if (!state.cam.fitted) fitCamera();
    drawTable();
  }

  // ---------------------------------------------------------------------------
  // Top-Down Optical Table Renderer
  // ---------------------------------------------------------------------------

  function drawArrowhead(x0, y0, x1, y1, color) {
    const dx = x1 - x0;
    const dy = y1 - y0;
    const len = Math.hypot(dx, dy);
    if (len < 28) return;
    const mx = x0 + dx * 0.56;
    const my = y0 + dy * 0.56;
    const ux = dx / len;
    const uy = dy / len;
    const sz = 5.5;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(mx + ux * sz, my + uy * sz);
    ctx.lineTo(mx - ux * sz - uy * sz * 0.65, my - uy * sz + ux * sz * 0.65);
    ctx.lineTo(mx - ux * sz + uy * sz * 0.65, my - uy * sz - ux * sz * 0.65);
    ctx.closePath();
    ctx.fill();
  }

  function drawPart(part, isHovered) {
    const s = state.cam.scale;
    const [cx, cy] = w2s(part.pos.x, part.pos.z);
    const yawRad = ((part.eff_yaw_deg ?? part.yaw_deg ?? 0) * Math.PI) / 180;

    ctx.save();

    if (part.kind === "mirror") {
      // Mirror normal points along (cos(yaw), sin(yaw)); backing mount sits on -normal side
      ctx.translate(cx, cy);
      ctx.rotate(yawRad);

      const mountHalfW = Math.max(7, 19 * s);
      const mountDepth = Math.max(5, 18 * s);
      const faceHalfW = Math.max(5.5, 12.7 * s);

      // 38 mm kinematic backing mount (-X in local frame)
      ctx.fillStyle = "#334155";
      ctx.strokeStyle = isHovered ? "#f05a28" : "#0f172a";
      ctx.lineWidth = isHovered ? 2 : 1.2;
      ctx.fillRect(-mountDepth, -mountHalfW, mountDepth, mountHalfW * 2);
      ctx.strokeRect(-mountDepth, -mountHalfW, mountDepth, mountHalfW * 2);

      // 25.4 mm reflective front face at local x = 0
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(0, -faceHalfW);
      ctx.lineTo(0, faceHalfW);
      ctx.stroke();

      // Subtle front-normal tick (+X in local frame)
      ctx.strokeStyle = "#64748b";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.max(5, 10 * s), 0);
      ctx.stroke();
    } else if (part.kind === "periscope") {
      ctx.translate(cx, cy);
      ctx.rotate(yawRad);
      const r = Math.max(6, 15 * s);
      ctx.fillStyle = "#dbeafe";
      ctx.strokeStyle = isHovered ? "#f05a28" : "#1e293b";
      ctx.lineWidth = isHovered ? 2 : 1.4;
      ctx.fillRect(-r, -r, r * 2, r * 2);
      ctx.strokeRect(-r, -r, r * 2, r * 2);
      ctx.beginPath();
      ctx.arc(0, 0, Math.max(3, 6 * s), 0, Math.PI * 2);
      ctx.fillStyle = "#1e293b";
      ctx.fill();
    } else if (part.kind === "stage") {
      // Rail along u = (cos(yaw), sin(yaw)); apex at 90 + stage_pos_mm, front face at apex - 50 mm
      const railYaw = ((part.yaw_deg ?? 0) * Math.PI) / 180;
      ctx.translate(cx, cy);
      ctx.rotate(railYaw);

      const stagePos = Number(part.stage_pos_mm || 0);
      const apexDist = (90 + stagePos) * s;
      const frontDist = (90 + stagePos - 50) * s;
      const retroHalfW = Math.max(7, 25.4 * s);
      const railLen = Math.max(24, 125 * s);
      const railHalfW = Math.max(6, 20 * s);

      // Stage base rail
      ctx.fillStyle = "#e2e8f0";
      ctx.strokeStyle = isHovered ? "#f05a28" : "#334155";
      ctx.lineWidth = isHovered ? 2 : 1.2;
      ctx.fillRect(-10 * s, -railHalfW, railLen, railHalfW * 2);
      ctx.strokeRect(-10 * s, -railHalfW, railLen, railHalfW * 2);

      // Gold hollow retroreflector carriage
      ctx.fillStyle = "#fef3c7";
      ctx.strokeStyle = "#b45309";
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.moveTo(frontDist, -retroHalfW);
      ctx.lineTo(apexDist, 0);
      ctx.lineTo(frontDist, retroHalfW);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    } else if (part.kind === "sample") {
      // Draw focusing lens(es) + sample plane
      const lenses = Array.isArray(part.lenses) ? part.lenses : [];
      for (const ln of lenses) {
        const [lx, ly] = w2s(ln.center.x, ln.center.z);
        const lYaw = ((ln.yaw_deg ?? 0) * Math.PI) / 180;
        const mountR = Math.max(7, (ln.mount_radius_mm || 25.4) * s);
        const clearR = Math.max(4.5, (ln.radius_mm || 12.7) * s);

        ctx.save();
        ctx.translate(lx, ly);
        ctx.rotate(lYaw);
        // Outer lens mount tube (blocks rays hitting 12.7..25.4 mm)
        ctx.strokeStyle = "#1e293b";
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(0, -mountR);
        ctx.lineTo(0, mountR);
        ctx.stroke();
        // Clear 25.4 mm lens aperture
        ctx.strokeStyle = "#06b6d4";
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(0, -clearR);
        ctx.lineTo(0, clearR);
        ctx.stroke();
        ctx.restore();
      }

      // Sample / nonlinear crystal focal point
      const sp = lenses[0] && lenses[0].sample_pos ? lenses[0].sample_pos : part.pos;
      const [sx, sy] = w2s(sp.x, sp.z);
      const sr = Math.max(5, 11 * s);
      ctx.fillStyle = "#ede9fe";
      ctx.strokeStyle = isHovered ? "#f05a28" : "#6d28d9";
      ctx.lineWidth = isHovered ? 2.2 : 1.6;
      ctx.fillRect(sx - sr * 0.55, sy - sr, sr * 1.1, sr * 2);
      ctx.strokeRect(sx - sr * 0.55, sy - sr, sr * 1.1, sr * 2);
    }

    ctx.restore();

    // Crisp part ID label
    ctx.save();
    ctx.font = '600 10.5px ui-monospace, "SFMono-Regular", Menlo, monospace';
    ctx.fillStyle = isHovered ? "#c2410c" : "#1e293b";
    ctx.textAlign = "center";
    const labelOffsetY = Math.max(13, 28 * s);
    ctx.fillText(part.id, cx, cy - labelOffsetY);
    ctx.restore();
  }

  function drawBeams(snap) {
    if (!snap || !snap.beams) return;
    const specs = [
      { key: "800nm", color: "#e11d48", glow: "rgba(225, 29, 72, 0.18)" },
      { key: "opa", color: "#0284c7", glow: "rgba(2, 132, 199, 0.18)" },
    ];

    for (const sp of specs) {
      const b = snap.beams[sp.key];
      if (!b || !b.open || !Array.isArray(b.segments) || b.segments.length === 0) continue;

      // Soft outer halo
      ctx.save();
      ctx.strokeStyle = sp.glow;
      ctx.lineWidth = 5.5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      for (const seg of b.segments) {
        const [x0, y0] = w2s(seg[0].x, seg[0].z);
        const [x1, y1] = w2s(seg[1].x, seg[1].z);
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
      }
      ctx.stroke();

      // Crisp beam core
      ctx.strokeStyle = sp.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (const seg of b.segments) {
        const [x0, y0] = w2s(seg[0].x, seg[0].z);
        const [x1, y1] = w2s(seg[1].x, seg[1].z);
        ctx.moveTo(x0, y0);
        ctx.lineTo(x1, y1);
      }
      ctx.stroke();

      // Direction arrowheads + vertex dots
      for (const seg of b.segments) {
        const [x0, y0] = w2s(seg[0].x, seg[0].z);
        const [x1, y1] = w2s(seg[1].x, seg[1].z);
        drawArrowhead(x0, y0, x1, y1, sp.color);
      }

      // Endpoint callout if beam didn't land cleanly on sample
      const lastSeg = b.segments[b.segments.length - 1];
      const [ex, ey] = w2s(lastSeg[1].x, lastSeg[1].z);
      ctx.fillStyle = sp.color;
      ctx.beginPath();
      ctx.arc(ex, ey, 3, 0, Math.PI * 2);
      ctx.fill();

      if (b.end && b.end !== "sample" && b.end !== "blocked") {
        const note = b.end_note || b.end;
        ctx.font = '600 10px ui-monospace, "SFMono-Regular", Menlo, monospace';
        const tw = ctx.measureText(note).width + 8;
        ctx.fillStyle = "#fffbeb";
        ctx.strokeStyle = "#d97706";
        ctx.lineWidth = 1.2;
        ctx.fillRect(ex + 6, ey - 16, tw, 15);
        ctx.strokeRect(ex + 6, ey - 16, tw, 15);
        ctx.fillStyle = "#92400e";
        ctx.textAlign = "left";
        ctx.fillText(note, ex + 10, ey - 5);
      }
      ctx.restore();
    }
  }

  function drawTable() {
    const dpr = window.devicePixelRatio || 1;
    const w = elCanvas.width / dpr;
    const h = elCanvas.height / dpr;

    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    // Drafting sheet background
    ctx.fillStyle = "#f7f9fc";
    ctx.fillRect(0, 0, w, h);

    const run = currentRun();
    if (!run) {
      ctx.fillStyle = "#475569";
      ctx.font = "13px sans-serif";
      ctx.fillText("No runs found in viewer/runs_bundle.js. Run: python3 scripts/build_viewer.py", 24, 36);
      ctx.restore();
      return;
    }

    const meta = run.meta;
    const step = currentStep();
    const snap = step ? step.snapshot : null;
    const tx = meta.table_mm.x;
    const tz = meta.table_mm.z;

    // Desk station (-300, 600)
    const [dx, dy] = w2s(meta.desk_mm.x, meta.desk_mm.z);
    const deskW = Math.max(18, 90 * state.cam.scale);
    const deskH = Math.max(30, 220 * state.cam.scale);
    ctx.fillStyle = "#e2e8f0";
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.2;
    ctx.fillRect(dx - deskW * 0.5, dy - deskH * 0.5, deskW, deskH);
    ctx.strokeRect(dx - deskW * 0.5, dy - deskH * 0.5, deskW, deskH);
    ctx.fillStyle = "#475569";
    ctx.font = '600 10px ui-monospace, "SFMono-Regular", Menlo, monospace';
    ctx.textAlign = "center";
    ctx.fillText("DESK", dx, dy + 3);

    // Optical table breadboard (0..2400 x 0..1200 mm)
    const [t0x, t0y] = w2s(0, 0);
    const [t1x, t1y] = w2s(tx, tz);
    const tw = t1x - t0x;
    const th = t1y - t0y;

    // Subtle breadboard drop shadow
    ctx.fillStyle = "rgba(15, 23, 42, 0.08)";
    ctx.fillRect(t0x + 4, t0y + 4, tw, th);

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(t0x, t0y, tw, th);

    // 100 mm & 200 mm coordinate grid
    for (let x = 100; x < tx; x += 100) {
      const [gx] = w2s(x, 0);
      ctx.strokeStyle = x % 200 === 0 ? "#dce3ee" : "#eef2f7";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(gx, t0y);
      ctx.lineTo(gx, t1y);
      ctx.stroke();
    }
    for (let z = 100; z < tz; z += 100) {
      const [, gy] = w2s(0, z);
      ctx.strokeStyle = z % 200 === 0 ? "#dce3ee" : "#eef2f7";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(t0x, gy);
      ctx.lineTo(t1x, gy);
      ctx.stroke();
    }

    // Breadboard outline
    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1.8;
    ctx.strokeRect(t0x, t0y, tw, th);

    // X and Z millimeter ruler labels
    ctx.fillStyle = "#64748b";
    ctx.font = '10px ui-monospace, "SFMono-Regular", Menlo, monospace';
    ctx.textAlign = "center";
    for (let x = 0; x <= tx; x += 400) {
      const [gx] = w2s(x, 0);
      ctx.fillText(`${x}`, gx, t0y - 6);
    }
    ctx.textAlign = "right";
    for (let z = 0; z <= tz; z += 200) {
      const [, gy] = w2s(0, z);
      ctx.fillText(`${z}`, t0x - 6, gy + 3);
    }

    // Laser & OPA source housings on right side of table
    for (const hBox of meta.housings_mm || []) {
      const [hx0, hy0] = w2s(hBox.x0, hBox.z0);
      const [hx1, hy1] = w2s(hBox.x1, hBox.z1);
      ctx.fillStyle = "#e2e8f0";
      ctx.strokeStyle = "#1e293b";
      ctx.lineWidth = 1.4;
      ctx.fillRect(hx0, hy0, hx1 - hx0, hy1 - hy0);
      ctx.strokeRect(hx0, hy0, hx1 - hx0, hy1 - hy0);
    }

    // Source port markers & shutter status
    const shutters = snap ? snap.shutters_open : { "800nm": false, opa: false };
    for (const [arm, color, shortLbl] of [
      ["800nm", "#e11d48", "800 nm"],
      ["opa", "#0284c7", `OPA ${Math.round(meta.opa_lambda_nm)} nm`],
    ]) {
      const p = meta.ports && meta.ports[arm];
      if (!p) continue;
      const [px, py] = w2s(p.pos.x, p.pos.z);
      const isOpen = Boolean(shutters && shutters[arm]);
      ctx.fillStyle = isOpen ? color : "#94a3b8";
      ctx.strokeStyle = "#0f172a";
      ctx.lineWidth = 1.2;
      ctx.fillRect(px - 5, py - 5, 10, 10);
      ctx.strokeRect(px - 5, py - 5, 10, 10);

      ctx.font = '600 10.5px ui-monospace, "SFMono-Regular", Menlo, monospace';
      ctx.fillStyle = "#0f172a";
      ctx.textAlign = "left";
      ctx.fillText(shortLbl, px + 9, py - 2);
      ctx.font = '10px ui-monospace, "SFMono-Regular", Menlo, monospace';
      ctx.fillStyle = isOpen ? color : "#64748b";
      ctx.fillText(`h=${Math.round(p.pos.h)}mm (${isOpen ? "open" : "shut"})`, px + 9, py + 10);
    }

    // Beams first or parts first? Draw parts, then beams on top so ray hits are crisp!
    const parts = snap && Array.isArray(snap.parts) ? snap.parts : [];
    for (const part of parts) {
      drawPart(part, state.hoverPart && state.hoverPart.id === part.id);
    }

    drawBeams(snap);

    // IR alignment card reticle if active on this step
    if (snap && snap.ir_probe) {
      const [ix, iy] = w2s(snap.ir_probe.x, snap.ir_probe.z);
      ctx.strokeStyle = "#f05a28";
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.arc(ix, iy, 8, 0, Math.PI * 2);
      ctx.moveTo(ix - 12, iy);
      ctx.lineTo(ix + 12, iy);
      ctx.moveTo(ix, iy - 12);
      ctx.lineTo(ix, iy + 12);
      ctx.stroke();
    }

    // Researcher marker (you_mm)
    const you = snap && snap.you_mm ? snap.you_mm : meta.desk_mm;
    if (you) {
      const [ux, uy] = w2s(you.x, you.z);
      ctx.fillStyle = "#f05a28";
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(ux, uy, 4.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    ctx.restore();
  }

  // ---------------------------------------------------------------------------
  // Selected Tool Call + Final Diagnostics Panels
  // ---------------------------------------------------------------------------

  function drawScanMini(canvas, scanData) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const w = Math.max(180, rect.width || 320);
    const h = 76;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    const c = canvas.getContext("2d");
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    c.clearRect(0, 0, w, h);

    const pts = scanData.points || [];
    if (pts.length < 2) return;
    const x0 = pts[0][0];
    const x1 = pts[pts.length - 1][0];
    let yMin = Infinity;
    let yMax = -Infinity;
    for (const p of pts) {
      if (p[1] < yMin) yMin = p[1];
      if (p[1] > yMax) yMax = p[1];
    }
    if (yMax <= yMin) yMax = yMin + 1;

    const padL = 8, padR = 8, padT = 16, padB = 16;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    c.strokeStyle = scanData.saturated ? "#dc2626" : "#0284c7";
    c.lineWidth = 1.5;
    c.beginPath();
    pts.forEach((p, idx) => {
      const px = padL + ((p[0] - x0) / Math.max(1e-9, x1 - x0)) * pw;
      const py = padT + ph - ((p[1] - yMin) / (yMax - yMin)) * ph;
      if (idx === 0) c.moveTo(px, py);
      else c.lineTo(px, py);
    });
    c.stroke();

    c.fillStyle = "#475569";
    c.font = '10px ui-monospace, "SFMono-Regular", Menlo, monospace';
    c.textAlign = "left";
    c.fillText(`${x0.toFixed(2)} mm`, padL, h - 4);
    c.fillText(
      `peak ${Math.round(scanData.max_counts)} cts @ ${Number(scanData.peak_mm).toFixed(3)} mm${scanData.saturated ? " [SAT]" : ""}`,
      padL,
      11
    );
    c.textAlign = "right";
    c.fillText(`${x1.toFixed(2)} mm`, w - padR, h - 4);
  }

  function renderSelectedCall() {
    const run = currentRun();
    if (!run) return;
    const total = run.trajectory.length;
    const step = currentStep();

    elSlider.max = String(total);
    elSlider.value = String(state.stepPos);
    elPrevBtn.disabled = state.stepPos <= 0;
    elNextBtn.disabled = state.stepPos >= total;

    const snap = step ? step.snapshot : null;
    const lamOpa = Math.round(run.meta.opa_lambda_nm);
    if (snap && snap.beams) {
      const b8 = snap.beams["800nm"];
      const bo = snap.beams.opa;
      elLeg800.textContent = `800 nm: ${b8.open ? b8.end : "shut"}`;
      elLegOpa.textContent = `OPA ${lamOpa} nm: ${bo.open ? bo.end : "shut"}`;
    } else {
      elLeg800.textContent = "800 nm: shut";
      elLegOpa.textContent = `OPA ${lamOpa} nm: shut`;
    }

    if (!step) {
      elStepLabel.textContent = `Step 0 / ${total}`;
      elCallTime.textContent = "00:00:00";
      elCallBody.innerHTML = `
        <div class="call-header-card">
          <span class="call-tool-name">Initial table state</span>
          <span class="call-delta">before call #1</span>
        </div>
        <div class="kv-block">
          <span class="kv-label">Status</span>
          <pre class="code-box">Empty 2400 × 1200 mm optical table. Both shutters closed; researcher at desk (-300, 600). Drag the slider right or press ▶ to step through tool calls.</pre>
        </div>
      `;
      return;
    }

    elStepLabel.textContent = `Step ${state.stepPos} / ${total}`;
    elCallTime.textContent = fmtClock(step.t_s);

    const resObj = step.result || {};
    const hasErr = Boolean(resObj && resObj.error);
    const headerCls = hasErr
      ? "call-header-card is-error"
      : step.tool === "submit"
      ? "call-header-card is-submit"
      : "call-header-card";

    const tr = step.truth || {};
    const argsJson = JSON.stringify(step.args || {}, null, 2);
    const resJson = JSON.stringify(resObj, null, 2);
    const hasScan = Boolean(snap && snap.scan_data && Array.isArray(snap.scan_data.points));

    elCallBody.innerHTML = `
      <div class="${headerCls}">
        <span class="call-tool-name">#${state.stepPos} &middot; ${esc(step.tool)}</span>
        <span class="call-delta">+${Number(step.cost_s ?? step.dt_s ?? 0).toFixed(1)}s &middot; €${Math.round(snap ? snap.cost_eur : 0)}</span>
      </div>
      ${hasScan ? `<canvas id="scanMiniCanvas" class="scan-mini"></canvas>` : ""}
      <div class="kv-block">
        <span class="kv-label">Arguments</span>
        <pre class="code-box">${esc(argsJson)}</pre>
      </div>
      <div class="kv-block">
        <span class="kv-label">Returned to agent</span>
        <pre class="code-box ${hasErr ? "has-err" : ""}">${esc(resJson)}</pre>
      </div>
      <div class="kv-block">
        <span class="kv-label">Simulator state after call (verifier truth)</span>
        <div class="truth-strip">
          <div class="truth-cell"><span class="k">Spot O</span><span class="v">${Number(tr.O || 0).toFixed(3)}</span></div>
          <div class="truth-cell"><span class="k">&Delta;t</span><span class="v">${fmtDt(tr.dt_fs)}</span></div>
          <div class="truth-cell"><span class="k">T_800 / T_opa</span><span class="v">${Number(tr.T_800 || 0).toFixed(2)} / ${Number(tr.T_opa || 0).toFixed(2)}</span></div>
          <div class="truth-cell"><span class="k">Live R</span><span class="v">${Number(tr.reward || 0).toFixed(3)}</span></div>
        </div>
      </div>
    `;

    if (hasScan) {
      const mini = document.getElementById("scanMiniCanvas");
      if (mini) drawScanMini(mini, snap.scan_data);
    }
  }

  function renderFinalDiagnostics() {
    const run = currentRun();
    if (!run) return;
    const d = run.diagnostics || {};
    const ended = d.ended_by || "—";
    elEndedBadge.textContent = `ended: ${ended}`;
    elEndedBadge.className =
      "badge " + (ended === "agent" ? "badge-ok" : ended === "timeout" ? "badge-err" : "badge-warn");

    const cells = [
      { k: "Reward R", v: Number(d.reward || 0).toFixed(3), primary: true },
      { k: "Overlap η", v: Number(d.eta || 0).toFixed(3), primary: true },
      { k: "Spot O", v: Number(d.O || 0).toFixed(3) },
      { k: "|Δt|", v: fmtDt(d.abs_dt_fs) },
      { k: "T_800 / T_opa", v: `${Number(d.T_800 || 0).toFixed(2)} / ${Number(d.T_opa || 0).toFixed(2)}` },
      {
        k: "Spent (min)",
        v: `€${Math.round(d.cost_eur || 0)} (€${Math.round(d.c_min_eur || run.meta.c_min_eur || 0)})`,
      },
    ];

    elDiagMetrics.innerHTML = cells
      .map(
        (c) => `
      <div class="metric-card ${c.primary ? "primary" : ""}">
        <div class="metric-k">${esc(c.k)}</div>
        <div class="metric-v">${esc(c.v)}</div>
      </div>`
      )
      .join("");

    const bought = Array.isArray(d.diagnostics_bought) && d.diagnostics_bought.length
      ? d.diagnostics_bought.join(", ")
      : "none";
    elDiagMeta.textContent =
      `Time: ${Number(d.lab_time_min || 0).toFixed(1)} / 240 min · Calls: ${d.tool_calls ?? run.trajectory.length} · Bought: ${bought}`;

    const tags = Array.isArray(run.failure_tags) ? run.failure_tags : [];
    if (!tags.length) {
      elDiagTags.innerHTML = `<div class="tag-row" style="border-left-color: var(--ok);"><span class="tag-name">clean</span><span class="tag-why">No failure tags triggered.</span></div>`;
    } else {
      elDiagTags.innerHTML = tags
        .map(
          ([tag, why]) => `
        <div class="tag-row">
          <span class="tag-name">${esc(tag)}</span>
          <span class="tag-why">${esc(why)}</span>
        </div>`
        )
        .join("");
    }
  }

  function setStep(pos) {
    const run = currentRun();
    const maxPos = run ? run.trajectory.length : 0;
    state.stepPos = Math.max(0, Math.min(maxPos, pos));
    renderSelectedCall();
    drawTable();
  }

  function selectRun(idx) {
    state.runIdx = Math.max(0, Math.min(runs.length - 1, idx));
    const run = currentRun();
    // Default to final step so the completed table & beam paths are immediately visible
    state.stepPos = run ? run.trajectory.length : 0;
    state.hoverPart = null;
    elTooltip.hidden = true;
    renderFinalDiagnostics();
    renderSelectedCall();
    drawTable();
  }

  // ---------------------------------------------------------------------------
  // Event Wiring
  // ---------------------------------------------------------------------------

  function init() {
    elRunSelect.innerHTML = runs
      .map((r, i) => `<option value="${i}">${esc(r.label)}</option>`)
      .join("");

    // Prefer the finished Flash L1 run on initial load if present
    let initialIdx = runs.findIndex(
      (r) => String(r.model || "").toLowerCase().includes("flash") && Number(r.meta && r.meta.level) === 1
    );
    if (initialIdx < 0) initialIdx = 0;
    elRunSelect.value = String(initialIdx);

    elRunSelect.addEventListener("change", () => selectRun(Number(elRunSelect.value)));
    elSlider.addEventListener("input", () => setStep(Number(elSlider.value)));
    elPrevBtn.addEventListener("click", () => setStep(state.stepPos - 1));
    elNextBtn.addEventListener("click", () => setStep(state.stepPos + 1));
    elFitBtn.addEventListener("click", () => {
      fitCamera();
      drawTable();
    });

    window.addEventListener("keydown", (ev) => {
      if (ev.target && (ev.target.tagName === "SELECT" || ev.target.tagName === "INPUT")) {
        if (ev.target !== elSlider) return;
      }
      if (ev.key === "ArrowLeft") {
        ev.preventDefault();
        setStep(state.stepPos - (ev.shiftKey ? 10 : 1));
      } else if (ev.key === "ArrowRight") {
        ev.preventDefault();
        setStep(state.stepPos + (ev.shiftKey ? 10 : 1));
      } else if (ev.key === "Home") {
        ev.preventDefault();
        setStep(0);
      } else if (ev.key === "End") {
        ev.preventDefault();
        const r = currentRun();
        if (r) setStep(r.trajectory.length);
      } else if (ev.key === "r" || ev.key === "R") {
        fitCamera();
        drawTable();
      }
    });

    // Canvas pan, zoom, and part hover
    elCanvas.addEventListener(
      "wheel",
      (ev) => {
        ev.preventDefault();
        const rect = elCanvas.getBoundingClientRect();
        const mx = ev.clientX - rect.left;
        const my = ev.clientY - rect.top;
        const [wx, wz] = s2w(mx, my);
        const factor = ev.deltaY < 0 ? 1.14 : 1 / 1.14;
        const nextScale = Math.max(0.12, Math.min(3.5, state.cam.scale * factor));
        state.cam.scale = nextScale;
        state.cam.panX = mx - wx * nextScale;
        state.cam.panY = my - wz * nextScale;
        drawTable();
      },
      { passive: false }
    );

    elCanvas.addEventListener("mousedown", (ev) => {
      state.drag = { x: ev.clientX, y: ev.clientY, panX: state.cam.panX, panY: state.cam.panY };
    });

    window.addEventListener("mouseup", () => {
      state.drag = null;
    });

    elCanvas.addEventListener("mousemove", (ev) => {
      const rect = elCanvas.getBoundingClientRect();
      const mx = ev.clientX - rect.left;
      const my = ev.clientY - rect.top;

      if (state.drag) {
        state.cam.panX = state.drag.panX + (ev.clientX - state.drag.x);
        state.cam.panY = state.drag.panY + (ev.clientY - state.drag.y);
        drawTable();
        return;
      }

      const [wx, wz] = s2w(mx, my);
      elCursor.textContent = `x ${Math.round(wx)}, z ${Math.round(wz)} mm`;

      const step = currentStep();
      const parts = step && step.snapshot ? step.snapshot.parts || [] : [];
      let hit = null;
      let bestD = 16;
      for (const p of parts) {
        const [px, py] = w2s(p.pos.x, p.pos.z);
        const d = Math.hypot(mx - px, my - py);
        if (d < bestD) {
          bestD = d;
          hit = p;
        }
      }
      if (hit !== state.hoverPart) {
        state.hoverPart = hit;
        drawTable();
      }
      if (hit) {
        const extra = hit.kind === "stage" ? `\nstage: ${Number(hit.stage_pos_mm || 0).toFixed(3)} mm` : "";
        elTooltip.textContent =
          `${hit.id}${hit.catalogue_id ? ` (${hit.catalogue_id})` : ""}\n` +
          `pos: (${hit.pos.x.toFixed(1)}, ${hit.pos.z.toFixed(1)}, h=${hit.pos.h.toFixed(1)}) mm\n` +
          `yaw: ${Number(hit.eff_yaw_deg ?? hit.yaw_deg ?? 0).toFixed(2)}°${extra}`;
        elTooltip.style.left = `${Math.min(rect.width - 190, mx + 12)}px`;
        elTooltip.style.top = `${Math.max(8, my + 12)}px`;
        elTooltip.hidden = false;
      } else {
        elTooltip.hidden = true;
      }
    });

    elCanvas.addEventListener("mouseleave", () => {
      state.hoverPart = null;
      elTooltip.hidden = true;
      drawTable();
    });

    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();
    if (runs.length > 0) selectRun(initialIdx);
  }

  init();
})();
