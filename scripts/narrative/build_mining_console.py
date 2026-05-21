"""Build the Narrative Mining Console — Phase 5.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §11.

Generates a single self-contained HTML file at
`docs/portfolio/narrative_mining_console.html` with the current narrative
data embedded inline. No external assets, no live runtime — just a static
viewer the user can open in any browser.

Usage:
    python scripts/narrative/build_mining_console.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>WITNESS Narrative Mining Console</title>
<style>
  :root {
    --bg: #15110d;
    --fg: #d4cfc7;
    --fg-dim: #7a716a;
    --accent: #e8c87a;
    --strong: #7fc8a4;
    --usable: #e8c87a;
    --weak: #d96b6b;
    --hold: #909090;
    --panel: #1d1813;
    --border: #2a221c;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    font-size: 12px;
    line-height: 1.5;
  }
  h1, h2, h3 { font-weight: normal; margin: 0; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }

  header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: baseline; gap: 24px;
    flex-wrap: wrap;
  }
  header h1 {
    font-size: 14px;
    color: var(--accent);
    letter-spacing: 0.05em;
  }
  header .meta { color: var(--fg-dim); font-size: 11px; }
  header .meta strong { color: var(--fg); font-weight: normal; }

  .timeline-wrap {
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    background: var(--panel);
  }
  .timeline-wrap canvas { display: block; width: 100%; height: 80px; }
  .timeline-legend {
    margin-top: 6px;
    font-size: 10px;
    color: var(--fg-dim);
    display: flex; gap: 16px; flex-wrap: wrap;
  }
  .timeline-legend span { display: inline-flex; align-items: center; gap: 4px; }
  .timeline-legend .dot {
    display: inline-block; width: 8px; height: 8px; border-radius: 2px;
  }

  main {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 1px;
    background: var(--border);
    min-height: calc(100vh - 200px);
  }
  .thread-list { background: var(--panel); padding: 12px; overflow-y: auto; }
  .thread-list .item {
    padding: 10px 12px; margin-bottom: 6px;
    border: 1px solid var(--border);
    border-radius: 3px;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
  }
  .thread-list .item:hover { background: rgba(232, 200, 122, 0.04); }
  .thread-list .item.active {
    border-color: var(--accent);
    background: rgba(232, 200, 122, 0.06);
  }
  .thread-list .item .id {
    color: var(--accent);
    font-size: 10px;
    letter-spacing: 0.1em;
  }
  .thread-list .item .title { color: var(--fg); margin-top: 2px; }
  .thread-list .item .meta {
    color: var(--fg-dim); font-size: 10px; margin-top: 4px;
    display: flex; justify-content: space-between;
  }
  .rank { padding: 1px 6px; border-radius: 2px; font-size: 10px; }
  .rank.strong { background: rgba(127, 200, 164, 0.15); color: var(--strong); }
  .rank.usable { background: rgba(232, 200, 122, 0.15); color: var(--usable); }
  .rank.weak   { background: rgba(217, 107, 107, 0.15); color: var(--weak); }
  .rank.hold   { background: rgba(144, 144, 144, 0.15); color: var(--hold); }

  .detail { background: var(--bg); padding: 20px 28px; overflow-y: auto; }
  .detail .empty {
    color: var(--fg-dim); font-style: italic; padding: 24px 0;
  }
  .detail h2 {
    font-size: 16px;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-bottom: 14px;
  }
  .detail h2 .id-prefix { color: var(--fg-dim); }
  .detail .badges { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
  .detail .badge {
    padding: 2px 8px;
    border: 1px solid var(--border);
    border-radius: 2px;
    color: var(--fg-dim);
    font-size: 10px;
  }
  .detail .badge strong { color: var(--fg); font-weight: normal; }

  .detail section { margin-bottom: 18px; }
  .detail section h3 {
    font-size: 11px;
    color: var(--fg-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .detail .logline { font-size: 13px; line-height: 1.6; }
  .detail .question {
    padding: 8px 12px;
    border-left: 2px solid var(--accent);
    background: rgba(232, 200, 122, 0.04);
  }

  table.evidence {
    width: 100%; border-collapse: collapse;
    font-size: 11px;
  }
  table.evidence th, table.evidence td {
    text-align: left; padding: 4px 8px;
    border-bottom: 1px solid var(--border);
  }
  table.evidence th { color: var(--fg-dim); font-weight: normal; }
  table.evidence td.tick { color: var(--accent); width: 50px; }
  table.evidence td.type { color: var(--fg-dim); width: 160px; }
  table.evidence td.prov {
    width: 120px; font-size: 10px;
  }
  table.evidence td.prov.source_derived  { color: var(--strong); }
  table.evidence td.prov.source_inferred { color: var(--usable); }
  table.evidence td.prov.not_used        { color: var(--hold); }

  .chip-row { display: flex; flex-wrap: wrap; gap: 4px; }
  .chip {
    padding: 2px 6px;
    border-radius: 2px;
    background: rgba(255, 255, 255, 0.04);
    color: var(--fg-dim);
    font-size: 10px;
  }
  .creative-uses .chip { color: var(--accent); }

  footer {
    padding: 12px 24px;
    border-top: 1px solid var(--border);
    color: var(--fg-dim);
    font-size: 10px;
  }
</style>
</head>
<body>

<header>
  <h1>WITNESS · Narrative Mining Console</h1>
  <span class="meta">
    run <strong id="meta-run">—</strong>
    · ticks <strong id="meta-ticks">—</strong>
    · moments <strong id="meta-moments">—</strong>
    · threads <strong id="meta-threads">—</strong>
    · strong <strong id="meta-strong">—</strong>
    · usable <strong id="meta-usable">—</strong>
  </span>
</header>

<div class="timeline-wrap">
  <canvas id="timeline" height="80"></canvas>
  <div class="timeline-legend">
    <span><i class="dot" style="background:var(--strong)"></i> strong thread</span>
    <span><i class="dot" style="background:var(--usable)"></i> usable</span>
    <span><i class="dot" style="background:var(--weak)"></i> weak</span>
    <span><i class="dot" style="background:rgba(217,107,107,0.55)"></i> world pressure shift</span>
    <span><i class="dot" style="background:rgba(232,200,122,0.55)"></i> agent state shift</span>
    <span><i class="dot" style="background:rgba(127,200,164,0.55)"></i> group tension shift</span>
  </div>
</div>

<main>
  <aside class="thread-list" id="threadList"></aside>
  <article class="detail" id="threadDetail">
    <p class="empty">Select a thread on the left.</p>
  </article>
</main>

<footer>
  static console · self-contained · regenerated by
  <code>scripts/narrative/build_mining_console.py</code> ·
  data classes: <code>source_derived</code> /
  <code>source_inferred</code> / <code>not_used</code>
</footer>

<script type="application/json" id="data-opportunities">__OPPORTUNITIES__</script>
<script type="application/json" id="data-threads">__THREADS__</script>
<script type="application/json" id="data-moments">__MOMENTS__</script>
<script type="application/json" id="data-meta">__META__</script>

<script>
"use strict";

const OPPS    = JSON.parse(document.getElementById("data-opportunities").textContent);
const THREADS = JSON.parse(document.getElementById("data-threads").textContent);
const MOMENTS = JSON.parse(document.getElementById("data-moments").textContent);
const META    = JSON.parse(document.getElementById("data-meta").textContent);

const THREAD_BY_ID = Object.fromEntries(THREADS.threads.map(t => [t.thread_id, t]));
const MOMENT_BY_ID = Object.fromEntries(MOMENTS.moments.map(m => [m.moment_id, m]));

// ============================================================
// Header meta
// ============================================================
document.getElementById("meta-run").textContent      = OPPS.run_label;
document.getElementById("meta-ticks").textContent    = META.ticks;
document.getElementById("meta-moments").textContent  = MOMENTS.moments.length;
document.getElementById("meta-threads").textContent  = OPPS.summary.threads_total;
document.getElementById("meta-strong").textContent   = OPPS.summary.strong_opportunities;
document.getElementById("meta-usable").textContent   = OPPS.summary.usable_threads;

// ============================================================
// Thread list
// ============================================================
const list = document.getElementById("threadList");
let activeId = null;

OPPS.opportunities.forEach(op => {
  const item = document.createElement("div");
  item.className = "item";
  item.dataset.id = op.thread_id;
  item.innerHTML = `
    <div class="id">${op.thread_id}</div>
    <div class="title">${op.title}</div>
    <div class="meta">
      <span>t${op.start_tick}–${op.end_tick} · ${op.moment_count} moments</span>
      <span class="rank ${op.rank}">${op.rank} · ${op.score.toFixed(2)}</span>
    </div>
  `;
  item.addEventListener("click", () => selectThread(op.thread_id));
  list.appendChild(item);
});

function selectThread(threadId) {
  activeId = threadId;
  for (const el of list.querySelectorAll(".item")) {
    el.classList.toggle("active", el.dataset.id === threadId);
  }
  renderDetail(threadId);
  renderTimeline();
}

// ============================================================
// Detail panel
// ============================================================
function renderDetail(threadId) {
  const detail = document.getElementById("threadDetail");
  const op = OPPS.opportunities.find(o => o.thread_id === threadId);
  const t  = THREAD_BY_ID[threadId];
  if (!op || !t) {
    detail.innerHTML = `<p class="empty">Thread not found.</p>`;
    return;
  }

  const evidenceRows = (t.moment_ids || []).map(mid => {
    const m = MOMENT_BY_ID[mid];
    if (!m) return "";
    return `
      <tr>
        <td class="tick">t${m.tick}</td>
        <td><code>${m.moment_id}</code></td>
        <td class="type">${m.moment_type}</td>
        <td class="prov ${m.provenance}">${m.provenance}</td>
        <td>${escapeHtml(m.summary)}</td>
      </tr>`;
  }).join("");

  const pressureChips = (t.pressure_history || [])
    .map(p => `<span class="chip">${p}</span>`).join("");
  const creativeChips = (op.creative_uses || [])
    .map(u => `<span class="chip">${u}</span>`).join("")
    || `<span class="chip">(no tags)</span>`;
  const groupsList    = (t.groups || []).join(", ") || "—";
  const mainAgents    = (t.main_agents || []).join(", ") || "(world-level)";
  const supporting    = (t.supporting_agents || []).join(", ") || "—";
  const relationship  = (t.relationship_drift || []).join(", ") || "—";

  detail.innerHTML = `
    <h2><span class="id-prefix">${op.thread_id} · </span>${escapeHtml(op.title)}</h2>
    <div class="badges">
      <span class="badge"><strong>${op.rank}</strong> · score ${op.score.toFixed(3)}</span>
      <span class="badge">conflict <strong>${op.core_conflict}</strong></span>
      <span class="badge">arc <strong>${op.arc_direction}</strong></span>
      <span class="badge">tick span <strong>${t.start_tick}–${t.end_tick}</strong></span>
      <span class="badge">${(t.moment_ids || []).length} moments</span>
    </div>

    <section>
      <h3>Logline</h3>
      <p class="logline">${escapeHtml(op.logline)}</p>
    </section>

    <section>
      <h3>Unresolved Question</h3>
      <p class="question">${escapeHtml(op.unresolved_question)}</p>
    </section>

    <section>
      <h3>Cast &amp; Setting</h3>
      <p>main: <strong>${escapeHtml(mainAgents)}</strong></p>
      <p>supporting: ${escapeHtml(supporting)}</p>
      <p>groups: ${escapeHtml(groupsList)}</p>
      <p>relationship drift: ${escapeHtml(relationship)}</p>
    </section>

    <section>
      <h3>Pressure History</h3>
      <div class="chip-row">${pressureChips || "<span class='chip'>(none)</span>"}</div>
    </section>

    <section>
      <h3>Creative Uses</h3>
      <div class="chip-row creative-uses">${creativeChips}</div>
    </section>

    <section>
      <h3>Evidence</h3>
      <table class="evidence">
        <thead>
          <tr><th>Tick</th><th>Moment</th><th>Type</th><th>Provenance</th><th>Summary</th></tr>
        </thead>
        <tbody>${evidenceRows || "<tr><td colspan='5'>—</td></tr>"}</tbody>
      </table>
    </section>
  `;
}

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ============================================================
// Timeline canvas
// ============================================================
function renderTimeline() {
  const canvas = document.getElementById("timeline");
  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth;
  const H = canvas.clientHeight;
  canvas.width  = W * dpr;
  canvas.height = H * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);

  const totalTicks = META.ticks || 200;
  const xOf = t => (t / totalTicks) * W;

  // Background grid
  ctx.strokeStyle = "rgba(255,255,255,0.03)";
  ctx.lineWidth = 1;
  for (let t = 0; t <= totalTicks; t += 25) {
    const x = xOf(t);
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, H);
    ctx.stroke();
  }

  // Moment dots by type
  const colorByType = {
    agent_state_shift:    "rgba(232,200,122,0.55)",
    group_tension_shift:  "rgba(127,200,164,0.55)",
    world_pressure_shift: "rgba(217,107,107,0.55)",
    conflict_marker:      "rgba(255,255,255,0.7)",
    unresolved_thread:    "rgba(160,140,200,0.5)",
  };
  for (const m of MOMENTS.moments) {
    const c = colorByType[m.moment_type] || "rgba(255,255,255,0.3)";
    const x = xOf(m.tick);
    const y = H - 14;
    ctx.fillStyle = c;
    ctx.beginPath();
    ctx.arc(x, y, 2.5, 0, Math.PI * 2);
    ctx.fill();
  }

  // Thread spans
  const rankColor = {
    strong: "rgba(127,200,164,0.65)",
    usable: "rgba(232,200,122,0.55)",
    weak:   "rgba(217,107,107,0.45)",
    hold:   "rgba(144,144,144,0.40)",
  };
  let row = 0;
  for (const op of OPPS.opportunities) {
    const x0 = xOf(op.start_tick);
    const x1 = xOf(op.end_tick);
    const isActive = op.thread_id === activeId;
    const color = rankColor[op.rank] || "rgba(255,255,255,0.3)";
    const yTop = 6 + row * 12;
    ctx.fillStyle = color;
    ctx.fillRect(x0, yTop, Math.max(2, x1 - x0), isActive ? 6 : 4);
    if (isActive) {
      ctx.strokeStyle = "rgba(232,200,122,0.9)";
      ctx.lineWidth = 1;
      ctx.strokeRect(x0 - 1, yTop - 1, Math.max(2, x1 - x0) + 2, 8);
    }
    row = (row + 1) % 5;
  }
}

// Initial render
renderTimeline();
window.addEventListener("resize", renderTimeline);

// Auto-select first thread if any
if (OPPS.opportunities.length > 0) {
  selectThread(OPPS.opportunities[0].thread_id);
}
</script>
</body>
</html>
"""


