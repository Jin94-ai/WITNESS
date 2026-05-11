"""Phase 3.1 §28 — flesh_baseline_output.json → portfolio demo (self-contained HTML + MD).

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §27 + §28 + §29.

산출:
    {output_dir}/index.html        (self-contained, 외부 CDN 0)
    {output_dir}/baseline.md       (human-readable)
    {output_dir}/flesh_baseline_output.json (machine-readable copy)

원칙:
    - raw text 노출 0 (audit.raw_text_used == False)
    - score는 설명 가능하게 표시 (reason_features + score_breakdown)
    - rule-based adapter 연결 명시 (recommended_adapter)
    - Phase 3.0 통과 전이면 prep 표시 (data_source == "rulebook_only")

사용:
    python scripts/narrative/build_flesh_baseline_demo.py \\
        --skeleton docs/portfolio/demo/skeleton_output.json \\
        --baseline data/narrative/phase3_1_demo/flesh_baseline_output.json \\
        --output docs/portfolio/demo_flesh_baseline
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


from scripts.narrative.apply_genre_adapter import _load_skeleton_output  # noqa: E402


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Per-seed top recommendation grouping
# ---------------------------------------------------------------------------

def group_by_seed(recommendations: list[dict]) -> dict[str, list[dict]]:
    """{seed_id → [recs sorted by score desc]}"""
    by_seed: dict[str, list[dict]] = {}
    for rec in recommendations:
        sid = rec.get("source_seed_id", "")
        by_seed.setdefault(sid, []).append(rec)
    for sid, recs in by_seed.items():
        recs.sort(key=lambda r: -float(r.get("score", 0)))
    return by_seed


def fit_class(label: str) -> str:
    return {
        "strong_fit": "fit-strong",
        "moderate_fit": "fit-moderate",
        "weak_fit": "fit-weak",
        "no_fit": "fit-no",
    }.get(label, "fit-unknown")


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def render_markdown(skeleton, baseline: dict) -> str:
    lines: list[str] = []
    lines.append("# Phase 3.1 Flesh Baseline — Recommendations")
    lines.append("")
    model = baseline.get("model", {})
    is_rulebook_only = (model.get("data_source") == "rulebook_only")
    if is_rulebook_only:
        lines.append(
            "> **📐 Prep mode (rulebook-only)** — 현재 점수는 *실제 annotation 기반 추천이 아니라* "
            "rulebook compatibility (seed의 conflict_axis / dominant_pressures가 장르 rulebook과 호환되는 정도)다. "
            "Phase 3.0 pilot 데이터가 들어와야 annotation component가 추가되어 *data-backed* recommendation이 된다. "
            "현재 fit_label은 **compatibility match**로 해석해야 안전하다."
        )
        lines.append("")
    lines.append(f"> **schema**: `{baseline['schema_version']}`  ")
    lines.append(f"> **source skeleton**: `{baseline['source_skeleton_id']}` ({baseline['source_skeleton_version']})  ")
    lines.append(f"> **profiles**: {', '.join(baseline['genre_profiles_used'])}  ")
    model = baseline.get("model", {})
    lines.append(
        f"> **model**: {model.get('type', '?')} "
        f"(trained={model.get('trained')}, data_source={model.get('data_source')})"
    )
    audit = baseline.get("audit", {})
    lines.append(
        f"> **audit**: raw_text_used={audit.get('raw_text_used')} / "
        f"evidence_preserved={audit.get('evidence_preserved')}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    by_seed = group_by_seed(baseline["recommendations"])
    skeleton_seed_ids = [s.seed_id for s in skeleton.seeds]
    label_suffix = " (rulebook-only)" if is_rulebook_only else ""

    lines.append("## Seed별 Top Recommendation")
    lines.append("")
    for sid in skeleton_seed_ids:
        recs = by_seed.get(sid, [])
        if not recs:
            continue
        top = recs[0]
        seed = next((s for s in skeleton.seeds if s.seed_id == sid), None)
        flow_role = seed.flow_role if seed else "?"
        axis = seed.conflict_axis_id if seed else "?"
        lines.append(f"### {sid} [{flow_role}] (`{axis}`)")
        lines.append("")
        lines.append(
            f"- **추천 장르**: `{top['genre_id']}`"
        )
        lines.append(
            f"- **점수**: {top['score']:.3f} ({top['fit_label']}{label_suffix})"
        )
        bd = top.get("score_breakdown") or {}
        if bd:
            ann_score = bd.get("annotation_score")
            ann_str = (
                f"{ann_score:.4f}" if isinstance(ann_score, (int, float))
                else "not available yet"
            )
            lines.append(
                f"- **score_breakdown**: mode=`{bd.get('mode', '?')}` · "
                f"compatibility={bd.get('compatibility_score', 0):.3f} "
                f"(axis={bd.get('axis_match', 0):.2f}, pressure={bd.get('pressure_overlap', 0):.2f}) · "
                f"annotation={ann_str}"
            )
        if top.get("reason_features"):
            lines.append(
                f"- **이유**: {', '.join(top['reason_features'])}"
            )
        lines.append(
            f"- **추천 어댑터**: `{top.get('recommended_adapter', '?')}`"
        )
        if len(recs) > 1:
            lines.append("- **다른 후보**:")
            for alt in recs[1:]:
                lines.append(
                    f"  - `{alt['genre_id']}`: {alt['score']:.3f} ({alt['fit_label']}{label_suffix})"
                )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 전체 Recommendation Matrix")
    lines.append("")
    lines.append("| seed | genre | score | fit | top reason |")
    lines.append("|---|---|---|---|---|")
    for rec in baseline["recommendations"]:
        reason = (rec.get("reason_features") or [""])[0]
        lines.append(
            f"| {rec['source_seed_id']} | `{rec['genre_id']}` | "
            f"{rec['score']:.3f} | {rec['fit_label']}{label_suffix} | {reason} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Audit")
    lines.append("")
    lines.append(f"- raw_text_used: `{audit.get('raw_text_used')}`")
    lines.append(f"- evidence_preserved: `{audit.get('evidence_preserved')}`")
    lines.append(f"- model_trained: `{model.get('trained')}`")
    lines.append(f"- model_type: `{model.get('type')}`")
    lines.append(f"- data_source: `{model.get('data_source')}`")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML render (self-contained)
# ---------------------------------------------------------------------------

def render_html(skeleton, baseline: dict) -> str:
    by_seed = group_by_seed(baseline["recommendations"])
    skeleton_seed_ids = [s.seed_id for s in skeleton.seeds]
    n_seeds = len(skeleton_seed_ids)
    n_profiles = len(baseline.get("genre_profiles_used", []))
    audit = baseline.get("audit", {})
    model = baseline.get("model", {})

    raw_safe_class = (
        "audit-pass" if audit.get("raw_text_used") is False else "audit-fail"
    )
    evidence_class = (
        "audit-pass" if audit.get("evidence_preserved") is True else "audit-fail"
    )

    # data_source banner (Phase 3.0 통과 전이면 prep 표시)
    data_source = model.get("data_source", "")
    is_rulebook_only = (data_source == "rulebook_only")
    if is_rulebook_only:
        data_source_banner = (
            '<div class="prep-banner">'
            "<strong>📐 Prep mode — rulebook-only</strong><br>"
            "현재 점수는 <em>실제 annotation 기반 추천이 아니라</em> rulebook compatibility "
            "(seed의 conflict_axis / dominant_pressures가 장르 rulebook과 호환되는 정도)다. "
            "Phase 3.0 pilot annotation 데이터가 들어와야 annotation component가 추가되어 "
            "*data-backed* recommendation이 된다. "
            "현재 fit_label은 <code>compatibility match</code>로 해석해야 안전하다."
            "</div>"
        )
    elif data_source == "phase3_pilot":
        data_source_banner = (
            '<div class="data-banner">'
            "<strong>📊 Phase 3.0 pilot 데이터 적용 완료</strong> — KEEP feature 기반 "
            "weighted score + rulebook compatibility 결합."
            "</div>"
        )
    else:
        data_source_banner = ""

    # Seed cards (top recommendation per seed + alternatives)
    seed_cards = []
    for sid in skeleton_seed_ids:
        recs = by_seed.get(sid, [])
        if not recs:
            continue
        seed = next((s for s in skeleton.seeds if s.seed_id == sid), None)
        flow_role = seed.flow_role if seed else "?"
        axis = seed.conflict_axis_id if seed else "?"
        archetype = seed.main_archetype if seed else "?"

        top = recs[0]
        reasons_html = ""
        if top.get("reason_features"):
            reasons_html = (
                '<div class="reasons">'
                + "".join(
                    f'<span class="reason">{_esc(r)}</span>'
                    for r in top["reason_features"]
                )
                + "</div>"
            )

        breakdown_html = ""
        bd = top.get("score_breakdown") or {}
        if bd:
            mode = bd.get("mode", "")
            ann_score = bd.get("annotation_score")
            ann_score_str = (
                f"{ann_score:.4f}" if isinstance(ann_score, (int, float))
                else "not available yet"
            )
            breakdown_html = (
                '<details><summary>score breakdown</summary><ul>'
                f'<li><strong>mode</strong>: <code>{_esc(str(mode))}</code></li>'
                f'<li>compatibility_score: {bd.get("compatibility_score", 0):.4f}'
                f' (axis_match={bd.get("axis_match", 0):.2f}, '
                f'pressure_overlap={bd.get("pressure_overlap", 0):.2f})</li>'
                f'<li>annotation_score: {ann_score_str}</li>'
                f'<li>final_score: {bd.get("final_score", 0):.4f}</li>'
                + "</ul></details>"
            )

        alt_html = ""
        if len(recs) > 1:
            alt_lines = []
            for alt in recs[1:]:
                alt_lines.append(
                    f'<li><code>{_esc(alt["genre_id"])}</code> · '
                    f'<span class="score">{alt["score"]:.3f}</span> · '
                    f'<span class="fit-tag {fit_class(alt["fit_label"])}">{_esc(alt["fit_label"])}</span></li>'
                )
            alt_html = (
                '<details><summary>다른 장르 후보</summary><ul>'
                + "".join(alt_lines) + "</ul></details>"
            )

        fit_class_str = fit_class(top["fit_label"])
        # Phase 3.05: rulebook_only이면 fit_label에 "(rulebook-only)" 명시
        fit_label_top = (
            f"{top['fit_label']} (rulebook-only)" if is_rulebook_only
            else top['fit_label']
        )
        seed_cards.append(f"""
        <article class="seed-card">
          <header>
            <h3>{_esc(sid)}</h3>
            <small class="muted">[{_esc(flow_role)}] · {_esc(archetype)}<br>
            갈등 축: <code>{_esc(axis)}</code></small>
          </header>
          <div class="recommendation">
            <div class="rec-genre">
              <span class="genre-id">{_esc(top['genre_id'])}</span>
              <span class="fit-tag {fit_class_str}">{_esc(fit_label_top)}</span>
            </div>
            <div class="rec-score">
              <span class="score-value">{top['score']:.3f}</span>
              <span class="muted small">/ 1.000</span>
            </div>
            {reasons_html}
            <div class="muted small">
              어댑터: <code>{_esc(top.get('recommended_adapter', '?'))}</code>
            </div>
            {breakdown_html}
            {alt_html}
          </div>
        </article>""")

    # Recommendation matrix table
    matrix_rows = []
    for rec in baseline["recommendations"]:
        reason = ", ".join(rec.get("reason_features", [])[:2])
        fit_label_row = (
            f"{rec['fit_label']} (rulebook-only)" if is_rulebook_only
            else rec['fit_label']
        )
        matrix_rows.append(f"""
        <tr>
          <td><strong>{_esc(rec['source_seed_id'])}</strong></td>
          <td><code>{_esc(rec['genre_id'])}</code></td>
          <td class="score-cell">{rec['score']:.3f}</td>
          <td><span class="fit-tag {fit_class(rec['fit_label'])}">{_esc(fit_label_row)}</span></td>
          <td class="muted small">{_esc(reason)}</td>
        </tr>""")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>WITNESS · Phase 3.1 Flesh Baseline — 장르 fit score</title>
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

  .prep-banner, .data-banner {{ padding: 0.9em 1.2em; border-radius: 7px;
                                margin: 1.2em 0; }}
  .prep-banner {{ background: #fdf3e3; border-left: 4px solid #c9a55a; }}
  .data-banner {{ background: #e9f5ec; border-left: 4px solid #2c6c3d; }}

  .audit-row {{ background: #f0ede5; padding: 0.8em 1em; border-radius: 7px;
                margin: 1em 0 1.5em; display: flex; gap: 1.5em; flex-wrap: wrap; }}
  .audit-tag {{ display: inline-block; padding: 0.3em 0.8em; border-radius: 4px;
                font-weight: 600; font-size: 0.92em; }}
  .audit-pass {{ background: #e9f5ec; color: #2c6c3d; }}
  .audit-fail {{ background: #fbe9e9; color: #a23030; }}

  .seed-grid {{ display: grid;
                grid-template-columns: repeat({n_seeds}, 1fr);
                gap: 1em; margin: 1em 0 2em; }}
  @media (max-width: 980px) {{
    .seed-grid {{ grid-template-columns: 1fr 1fr; }}
  }}
  @media (max-width: 600px) {{
    .seed-grid {{ grid-template-columns: 1fr; }}
  }}
  .seed-card {{ background: #fff; padding: 1em 1.2em; border-radius: 8px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
  .seed-card h3 {{ margin: 0 0 0.2em; font-size: 1.15em; }}
  .seed-card header {{ border-bottom: 1px solid #eee; padding-bottom: 0.5em;
                       margin-bottom: 0.7em; }}
  .recommendation {{ margin-top: 0.5em; }}
  .rec-genre {{ display: flex; align-items: center; gap: 0.5em;
                margin-bottom: 0.4em; }}
  .genre-id {{ font-weight: 600; font-family: ui-monospace, monospace;
               font-size: 0.95em; }}
  .rec-score {{ margin: 0.4em 0; }}
  .score-value {{ font-size: 1.5em; font-weight: 600; color: #444; }}
  .reasons {{ margin: 0.6em 0; }}
  .reason {{ display: inline-block; padding: 0.15em 0.55em; margin: 0.15em 0.2em 0.15em 0;
             background: #f5f1e8; border-radius: 3px; font-size: 0.85em;
             font-family: ui-monospace, monospace; }}

  .fit-tag {{ display: inline-block; padding: 0.15em 0.55em; border-radius: 3px;
              font-size: 0.82em; font-weight: 600; }}
  .fit-strong {{ background: #e9f5ec; color: #2c6c3d; }}
  .fit-moderate {{ background: #f5f1e8; color: #846020; }}
  .fit-weak {{ background: #fdf3e3; color: #946a1f; }}
  .fit-no {{ background: #f3f3f3; color: #666; }}

  details {{ margin: 0.6em 0; padding: 0.6em 0.8em; background: #faf8f3;
             border-radius: 5px; }}
  summary {{ cursor: pointer; font-weight: 600; font-size: 0.88em; }}
  details ul {{ margin: 0.4em 0 0; padding-left: 1.2em; font-size: 0.88em; }}
  details code {{ font-size: 0.85em; }}

  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ text-align: left; padding: 0.5em 0.7em; border-bottom: 1px solid #eee;
           vertical-align: top; }}
  th {{ background: rgba(0,0,0,0.04); font-weight: 600; }}
  .score-cell {{ font-family: ui-monospace, monospace; }}

  footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #e0dcd0;
            color: #999; font-size: 0.85em; }}
</style>
</head>
<body>

<header class="page-head">
  <h1>WITNESS · Phase 3.1 Flesh Baseline</h1>
  <p class="lead">universal skeleton의 각 seed가 어떤 장르 flesh와 잘 맞는지를
    *설명 가능한 weighted score*로 점수화한다. ML / fine-tuning 0.</p>
</header>

{data_source_banner}

<div class="audit-row">
  <span class="audit-tag {raw_safe_class}">raw_text_used: {str(audit.get('raw_text_used')).lower()}</span>
  <span class="audit-tag {evidence_class}">evidence_preserved: {str(audit.get('evidence_preserved')).lower()}</span>
  <span class="audit-tag {'audit-pass' if not model.get('trained') else 'audit-fail'}">model.trained: {str(model.get('trained')).lower()}</span>
  <span class="muted small">model.type: <code>{_esc(model.get('type', '?'))}</code></span>
  <span class="muted small">data_source: <code>{_esc(model.get('data_source', '?'))}</code></span>
</div>

<h2>Seed별 Top Recommendation</h2>
<p class="muted small">각 universal seed에 가장 잘 맞는 장르 + 점수 근거 (compatibility + annotation 결합).</p>

<section class="seed-grid">
  {''.join(seed_cards)}
</section>

<h2>전체 Recommendation Matrix</h2>
<p class="muted small">{n_seeds} seeds × {n_profiles} profiles = {len(baseline['recommendations'])} 개 recommendations.</p>
<table>
  <thead>
    <tr><th>seed</th><th>genre</th><th>score</th><th>fit</th><th>top reason</th></tr>
  </thead>
  <tbody>
    {''.join(matrix_rows)}
  </tbody>
</table>

<details>
  <summary>Score 공식 (설명 가능)</summary>
  <ul style="margin-top:0.5em">
    <li><strong>compatibility (50%)</strong> = axis 매칭 (0.5) + dominant_pressures × profile.compatible_pressures overlap × 0.5</li>
    <li><strong>annotation (50%)</strong> = Σ(feature_score normalized × profile.feature_weight)</li>
    <li>annotation이 없으면 compatibility-only fallback (Phase 3.0 통과 전 상태)</li>
    <li>fit_label: ≥ 0.7 strong / ≥ 0.5 moderate / ≥ 0.25 weak / 그 외 no_fit</li>
  </ul>
</details>

<details>
  <summary>Technical Appendix</summary>
  <ul style="margin-top:0.5em">
    <li>schema: <code>{_esc(baseline['schema_version'])}</code></li>
    <li>source skeleton: <code>{_esc(baseline['source_skeleton_id'])}</code> ({_esc(baseline['source_skeleton_version'])})</li>
    <li>profiles used: <code>{_esc(', '.join(baseline['genre_profiles_used']))}</code></li>
    <li>model: <code>{_esc(model.get('type', '?'))}</code> · trained={str(model.get('trained')).lower()}</li>
    <li>raw text 사용 0 / 학습 0 / fine-tuning 0 / 대사 생성 0</li>
    <li>각 score는 코드 + JSON으로 추적 가능 (ablation baseline으로 그대로 사용 가능)</li>
  </ul>
</details>

<footer>
  <p>WITNESS Phase 3.1 prep · No-ML weighted rule score · 설명 가능한 baseline.<br>
     CLI: <code>scripts/narrative/build_genre_profiles.py</code> + <code>run_flesh_baseline.py</code> + <code>build_flesh_baseline_demo.py</code></p>
</footer>

</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True, type=Path,
                     help="SkeletonOutput JSON (e.g. docs/portfolio/demo/skeleton_output.json)")
    ap.add_argument("--baseline", required=True, type=Path,
                     help="flesh_baseline_output.json (run_flesh_baseline.py 출력)")
    ap.add_argument("--output", required=True, type=Path,
                     help="output dir (e.g. docs/portfolio/demo_flesh_baseline)")
    args = ap.parse_args(argv)

    if not args.skeleton.exists():
        print(f"ERROR: skeleton not found: {args.skeleton}", file=sys.stderr)
        return 2
    if not args.baseline.exists():
        print(f"ERROR: baseline not found: {args.baseline}", file=sys.stderr)
        return 2

    skeleton = _load_skeleton_output(args.skeleton)
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))

    args.output.mkdir(parents=True, exist_ok=True)
    html_path = args.output / "index.html"
    md_path = args.output / "baseline.md"
    json_path = args.output / "flesh_baseline_output.json"

    html_path.write_text(render_html(skeleton, baseline), encoding="utf-8")
    md_path.write_text(render_markdown(skeleton, baseline), encoding="utf-8")
    # mirror baseline JSON
    json_path.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    print(f"OK: flesh baseline demo → {args.output}")
    print(f"  html: {html_path.name}")
    print(f"  md:   {md_path.name}")
    print(f"  json: {json_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
