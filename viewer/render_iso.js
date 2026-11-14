(function () {
  "use strict";

  const INK = "#24344b";
  const GRID = "#cad5df";
  const RED = "#df3658";
  const BLUE = "#1686bb";
  const ORANGE = "#e97136";

  function actionLabel(step) {
    if (!step) return "At the lab desk";
    const a = step.args || {};
    const part = a.part || "optic";
    const names = {
      read_manual: `Reading ${a.device || "manual"}`,
      get_datasheet: `Checking ${a.part_id || "datasheet"}`,
      list_catalogue: "Checking the parts catalogue",
      status: "Checking lab status",
      buy: "Buying parts",
      place: `Placing ${part}`,
      move: `Moving ${part}`,
      remove: `Removing ${part}`,
      knob: `Adjusting ${part}`,
      ir_card: "Checking the IR card",
      view_camera: "Viewing the camera",
      measure_path: `Measuring ${a.arm || "beam"} path`,
      move_stage: "Moving the delay stage",
      scan: "Scanning the delay stage",
      read_signal: "Reading the detector",
      block: `Closing ${a.arm || "beam"} shutter`,
      unblock: `Opening ${a.arm || "beam"} shutter`,
      submit: "Submitting the setup",
    };
    return names[step.tool] || step.tool.replace(/_/g, " ");
  }

  function create(canvas, actionElement) {
    const ctx = canvas.getContext("2d");
    let scene = null;
    let animationFrame = null;
    let from = null;
    let to = null;
    let started = 0;
    let duration = 0;
    let view = null;

    function world(x, z, h) {
      const rawX = (x - z) * 0.8660254;
      const rawY = (x + z) * 0.5 - h * 1.08;
      return [rawX * view.scaleX + view.offsetX, rawY * view.scaleY + view.offsetY];
    }

    function setupView() {
      const width = canvas.clientWidth || 800;
      const height = canvas.clientHeight || 440;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, Math.round(width * dpr));
      canvas.height = Math.max(1, Math.round(height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const corners = [];
      for (const x of [-390, 2510]) for (const z of [-110, 1310]) for (const h of [0, 380]) {
        corners.push([(x - z) * 0.8660254, (x + z) * 0.5 - h * 1.08]);
      }
      const minX = Math.min(...corners.map((p) => p[0]));
      const maxX = Math.max(...corners.map((p) => p[0]));
      const minY = Math.min(...corners.map((p) => p[1]));
      const maxY = Math.max(...corners.map((p) => p[1]));
      const scaleX = (width - 90) / (maxX - minX);
      const scaleY = (height - 46) / (maxY - minY);
      view = {
        width, height, scaleX, scaleY,
        offsetX: (width - (maxX - minX) * scaleX) / 2 - minX * scaleX,
        offsetY: (height - (maxY - minY) * scaleY) / 2 - minY * scaleY + 15,
      };
    }

    function polygon(points, fill, stroke = INK, lineWidth = 1.3) {
      ctx.beginPath();
      points.forEach((p, i) => {
        const [sx, sy] = world(p.x, p.z, p.h || 0);
        if (i === 0) ctx.moveTo(sx, sy);
        else ctx.lineTo(sx, sy);
      });
      ctx.closePath();
      ctx.fillStyle = fill;
      ctx.fill();
      if (stroke) {
        ctx.strokeStyle = stroke;
        ctx.lineWidth = lineWidth;
        ctx.stroke();
      }
    }

    function line(a, b, color = INK, width = 1.2) {
      const [x0, y0] = world(a.x, a.z, a.h || 0);
      const [x1, y1] = world(b.x, b.z, b.h || 0);
      ctx.beginPath();
      ctx.moveTo(x0, y0);
      ctx.lineTo(x1, y1);
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.lineCap = "round";
      ctx.stroke();
    }

    function dot(point, radius, fill, stroke = null) {
      const [x, y] = world(point.x, point.z, point.h || 0);
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fillStyle = fill;
      ctx.fill();
      if (stroke) {
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
    }

    function box(b, top, front) {
      const p = (x, z, h) => ({ x, z, h });
      polygon([p(b.x0, b.z0, b.h1), p(b.x1, b.z0, b.h1),
        p(b.x1, b.z1, b.h1), p(b.x0, b.z1, b.h1)], top);
      polygon([p(b.x1, b.z0, b.h0), p(b.x1, b.z1, b.h0),
        p(b.x1, b.z1, b.h1), p(b.x1, b.z0, b.h1)], front);
      polygon([p(b.x0, b.z1, b.h0), p(b.x1, b.z1, b.h0),
        p(b.x1, b.z1, b.h1), p(b.x0, b.z1, b.h1)], "#aab8c7");
    }

    function drawTable(meta) {
      const x = meta.table_mm.x;
      const z = meta.table_mm.z;
      const p = (xx, zz, h = 0) => ({ x: xx, z: zz, h });
      polygon([p(0, 0, -34), p(x, 0, -34), p(x, z, -34), p(0, z, -34)], "#a9b8c7");
      polygon([p(0, 0), p(x, 0), p(x, z), p(0, z)], "#f7fafc", INK, 1.8);
      for (let gx = 100; gx < x; gx += 100) {
        for (let gz = 100; gz < z; gz += 100) {
          dot(p(gx, gz), gx % 200 === 0 && gz % 200 === 0 ? 1.1 : 0.65, GRID);
        }
      }
      line(p(0, 0), p(x, 0), "#58728d", 1.5);
      line(p(0, 0), p(0, z), "#58728d", 1.5);
    }

    function drawPartPost(part) {
      const p = part.pos;
      line({ x: p.x, z: p.z, h: 0 }, p, "#7a8b9d", 3);
      dot({ x: p.x, z: p.z, h: 0 }, 3.5, "#d5dee6", INK);
    }

    function drawPartHead(part) {
      const p = part.pos;
      const [cx, cy] = world(p.x, p.z, p.h);
      if (part.kind === "mirror") {
        const a = (part.eff_yaw_deg ?? part.yaw_deg ?? 0) * Math.PI / 180;
        const tangent = { x: -Math.sin(a) * 34, z: Math.cos(a) * 34 };
        line({ x: p.x - tangent.x, z: p.z - tangent.z, h: p.h },
          { x: p.x + tangent.x, z: p.z + tangent.z, h: p.h }, "#25a4c7", 4);
        dot(p, 4, "#33475a", "#14253b");
      } else if (part.kind === "periscope") {
        if (part.h_in != null) {
          line({ x: p.x, z: p.z, h: part.h_in }, p, "#849bb0", 5);
          dot({ x: p.x, z: p.z, h: part.h_in }, 5, "#cedae5", INK);
        }
        dot(p, 6, "#b9d2df", INK);
        dot(p, 2.5, INK);
      } else if (part.kind === "stage") {
        const a = (part.yaw_deg || 0) * Math.PI / 180;
        const railEnd = { x: p.x + Math.cos(a) * 135, z: p.z + Math.sin(a) * 135, h: p.h };
        line(p, railEnd, "#667f96", 8);
        line(p, railEnd, "#e4edf3", 4);
        const t = 90 + Number(part.stage_pos_mm || 0);
        dot({ x: p.x + Math.cos(a) * t, z: p.z + Math.sin(a) * t, h: p.h },
          7, "#e8bc56", "#835c1e");
      } else if (part.kind === "sample") {
        for (const lens of part.lenses || []) {
          dot(lens.center, 6, "#9ee2ed", "#267a91");
        }
        dot((part.lenses || [])[0]?.sample_pos || p, 7, "#9a85d5", "#57478a");
      }
      ctx.fillStyle = INK;
      ctx.font = '600 10px ui-monospace, "SFMono-Regular", Menlo, monospace';
      ctx.textAlign = "center";
      ctx.fillText(part.id, cx, cy - 13);
    }

    function drawBeams(snap) {
      for (const [key, color] of [["800nm", RED], ["opa", BLUE]]) {
        const beam = snap.beams && snap.beams[key];
        if (!beam || !beam.open) continue;
        for (const segment of beam.segments || []) {
          line(segment[0], segment[1], color === RED ? "#f5bcc9" : "#a7d7ed", 6);
          line(segment[0], segment[1], color, 2.4);
        }
      }
    }

    function drawAvatar(pos, moving, tool) {
      if (!pos) return;
      const foot = { x: pos.x, z: pos.z, h: 0 };
      const body = { x: pos.x, z: pos.z, h: 150 };
      const head = { x: pos.x, z: pos.z, h: 260 };
      const [fx, fy] = world(foot.x, foot.z, 0);
      ctx.beginPath();
      ctx.ellipse(fx, fy, 7, 3, 0, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(21, 39, 58, 0.18)";
      ctx.fill();
      line({ x: pos.x - 24, z: pos.z, h: 0 },
        { x: pos.x - 10, z: pos.z, h: 82 }, INK, 2.8);
      line({ x: pos.x + 24, z: pos.z, h: 0 },
        { x: pos.x + 10, z: pos.z, h: 82 }, INK, 2.8);
      line({ x: pos.x, z: pos.z, h: 82 }, body, ORANGE, 9);
      const gesture = moving ? Math.sin(performance.now() / 90) * 15 : 0;
      line({ x: pos.x, z: pos.z, h: 160 },
        { x: pos.x + 44, z: pos.z + gesture, h: tool === "knob" ? 195 : 130 }, INK, 2.8);
      line({ x: pos.x, z: pos.z, h: 160 },
        { x: pos.x - 40, z: pos.z, h: 125 }, INK, 2.8);
      dot(head, 7, "#f2c89e", INK);
      line({ x: pos.x - 30, z: pos.z, h: 282 },
        { x: pos.x + 30, z: pos.z, h: 282 }, INK, 3);
      const [bx, by] = world(pos.x, pos.z, 320);
      ctx.fillStyle = "#ffffff";
      ctx.strokeStyle = INK;
      ctx.lineWidth = 1;
      ctx.font = '600 10px ui-monospace, "SFMono-Regular", Menlo, monospace';
      const action = actionLabel(scene.step);
      const width = Math.min(230, ctx.measureText(action).width + 12);
      ctx.fillRect(bx - width / 2, by - 16, width, 19);
      ctx.strokeRect(bx - width / 2, by - 16, width, 19);
      ctx.fillStyle = INK;
      ctx.textAlign = "center";
      ctx.fillText(action, bx, by - 3);
    }

    function drawTarget(step, snap) {
      if (!step || !snap) return;
      const partId = step.args && step.args.part;
      if (!partId || !["place", "move", "knob", "remove", "ir_card"].includes(step.tool)) return;
      const part = (snap.parts || []).find((item) => item.id === partId);
      if (!part) return;
      const [x, y] = world(part.pos.x, part.pos.z, part.pos.h);
      ctx.beginPath();
      ctx.arc(x, y, 12, 0, Math.PI * 2);
      ctx.strokeStyle = ORANGE;
      ctx.lineWidth = 1.6;
      ctx.setLineDash([3, 3]);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    function paint(timestamp = performance.now()) {
      animationFrame = null;
      setupView();
      ctx.clearRect(0, 0, view.width, view.height);
      ctx.fillStyle = "#edf2f6";
      ctx.fillRect(0, 0, view.width, view.height);
      if (!scene || !scene.run) return;
      const { run, step } = scene;
      const snap = step && step.snapshot;
      drawTable(run.meta);
      for (const housing of run.meta.housings_mm || []) box(housing, "#d1dce5", "#9bafc0");
      const desk = run.meta.desk_mm;
      box({ x0: desk.x - 55, x1: desk.x + 55, z0: desk.z - 105, z1: desk.z + 105,
        h0: 0, h1: 75 }, "#c9d6e1", "#9dafbd");
      if (snap) {
        const parts = [...(snap.parts || [])].sort((a, b) =>
          (a.pos.x + a.pos.z) - (b.pos.x + b.pos.z));
        for (const part of parts) drawPartPost(part);
        drawBeams(snap);
        for (const part of parts) drawPartHead(part);
        drawTarget(step, snap);
      }
      const progress = duration > 0 ? Math.min(1, (timestamp - started) / duration) : 1;
      const eased = progress * progress * (3 - 2 * progress);
      const pos = to && from ? {
        x: from.x + (to.x - from.x) * eased,
        z: from.z + (to.z - from.z) * eased,
      } : to || desk;
      drawAvatar(pos, progress < 1, step && step.tool);
      if (progress < 1) animationFrame = requestAnimationFrame(paint);
    }

    return {
      show(run, step, previousStep, animate = false, speed = 1) {
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
        scene = { run, step };
        actionElement.textContent = actionLabel(step);
        to = step && step.snapshot ? step.snapshot.you_mm : run?.meta.desk_mm || null;
        from = previousStep && previousStep.snapshot ? previousStep.snapshot.you_mm : run?.meta.desk_mm || to;
        duration = animate && from && to ? 760 / speed : 0;
        started = performance.now();
        paint(started);
      },
      resize() {
        if (animationFrame !== null) cancelAnimationFrame(animationFrame);
        paint();
      },
    };
  }

  window.GSSIsoRenderer = { create };
})();
