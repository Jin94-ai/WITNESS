"""Build Story Candidate Console — Phase F.

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §7.3.

Generates a single self-contained static HTML at
`docs/portfolio/story_candidate_console.html` showing:
    - Run summary header
    - Story Candidate list (sortable by rank)
    - Selected candidate detail: title / premise / arc / turning points /
      character & group context / creative-use tabs / evidence toggle
    - Cross-seed robustness badge (if cross_seed_story_patterns.json exists)
    - All data embedded inline (no external assets, no live runtime)

Usage:
    python scripts/narrative/build_story_candidate_console.py
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
<title>WITNESS Story Candidate Console</title>
<style>
  :root {
    --bg: #14110d;
    --bg-soft: #1c1813;
    --fg: #d6d0c7;
    --fg-dim: #7a716a;
    --accent: #e8c87a;
    --accent-soft: rgba(232, 200, 122, 0.08);
    --robust:  #7fc8a4;
    --moderate: #e8c87a;
    --anomaly: #d96b6b;
    --border: #2a221c;
    --src-derived: #7fc8a4;
    --src-inferred: #e8c87a;
    --not-used: #909090;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    font-size: 12px;
    line-height: 1.55;
  }
  h1, h2, h3 { font-weight: normal; margin: 0; }

  header {
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: baseline; gap: 24px;
    flex-wrap: wrap;
  }
  header h1 {
    font-size: 14px; color: var(--accent); letter-spacing: 0.05em;
  }
  header .meta { color: var(--fg-dim); font-size: 11px; }
  header .meta strong { color: var(--fg); font-weight: normal; }

  main {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 1px;
    background: var(--border);
    min-height: calc(100vh - 60px);
  }

  /* candidate list */
  aside.candidates {
    background: var(--bg-soft);
    padding: 10px;
    overflow-y: auto;
  }
  aside.candidates .item {
    padding: 10px 12px;
    margin-bottom: 6px;
    border: 1px solid var(--border);
    border-radius: 3px;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
  }
  aside.candidates .item:hover { background: var(--accent-soft); }
  aside.candidates .item.active {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  aside.candidates .item .id {
    font-size: 10px; color: var(--accent); letter-spacing: 0.1em;
  }
  aside.candidates .item .title { color: var(--fg); margin-top: 3px; }
  aside.candidates .item .conflict {
    font-size: 10px; color: var(--fg-dim); margin-top: 4px;
  }
  aside.candidates .item .robustness {
    margin-top: 5px; display: flex; gap: 6px; align-items: center;
  }
  .badge {
    font-size: 10px; padding: 1px 6px; border-radius: 2px;
  }
  .badge.robust   { background: rgba(127, 200, 164, 0.15); color: var(--robust); }
  .badge.moderate { background: rgba(232, 200, 122, 0.15); color: var(--moderate); }
  .badge.anomaly  { background: rgba(217, 107, 107, 0.15); color: var(--anomaly); }

  /* detail panel */
  article.detail {
    background: var(--bg);
    padding: 22px 28px;
    overflow-y: auto;
  }
  article.detail .empty {
    color: var(--fg-dim); font-style: italic;
  }
  article.detail h2 {
    font-size: 16px; color: var(--accent);
    border-bottom: 1px solid var(--border); padding-bottom: 6px;
    margin-bottom: 14px;
  }
  article.detail h2 .id-prefix { color: var(--fg-dim); }
  article.detail .badges-row {
    display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px;
  }
  article.detail .badge-meta {
    padding: 2px 8px; border: 1px solid var(--border); border-radius: 2px;
    color: var(--fg-dim); font-size: 10px;
  }
  article.detail .badge-meta strong { color: var(--fg); font-weight: normal; }

  article.detail section { margin-bottom: 18px; }
  article.detail section h3 {
    font-size: 11px; color: var(--fg-dim);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 6px;
  }
  article.detail .premise { font-size: 13px; line-height: 1.65; }
  article.detail .question {
    padding: 8px 12px;
    border-left: 2px solid var(--accent);
    background: var(--accent-soft);
  }
  article.detail .arc {
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 2px;
    font-family: inherit;
  }

  /* turning points table */
  table.turning {
    width: 100%; border-collapse: collapse; font-size: 11px;
  }
  table.turning th, table.turning td {
    text-align: left; padding: 4px 8px;
    border-bottom: 1px solid var(--border);
  }
  table.turning th { color: var(--fg-dim); font-weight: normal; }
  table.turning td.tick { color: var(--accent); width: 50px; }
  table.turning td.label { color: var(--fg-dim); width: 200px; }
  table.turning td.prov { width: 120px; font-size: 10px; }
  table.turning td.prov.source_derived  { color: var(--src-derived); }
  table.turning td.prov.source_inferred { color: var(--src-inferred); }
  table.turning td.prov.not_used        { color: var(--not-used); }

  /* creative use tabs */
  .tabs {
    display: flex; gap: 1px; background: var(--border);
    margin-bottom: 8px;
  }
  .tab {
    flex: 0 0 auto;
    background: var(--bg-soft);
    padding: 6px 12px; cursor: pointer;
    color: var(--fg-dim);
    font-size: 11px;
  }
  .tab:hover { color: var(--fg); }
  .tab.active {
    background: var(--bg);
    color: var(--accent);
    border-bottom: 1px solid var(--accent);
  }
  .tab-content {
    padding: 10px 14px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 0 0 3px 3px;
    min-height: 50px;
  }

  /* evidence toggle */
  details.evidence {
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 6px 12px;
  }
  details.evidence summary {
    cursor: pointer; color: var(--fg-dim); font-size: 11px;
    list-style: none;
  }
  details.evidence summary::before { content: "▸ "; }
  details[open].evidence summary::before { content: "▾ "; }
  details.evidence .evidence-body { padding-top: 8px; font-size: 11px; }

  /* chip rows */
  .chip-row { display: flex; flex-wrap: wrap; gap: 4px; }
  .chip {
    padding: 2px 6px; border-radius: 2px;
    background: rgba(255, 255, 255, 0.04);
    color: var(--fg-dim); font-size: 10px;
  }

  footer {
    padding: 10px 24px;
    border-top: 1px solid var(--border);
    color: var(--fg-dim);
    font-size: 10px;
  }
</style>
</head>
<body>

<header>
  <h1>WITNESS · Story Candidate Console</h1>
  <span class="meta">
    run <strong id="meta-run">—</strong>
    · candidates <strong id="meta-cands">—</strong>
    · cross-seed <strong id="meta-xs">—</strong>
  </span>
</header>

<main>
  <aside class="candidates" id="candList"></aside>
  <article class="detail" id="detail">
    <p class="empty">Select a story candidate on the left.</p>
  </article>
</main>

<footer>
  static console · self-contained · regenerated by
  <code>scripts/narrative/build_story_candidate_console.py</code> ·
  forbidden in this surface: completed dialogue / screenplay / over-narrated emotion ·
  every line traceable to its source moment via <code>source_derived</code> /
  <code>source_inferred</code> / <code>not_used</code>
</footer>

<script type="application/json" id="data-candidates">__CANDS__</script>
<script type="application/json" id="data-xs">__XS__</script>
<script type="application/json" id="data-meta">__META__</script>

<script>
"use strict";

const CANDS_PAYLOAD = JSON.parse(document.getElementById("data-candidates").textContent);
const XS_PAYLOAD    = JSON.parse(document.getElementById("data-xs").textContent);
const META          = JSON.parse(document.getElementById("data-meta").textContent);
const CANDS = (CANDS_PAYLOAD && CANDS_PAYLOAD.candidates) || [];

// Build robustness lookup from cross-seed report (if present)
const ROBUSTNESS_BY_CONFLICT = {};
const ROBUSTNESS_BY_CHARACTER = {};
if (XS_PAYLOAD && XS_PAYLOAD.conflict_patterns) {
  for (const p of XS_PAYLOAD.conflict_patterns) {
    ROBUSTNESS_BY_CONFLICT[p.pattern_value] = p.robustness;
  }
}
if (XS_PAYLOAD && XS_PAYLOAD.character_patterns) {
  for (const p of XS_PAYLOAD.character_patterns) {
    ROBUSTNESS_BY_CHARACTER[p.pattern_value] = p.robustness;
  }
}

// --- Header ---
document.getElementById("meta-run").textContent   = (CANDS_PAYLOAD && CANDS_PAYLOAD.run_label) || "—";
document.getElementById("meta-cands").textContent = CANDS.length;
document.getElementById("meta-xs").textContent    = XS_PAYLOAD
  ? `${(XS_PAYLOAD.summary || {}).total_patterns || 0} patterns (robust ${(XS_PAYLOAD.summary||{}).robust||0} / anomaly ${(XS_PAYLOAD.summary||{}).anomaly||0})`
  : "(no cross-seed)";

// --- Candidate list ---
const list = document.getElementById("candList");
let activeId = null;
CANDS.forEach(c => {
  const item = document.createElement("div");
  item.className = "item";
  item.dataset.id = c.story_candidate_id;
  const conflictRobust = ROBUSTNESS_BY_CONFLICT[c.core_conflict] || "";
  const charRobust = (c.main_characters || [])
    .map(n => ROBUSTNESS_BY_CHARACTER[n] || "")
    .find(Boolean) || "";
  const robustnessHTML = conflictRobust
    ? `<span class="badge ${conflictRobust}">${conflictRobust}</span>`
    : "";
  item.innerHTML = `
    <div class="id">${c.story_candidate_id}</div>
    <div class="title">${escapeHtml(c.title)}</div>
    <div class="conflict">${escapeHtml(c.core_conflict)}</div>
    <div class="robustness">${robustnessHTML}</div>
  `;
  item.addEventListener("click", () => selectCandidate(c.story_candidate_id));
  list.appendChild(item);
});

function selectCandidate(cid) {
  activeId = cid;
  for (const el of list.querySelectorAll(".item")) {
    el.classList.toggle("active", el.dataset.id === cid);
  }
  renderDetail(cid);
}

function renderDetail(cid) {
  const detail = document.getElementById("detail");
  const c = CANDS.find(x => x.story_candidate_id === cid);
  if (!c) {
    detail.innerHTML = `<p class="empty">Candidate not found.</p>`;
    return;
  }

  const conflictRobust = ROBUSTNESS_BY_CONFLICT[c.core_conflict] || "";
  const conflictBadge = conflictRobust
    ? `<span class="badge ${conflictRobust}">conflict ${conflictRobust}</span>`
    : "";

  const turningRows = (c.key_turning_points || []).map(tp => `
    <tr>
      <td class="tick">t${tp.tick}</td>
      <td class="label">${escapeHtml(tp.label)}</td>
      <td class="prov ${tp.provenance}">${tp.provenance}</td>
      <td>${escapeHtml(tp.summary)}</td>
    </tr>
  `).join("");

  const tabs = (c.usable_formats || []).map((fmt, i) => `
    <div class="tab${i === 0 ? ' active' : ''}" data-fmt="${escapeHtml(fmt)}">${escapeHtml(fmt)}</div>
  `).join("");
  const firstFmt = (c.usable_formats || [])[0];
  const firstHook = firstFmt ? (c.adaptation_hooks || {})[firstFmt] : "";

  const pressureCtxChips = (c.world_pressure_context || []).map(p =>
    `<span class="chip">${escapeHtml(p)}</span>`
  ).join("") || `<span class="chip">(none)</span>`;

  const relationshipBlock = (c.relationship_dynamics || []).length
    ? `<ul>${c.relationship_dynamics.map(r => `<li>${escapeHtml(r)}</li>`).join("")}</ul>`
    : `<em class="empty">(none recorded)</em>`;

  const evidenceRows = ((CANDS_PAYLOAD && CANDS_PAYLOAD.candidates) || [])
    .find(x => x.story_candidate_id === cid)
    ? (c.key_turning_points || []).map(tp => `
        <li><code>t${tp.tick}</code> · <code>${tp.provenance}</code> · ${escapeHtml(tp.summary)}</li>
      `).join("")
    : "";

  const provSummary = c.provenance_summary || {};
  const provLine = Object.entries(provSummary)
    .filter(([k, v]) => v > 0)
    .map(([k, v]) => `<span class="chip">${k}: ${v}</span>`)
    .join("");

  const riskLines = (c.risk_notes || []).map(r => `<li>${escapeHtml(r)}</li>`).join("");

  const mainNames = (c.main_characters || []).join(", ") || "(world-level)";
  const supporting = (c.supporting_characters_or_groups || []).join(", ") || "(none)";

  detail.innerHTML = `
    <h2><span class="id-prefix">${c.story_candidate_id} · </span>${escapeHtml(c.title)}</h2>
    <div class="badges-row">
      <span class="badge-meta">conflict <strong>${escapeHtml(c.core_conflict)}</strong></span>
      ${conflictBadge}
      <span class="badge-meta">main <strong>${escapeHtml(mainNames)}</strong></span>
      <span class="badge-meta">supporting <strong>${escapeHtml(supporting)}</strong></span>
      <span class="badge-meta">source thread <strong>${escapeHtml(c.source_thread_id)}</strong></span>
    </div>

    <section>
      <h3>One-line premise</h3>
      <p class="premise">${escapeHtml(c.one_line_premise)}</p>
    </section>

    <section>
      <h3>Arc summary</h3>
      <p class="arc">${escapeHtml(c.arc_summary)}</p>
    </section>

    <section>
      <h3>Unresolved question</h3>
      <p class="question">${escapeHtml(c.unresolved_question)}</p>
    </section>

    <section>
      <h3>Key turning points</h3>
      <table class="turning">
        <thead>
          <tr><th>Tick</th><th>Label</th><th>Provenance</th><th>Summary</th></tr>
        </thead>
        <tbody>${turningRows || `<tr><td colspan="4">(none selected)</td></tr>`}</tbody>
      </table>
    </section>

    <section>
      <h3>Relationship dynamics</h3>
      ${relationshipBlock}
    </section>

    <section>
      <h3>World pressure context</h3>
      <div class="chip-row">${pressureCtxChips}</div>
    </section>

    <section>
      <h3>Adaptation hooks</h3>
      <div class="tabs" id="tabs-${cid}">${tabs || ""}</div>
      <div class="tab-content" id="tab-content-${cid}">
        ${firstHook ? escapeHtml(firstHook) : "<em>(no creative-use hooks for this conflict)</em>"}
      </div>
    </section>

    <section>
      <h3>Evidence</h3>
      <p>${escapeHtml(c.evidence_summary || "")}</p>
      <div class="chip-row" style="margin-top:6px">${provLine}</div>
      <details class="evidence" style="margin-top:8px">
        <summary>Show per-tick provenance</summary>
        <div class="evidence-body">
          <ul>${evidenceRows || "<li><em>no per-tick evidence</em></li>"}</ul>
        </div>
      </details>
    </section>

    <section>
      <h3>Risk notes</h3>
      <ul>${riskLines}</ul>
    </section>
  `;

  // Tab interactivity
  const tabsRoot = document.getElementById(`tabs-${cid}`);
  if (tabsRoot) {
    for (const t of tabsRoot.querySelectorAll(".tab")) {
      t.addEventListener("click", () => {
        for (const o of tabsRoot.querySelectorAll(".tab")) o.classList.remove("active");
        t.classList.add("active");
        const fmt = t.dataset.fmt;
        const hook = (c.adaptation_hooks || {})[fmt] || "";
        document.getElementById(`tab-content-${cid}`).textContent = hook;
      });
    }
  }
}

function escapeHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Auto-select first candidate
if (CANDS.length > 0) {
  selectCandidate(CANDS[0].story_candidate_id);
}
</script>
</body>
</html>
"""


