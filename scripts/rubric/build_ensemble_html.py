"""Rubric Cross-Scenario Ensemble HTML Generator (Phase 3.05).

여러 ensemble JSON (multi_seed / multi_agent / cross_scenario)을 읽어서
self-contained portfolio HTML로 시각화.

원칙 (Phase 3.05 Non-Claims):
    - Discovery class는 *candidate*. Truth claim 아님.
    - 모든 threshold uncalibrated_phase3_placeholder.
    - Rule #14: rubric은 evaluation-only.

사용:
    python scripts/rubric/build_ensemble_html.py \\
        --ensembles cross_scenario_ensemble.json multi_seed_ensemble.json \\
        --output docs/portfolio/demo_rubric/ensemble_visualization.html
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace",
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace",
            )
        except Exception:
            pass


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _class_color(cls: str) -> str:
    """discovery_class별 색상."""
    return {
        "character_consistent_novel_candidate": "#2c6c3d",  # green (positive)
        "canonical_reproduction": "#3c6e90",                # blue
        "canon_compatible_character_drift": "#a07a3c",      # amber
        "not_discovery_noise": "#a04040",                   # red
        "not_discovery_incoherent": "#7a3aa0",              # purple
        "invalid_canon_violation": "#7a3a3a",               # dark red
        "not_discovery_hardcoded": "#888",                  # gray
    }.get(cls, "#666")


def render_ensemble_card(ensemble_data: dict, ensemble_name: str) -> str:
    """단일 ensemble JSON → HTML card."""
    meta = ensemble_data.get("meta", {})

    # Aggregate distribution (overall + per breakdown)
    overall = ensemble_data.get("overall_distribution") or ensemble_data.get("distribution", {})
    total = sum(overall.values())

    # 핵심 class 통계
    pos_count = overall.get("character_consistent_novel_candidate", 0)
    pos_pct = (100 * pos_count / total) if total else 0

    # Per-breakdown (per_agent / per_context / per_seed)
    per_agent = ensemble_data.get("per_agent", {})
    per_context = ensemble_data.get("per_context", {})
    per_seed = ensemble_data.get("per_seed", [])

    breakdown_html = ""
    if per_context:
        breakdown_html += '<h4>Per agent context</h4><table class="breakdown"><thead><tr><th>Context</th><th>Distribution</th></tr></thead><tbody>'
        for ctx, dist in per_context.items():
            dist_str = " · ".join(f'<span class="cls-tag" style="background:{_class_color(c)}">{_esc(c)}={n}</span>' for c, n in dist.items())
            breakdown_html += f'<tr><td><code>{_esc(ctx)}</code></td><td>{dist_str}</td></tr>'
        breakdown_html += '</tbody></table>'
    elif per_agent:
        breakdown_html += '<h4>Per agent</h4><table class="breakdown"><thead><tr><th>Agent</th><th>Distribution</th></tr></thead><tbody>'
        for ag, info in per_agent.items():
            dist = info.get("distribution", {})
            dist_str = " · ".join(f'<span class="cls-tag" style="background:{_class_color(c)}">{_esc(c)}={n}</span>' for c, n in dist.items())
            breakdown_html += f'<tr><td><code>{_esc(ag)}</code></td><td>{dist_str}</td></tr>'
        breakdown_html += '</tbody></table>'
    elif per_seed:
        breakdown_html += '<h4>Per seed</h4><table class="breakdown"><thead><tr><th>Seed</th><th>discovery_class</th><th>Character</th><th>Causal</th></tr></thead><tbody>'
        for entry in per_seed:
            s = entry.get("seed", "?")
            cls = entry.get("discovery_class", "?")
            ch = "✓" if entry.get("character_passed") else "✗"
            cg = "✓" if entry.get("causal_gate") else "✗"
            breakdown_html += f'<tr><td>{s}</td><td><span class="cls-tag" style="background:{_class_color(cls)}">{_esc(cls)}</span></td><td>{ch}</td><td>{cg}</td></tr>'
        breakdown_html += '</tbody></table>'

    # Overall distribution as bar
    overall_html = '<div class="overall-dist">'
    for cls, n in sorted(overall.items(), key=lambda x: -x[1]):
        pct = (100 * n / total) if total else 0
        overall_html += (
            f'<div class="dist-row">'
            f'<span class="cls-name">{_esc(cls)}</span>'
            f'<div class="dist-bar-track"><div class="dist-bar-fill" '
            f'style="width:{pct:.1f}%; background:{_class_color(cls)}"></div></div>'
            f'<span class="dist-count">{n}/{total} ({pct:.0f}%)</span>'
            f'</div>'
        )
    overall_html += '</div>'

    # Axis means (if present)
    axis_means = ensemble_data.get("axis_means", {})
    axis_html = ""
    if axis_means:
        axis_html += '<h4>Per-axis means</h4><table class="axis-means"><tbody>'
        for k, v in axis_means.items():
            axis_html += f'<tr><td><code>{_esc(k)}</code></td><td class="axis-val">{v:.3f}</td></tr>'
        axis_html += '</tbody></table>'

    headline = (
        f'<span class="headline-pct">{pos_pct:.0f}%</span> '
        f'<span class="headline-label">character_consistent_novel_candidate</span>'
    )

    return f"""