def _load_or_empty(p: Path, default: dict) -> dict:
    """Load JSON from p; on missing file or empty dict, fall back to default
    (merged shallowly with whatever was loaded)."""
    if not p.exists():
        return default
    loaded = json.loads(p.read_text(encoding="utf-8"))
    if not loaded:
        return default
    # Shallow merge: defaults provide missing top-level keys
    out = dict(default)
    out.update(loaded)
    return out


def main(in_ops: str, in_threads: str, in_moments: str,
         in_observer: str, out_html: str) -> None:
    ops = _load_or_empty(Path(in_ops), {
        "run_label": "unknown", "summary": {
            "threads_total": 0, "strong_opportunities": 0,
            "usable_threads": 0, "weak_threads": 0, "hold_threads": 0,
        }, "opportunities": [],
    })
    threads = _load_or_empty(Path(in_threads), {"threads": []})
    moments = _load_or_empty(Path(in_moments), {"moments": []})
    observer = _load_or_empty(Path(in_observer), {"meta": {}, "ticks": []})

    meta = {
        "ticks": observer.get("meta", {}).get("n_ticks") or len(observer.get("ticks", [])),
        "anchor_id": observer.get("meta", {}).get("anchor_id", "unknown"),
        "seed": observer.get("meta", {}).get("seed"),
    }

    html = HTML_TEMPLATE
    html = html.replace("__OPPORTUNITIES__", json.dumps(ops, ensure_ascii=False))
    html = html.replace("__THREADS__",       json.dumps(threads, ensure_ascii=False))
    html = html.replace("__MOMENTS__",       json.dumps(moments, ensure_ascii=False))
    html = html.replace("__META__",          json.dumps(meta, ensure_ascii=False))

    out = Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(
        f"Wrote {out_html} ({len(html)} bytes, "
        f"{len(ops['opportunities'])} threads, "
        f"{len(moments.get('moments', []))} moments embedded)"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--ops", default="data/narrative/narrative_opportunities.json")
    ap.add_argument("--threads", default="data/narrative/story_threads.json")
    ap.add_argument("--moments", default="data/narrative/moments.json")
    ap.add_argument("--observer", default="data/visual/dot_observer_data.json")
    ap.add_argument("--out", default="docs/portfolio/narrative_mining_console.html")
    ns = ap.parse_args()
    main(ns.ops, ns.threads, ns.moments, ns.observer, ns.out)


if __name__ == "__main__":
    cli()