def _load_or_empty(p: Path, default: dict) -> dict:
    if not p.exists():
        return default
    loaded = json.loads(p.read_text(encoding="utf-8"))
    if not loaded:
        return default
    out = dict(default); out.update(loaded); return out


def main(in_cands: str, in_xs: str, out_html: str) -> None:
    cands = _load_or_empty(Path(in_cands), {
        "run_label": "unknown", "candidates": [],
    })
    xs = _load_or_empty(Path(in_xs), {})
    meta = {"build_time_iso": "static"}

    html = HTML_TEMPLATE
    html = html.replace("__CANDS__", json.dumps(cands, ensure_ascii=False))
    html = html.replace("__XS__", json.dumps(xs, ensure_ascii=False))
    html = html.replace("__META__", json.dumps(meta, ensure_ascii=False))

    out = Path(out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(
        f"Wrote {out_html} ({len(html)} bytes, {len(cands.get('candidates', []))} candidates embedded)"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cands",
                    default="data/narrative/story_candidates.json")
    ap.add_argument("--xs",
                    default="data/narrative/cross_seed_story_patterns.json")
    ap.add_argument("--out",
                    default="docs/portfolio/story_candidate_console.html")
    ns = ap.parse_args()
    main(ns.cands, ns.xs, ns.out)


if __name__ == "__main__":
    cli()