<article class="ensemble-card">
  <header>
    <h3>{_esc(ensemble_name)}</h3>
    <small class="muted">{_esc(meta.get('tool', ''))}<br>
    Generated: {_esc(meta.get('generated', '?'))}<br>
    Total: {total} reports</small>
  </header>
  <div class="headline">{headline}</div>
  {overall_html}
  {axis_html}
  {breakdown_html}
</article>"""


def render_html(ensembles: list[tuple[str, dict]]) -> str:
    """모든 ensemble cards 합쳐서 self-contained HTML."""
    cards = "".join(
        render_ensemble_card(data, name) for name, data in ensembles
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>WITNESS · Rubric Cross-Scenario Ensemble Visualization (Phase 3.05)</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          max-width: 1200px; margin: 1.5em auto; padding: 0 1em; line-height: 1.55;
          color: #222; background: #fafaf7; }}
  header.page-head h1 {{ font-size: 1.85em; margin: 0 0 0.3em 0; }}
  header.page-head .lead {{ font-size: 1.05em; color: #444; }}
  .muted {{ color: #777; }}
  .small {{ font-size: 0.88em; }}
  code {{ background: #efece4; padding: 1px 5px; border-radius: 3px; font-size: 0.88em; }}

  .non-claims-banner {{ background: #fdf3e3; border-left: 4px solid #c9a55a;
                         padding: 0.9em 1.2em; border-radius: 7px;
                         margin: 1.2em 0; }}
  .non-claims-banner strong {{ color: #946a1f; }}

  .ensemble-card {{ background: #fff; padding: 1.5em; border-radius: 8px;
                     box-shadow: 0 1px 4px rgba(0,0,0,0.06); margin: 1.5em 0; }}
  .ensemble-card h3 {{ margin: 0 0 0.3em; font-size: 1.3em; }}
  .ensemble-card header {{ border-bottom: 1px solid #eee; padding-bottom: 0.7em;
                            margin-bottom: 1em; }}

  .headline {{ font-size: 1.1em; margin: 1em 0; padding: 0.6em 1em;
                background: #e9f5ec; border-left: 4px solid #2c6c3d;
                border-radius: 5px; }}
  .headline-pct {{ font-size: 1.4em; font-weight: 700; color: #2c6c3d; }}
  .headline-label {{ color: #555; font-family: ui-monospace, monospace;
                      font-size: 0.95em; }}

  .overall-dist {{ margin: 1em 0; }}
  .dist-row {{ display: flex; align-items: center; gap: 0.6em; margin: 0.3em 0; }}
  .cls-name {{ flex: 0 0 280px; font-family: ui-monospace, monospace; font-size: 0.85em; }}
  .dist-bar-track {{ flex: 1; height: 18px; background: #efece4;
                      border-radius: 3px; overflow: hidden; min-width: 100px; }}
  .dist-bar-fill {{ height: 100%; transition: width 0.3s; }}
  .dist-count {{ flex: 0 0 100px; text-align: right; color: #555;
                  font-family: ui-monospace, monospace; font-size: 0.88em; }}

  .cls-tag {{ display: inline-block; padding: 0.15em 0.55em; border-radius: 3px;
              color: #fff; font-size: 0.78em; font-family: ui-monospace, monospace;
              margin: 0.1em 0.15em; }}

  table {{ border-collapse: collapse; width: 100%; margin: 0.8em 0; }}
  th, td {{ text-align: left; padding: 0.4em 0.7em; border-bottom: 1px solid #eee;
           vertical-align: middle; font-size: 0.92em; }}
  th {{ background: rgba(0,0,0,0.04); font-weight: 600; }}
  .axis-val {{ font-family: ui-monospace, monospace; text-align: right; }}
  .breakdown td:first-child {{ width: 200px; }}

  h4 {{ margin: 1em 0 0.4em; font-size: 1em; color: #555; }}

  details {{ margin: 0.8em 0; padding: 0.7em 1em; background: #faf8f3;
             border-radius: 5px; }}
  summary {{ cursor: pointer; font-weight: 600; }}

  footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #e0dcd0;
            color: #999; font-size: 0.85em; }}
</style>
</head>
<body>

<header class="page-head">
  <h1>WITNESS · Rubric Cross-Scenario Ensemble Visualization</h1>
  <p class="lead">4-Axis Discovery <strong>Candidate Classifier</strong> 결과 — multi-seed / multi-agent / cross-scenario ensemble.
    실제 simulation trace에 rubric 적용 (합성 fixture 아님).</p>
</header>

<div class="non-claims-banner">
  <strong>📐 Non-Claims (review §3)</strong><br>
  이 visualization은 *결과물 시연*이다. 다음을 <em>증명하지 않는다</em>: 신학적 정답 / 문학적 완성도 / 진리 주장.
  <br>최종 label은 <strong>discovery candidate class</strong>로 해석. 모든 threshold는 <code>uncalibrated_phase3_placeholder</code>.
  <br>Rule #14: Rubric은 evaluation-only (학습 loss 사용 0).
</div>

{cards}

<details>
  <summary>Discovery class 의미 (Phase 3.05 review)</summary>
  <ul>
    <li><strong>character_consistent_novel_candidate</strong> (Step 7, review §2.1 P0) — novelty meaningful + character signature pass + scene_fit pass</li>
    <li><strong>canonical_reproduction</strong> (Step 6) — 정경 sequence 충실 재생</li>
    <li><strong>canon_compatible_character_drift</strong> (Step 8) — canon valid, character ✓이지만 full novel tier 미달</li>
    <li><strong>not_discovery_incoherent</strong> (Step 3, review §2.2 P0) — causal gate fail</li>
    <li><strong>not_discovery_noise</strong> (Step 4-5) — context_break high 또는 novelty noise</li>
    <li><strong>not_discovery_hardcoded</strong> (Step 1) — hardcoded firing</li>
    <li><strong>invalid_canon_violation</strong> (Step 2) — hard canon violation</li>
  </ul>
</details>

<details>
  <summary>Phase 3.05 Rubric directive 결과물 진화 (10단계)</summary>
  <ol>
    <li>CLI runner (`scripts/rubric/run_rubric.py`)</li>
    <li>single demo (`peter_synthetic_trace`)</li>
    <li>3-variants</li>
    <li>4-variants</li>
    <li>5-variants positive (`peter_meaningful_novel` — review §2.1 P0 도달)</li>
    <li>8-variants all endpoints (review §2.2 P0 입증)</li>
    <li>real simulation single seed</li>
    <li>multi-seed ensemble (review §H8)</li>
    <li>multi-agent ensemble</li>
    <li>cross-scenario ensemble (engine generality 입증)</li>
  </ol>
</details>

<footer>
  <p>WITNESS Phase 3.05 · Rubric Cross-Scenario Ensemble Visualization · 2026-05-11.<br>
     Source: <code>docs/portfolio/demo_rubric/*_ensemble.json</code> · CLI: <code>scripts/rubric/build_ensemble_html.py</code></p>
</footer>

</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ensembles", nargs="+", required=True, type=Path,
                     help="ensemble JSON 경로들")
    ap.add_argument("--output", required=True, type=Path,
                     help="HTML output 경로")
    args = ap.parse_args(argv)

    ensembles: list[tuple[str, dict]] = []
    for path in args.ensembles:
        if not path.exists():
            print(f"WARN: ensemble 미존재: {path}", file=sys.stderr)
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        # name = filename stem
        ensembles.append((path.stem, d))

    if not ensembles:
        print("ERROR: ensemble 0건", file=sys.stderr)
        return 2

    html = render_html(ensembles)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(f"OK: {len(ensembles)} ensembles → {args.output}")
    print(f"  size: {len(html)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
