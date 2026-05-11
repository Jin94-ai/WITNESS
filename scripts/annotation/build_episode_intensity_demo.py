"""Phase 3.1 §22.2 + §28 — episode_intensity.json → portfolio demo (self-contained HTML + MD).

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22.2 + §28.

산출:
    {output_dir}/index.html              (self-contained, 외부 CDN 0)
    {output_dir}/intensity.md            (human-readable)
    {output_dir}/episode_intensity.json  (machine-readable copy)

원칙:
    - raw text 노출 0 (audit.raw_text_used == False)
    - score는 설명 가능하게 표시 (feature_contributions breakdown)
    - record_id에서 title prefix만 노출 (synopsis_text / source_url 없음)
    - Phase 3.0 통과 전 fixture demo이면 prep 표시

사용:
    python scripts/annotation/build_episode_intensity_demo.py \\
        --intensity data/annotation/phase3_pilot/episode_intensity.json \\
        --output docs/portfolio/demo_episode_intensity
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import defaultdict
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


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


_RECORD_ID_RE = re.compile(r"^(?P<prefix>.+?)_ep(?P<ep>\d+)$")


def parse_record_id(record_id: str) -> tuple[str, int | None]:
    """record_id "{prefix}_ep{NNN}" → (prefix, episode_num).

    prefix가 없거나 매칭 실패 시 (record_id, None).
    """
    m = _RECORD_ID_RE.match(record_id or "")
    if not m:
        return (record_id, None)
    return (m.group("prefix"), int(m.group("ep")))


def fit_class(label: str) -> str:
    return {
        "strong_fit": "fit-strong",
        "moderate_fit": "fit-moderate",
        "weak_fit": "fit-weak",
        "no_fit": "fit-no",
    }.get(label, "fit-unknown")


def group_by_title_genre(records: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """{(title_prefix, genre_id): [records sorted by episode]}"""
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        title_prefix, _ = parse_record_id(r.get("record_id", ""))
        groups[(title_prefix, r.get("genre_id", ""))].append(r)
    for key, recs in groups.items():
        recs.sort(key=lambda x: parse_record_id(x.get("record_id", ""))[1] or 0)
    return groups


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def render_markdown(intensity: dict, fixture_only: bool = False) -> str:
    lines: list[str] = []
    lines.append("# Phase 3.1 Episode Intensity — 회차 단위 장르 시그니처")
    lines.append("")
    if fixture_only:
        lines.append(
            "> **🧪 Fictional fixture-only demo** — 이 demo는 "
            "`tests/fixtures/annotation_public_safe/`의 *가공된 가상 인물* "
            "5 episode × 2 annotators 기반이며 실제 방송 회차 데이터가 아니다. "
            "Operating Guide §9 deploy 카테고리: `fixture-only`.",
        )
        lines.append("")
    lines.append(f"> **schema**: `{intensity['schema_version']}`  ")
    lines.append(f"> **n_records**: {intensity['n_records']} / **n_genres**: {intensity['n_genres']}  ")
    kept = intensity.get("kept_features_used", [])
    lines.append(f"> **kept_features_used** ({len(kept)}): {', '.join(kept)}")
    model = intensity.get("model", {})
    lines.append(
        f"> **model**: {model.get('type', '?')} "
        f"(trained={model.get('trained')}, data_source={model.get('data_source')})"
    )
    audit = intensity.get("audit", {})
    lines.append(
        f"> **audit**: raw_text_used={audit.get('raw_text_used')} / "
        f"evidence_preserved={audit.get('evidence_preserved')}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    groups = group_by_title_genre(intensity.get("intensity_records", []))
    if groups:
        lines.append("## Title × Genre 별 Episode Arc")
        lines.append("")
        for (title, genre), recs in sorted(groups.items()):
            lines.append(f"### `{title}` × `{genre}`")
            lines.append("")
            scores_str = " → ".join(
                f"{r['intensity_score']:.3f}" for r in recs
            )
            labels_str = " · ".join(r["fit_label"] for r in recs)
            lines.append(f"- arc: {scores_str}")
            lines.append(f"- fit: {labels_str}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 전체 Intensity Matrix")
    lines.append("")
    lines.append("| record | genre | intensity | fit | top contribution |")
    lines.append("|---|---|---|---|---|")
    for r in intensity.get("intensity_records", []):
        bd = r.get("feature_contributions", {}) or {}
        top = max(bd.items(), key=lambda x: x[1])[0] if bd else ""
        lines.append(
            f"| `{r['record_id']}` | `{r['genre_id']}` | "
            f"{r['intensity_score']:.3f} | {r['fit_label']} | {top} |"
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

def _bar_inline(score: float, max_width_px: int = 200) -> str:
    """0-1 score → inline svg-free div bar (CSS only)."""
    pct = max(0.0, min(1.0, score)) * 100
    return (
        f'<div class="bar-track"><div class="bar-fill" '
        f'style="width:{pct:.1f}%"></div></div>'
    )


def render_html(intensity: dict, fixture_only: bool = False) -> str:
    records = intensity.get("intensity_records", []) or []
    audit = intensity.get("audit", {})
    model = intensity.get("model", {})
    kept = intensity.get("kept_features_used", []) or []

    raw_safe_class = "audit-pass" if audit.get("raw_text_used") is False else "audit-fail"
    evidence_class = "audit-pass" if audit.get("evidence_preserved") is True else "audit-fail"

    # cycle 40 — fixture-only banner (Operating Guide §9 deploy category).
    # Takes precedence over data_source banner — public-safe fictional data must be
    # *prominently* labeled as such.
    fixture_banner = (
        '<div class="fixture-banner">'
        "<strong>🧪 Fictional fixture-only demo</strong> — "
        "이 demo는 <code>tests/fixtures/annotation_public_safe/</code>의 "
        "<em>가공된 가상 인물</em> 5 episode × 2 annotators 기반이며 "
        "실제 방송 회차 / 작가 인터뷰 / 시청자 reaction 데이터가 아니다. "
        "Operating Guide §9 deploy 카테고리: <code>fixture-only</code>."
        "</div>"
    ) if fixture_only else ""

    data_source = model.get("data_source", "")
    if data_source == "rulebook_only":
        data_source_banner = (
            '<div class="prep-banner">'
            "<strong>📐 Prep mode</strong> — Phase 3.0 reliability 통과 전 prep 데이터. "
            "Phase 3.0 pilot 후 phase3_pilot 데이터로 갱신됨."
            "</div>"
        )
    elif data_source == "phase3_pilot":
        data_source_banner = (
            '<div class="data-banner">'
            "<strong>📊 Phase 3.0 pilot 데이터 적용</strong> — KEEP feature 기반 weighted score."
            "</div>"
        )
    else:
        data_source_banner = ""

    # title × genre groups
    groups = group_by_title_genre(records)
    n_titles = len({k[0] for k in groups})

    arc_cards: list[str] = []
    for (title, genre), recs in sorted(groups.items()):
        bars: list[str] = []
        for r in recs:
            score = float(r["intensity_score"])
            bars.append(f"""
            <div class="arc-bar">
              <div class="arc-bar-label">ep{parse_record_id(r['record_id'])[1] or '?'}</div>
              <div class="arc-bar-track">
                <div class="arc-bar-fill {fit_class(r['fit_label'])}" style="height:{score*100:.1f}%"></div>
              </div>
              <div class="arc-bar-score">{score:.2f}</div>
            </div>""")
        arc_cards.append(f"""
        <article class="title-card">
          <header>
            <h3>{_esc(title)}</h3>
            <small class="muted">장르: <code>{_esc(genre)}</code> · {len(recs)} ep</small>
          </header>
          <div class="arc-chart">
            {''.join(bars)}
          </div>
        </article>""")

    # Full matrix rows with feature contribution mini-bars
    matrix_rows: list[str] = []
    for r in records:
        bd = r.get("feature_contributions", {}) or {}
        # Top contribution feature
        top_pair = max(bd.items(), key=lambda x: x[1]) if bd else ("", 0)
        contrib_bars = []
        for fname, val in sorted(bd.items(), key=lambda x: -x[1])[:4]:
            if val <= 0:
                continue
            # contribution can be 0-1, but typically much smaller; scale by max bd value
            max_val = max(bd.values()) if bd else 1.0
            pct = (val / max_val * 100) if max_val > 0 else 0
            contrib_bars.append(
                f'<div class="contrib-row">'
                f'<span class="contrib-name">{_esc(fname)}</span>'
                f'<div class="contrib-bar"><div class="contrib-fill" style="width:{pct:.1f}%"></div></div>'
                f'<span class="contrib-val">{val:.3f}</span>'
                f'</div>'
            )
        contribs_html = ''.join(contrib_bars) or '<span class="muted small">-</span>'

        matrix_rows.append(f"""
        <tr>
          <td><code class="rid">{_esc(r['record_id'])}</code></td>
          <td><code>{_esc(r['genre_id'])}</code></td>
          <td class="score-cell">{r['intensity_score']:.3f}</td>
          <td><span class="fit-tag {fit_class(r['fit_label'])}">{_esc(r['fit_label'])}</span></td>
          <td class="contribs">{contribs_html}</td>
        </tr>""")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>WITNESS · Phase 3.1 Episode Intensity — 회차 단위 장르 시그니처</title>
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

  .fixture-banner {{ padding: 0.9em 1.2em; border-radius: 7px;
              margin: 0.8em 0; font-size: 0.92em; line-height: 1.5;
              background: #fff8e6; border-left: 4px solid #d4942c;
              color: #4a3a18; }}
  .fixture-banner code {{ background: rgba(0,0,0,0.06); padding: 0.05em 0.4em;
              border-radius: 3px; font-size: 0.95em; }}
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

  .title-grid {{ display: grid;
                 grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                 gap: 1em; margin: 1em 0 2em; }}
  .title-card {{ background: #fff; padding: 1em 1.2em; border-radius: 8px;
                 box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
  .title-card h3 {{ margin: 0 0 0.2em; font-size: 1.15em; font-family: ui-monospace, monospace; }}
  .title-card header {{ border-bottom: 1px solid #eee; padding-bottom: 0.5em;
                        margin-bottom: 0.7em; }}

  .arc-chart {{ display: flex; align-items: flex-end; gap: 0.5em;
                height: 140px; padding: 0.5em 0; border-bottom: 1px solid #eee; }}
  .arc-bar {{ display: flex; flex-direction: column; align-items: center;
              flex: 1; min-width: 30px; }}
  .arc-bar-label {{ font-size: 0.78em; color: #888; margin-bottom: 4px; font-family: ui-monospace, monospace; }}
  .arc-bar-track {{ width: 100%; height: 90px; background: #f5f1e8;
                    border-radius: 3px; display: flex; align-items: flex-end;
                    overflow: hidden; }}
  .arc-bar-fill {{ width: 100%; transition: height 0.3s; }}
  .arc-bar-fill.fit-strong {{ background: #5a8d6c; }}
  .arc-bar-fill.fit-moderate {{ background: #b8954a; }}
  .arc-bar-fill.fit-weak {{ background: #c9a55a; }}
  .arc-bar-fill.fit-no {{ background: #aaa; }}
  .arc-bar-score {{ font-size: 0.78em; color: #555; margin-top: 4px;
                    font-family: ui-monospace, monospace; }}

  .fit-tag {{ display: inline-block; padding: 0.15em 0.55em; border-radius: 3px;
              font-size: 0.82em; font-weight: 600; }}
  .fit-strong {{ background: #e9f5ec; color: #2c6c3d; }}
  .fit-moderate {{ background: #f5f1e8; color: #846020; }}
  .fit-weak {{ background: #fdf3e3; color: #946a1f; }}
  .fit-no {{ background: #f3f3f3; color: #666; }}

  table {{ border-collapse: collapse; width: 100%; margin: 1em 0;
           background: #fff; border-radius: 6px; overflow: hidden;
           box-shadow: 0 1px 3px rgba(0,0,0,0.04); }}
  th, td {{ text-align: left; padding: 0.5em 0.7em; border-bottom: 1px solid #eee;
           vertical-align: middle; }}
  th {{ background: rgba(0,0,0,0.04); font-weight: 600; font-size: 0.92em; }}
  .score-cell {{ font-family: ui-monospace, monospace; font-weight: 600; }}
  .rid {{ font-size: 0.82em; }}

  .contrib-row {{ display: flex; align-items: center; gap: 0.4em;
                  font-size: 0.78em; margin: 0.1em 0; }}
  .contrib-name {{ flex: 0 0 130px; color: #555; font-family: ui-monospace, monospace; }}
  .contrib-bar {{ flex: 1; height: 8px; background: #f5f1e8;
                  border-radius: 2px; overflow: hidden; min-width: 60px; }}
  .contrib-fill {{ height: 100%; background: #7a8c5a; }}
  .contrib-val {{ flex: 0 0 50px; text-align: right; color: #666;
                  font-family: ui-monospace, monospace; }}

  details {{ margin: 0.6em 0; padding: 0.6em 0.8em; background: #faf8f3;
             border-radius: 5px; }}
  summary {{ cursor: pointer; font-weight: 600; font-size: 0.88em; }}
  details ul {{ margin: 0.4em 0 0; padding-left: 1.2em; font-size: 0.88em; }}

  footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #e0dcd0;
            color: #999; font-size: 0.85em; }}
</style>
</head>
<body>

<header class="page-head">
  <h1>WITNESS · Phase 3.1 Episode Intensity</h1>
  <p class="lead">각 *에피소드*가 장르 시그니처에 얼마나 부합하는지 *설명 가능한 weighted score*로 점수화한다.
    annotation feature × profile.feature_weights 선형 결합. ML / fine-tuning 0.</p>
</header>

{fixture_banner}
{data_source_banner}

<div class="audit-row">
  <span class="audit-tag {raw_safe_class}">raw_text_used: {str(audit.get('raw_text_used')).lower()}</span>
  <span class="audit-tag {evidence_class}">evidence_preserved: {str(audit.get('evidence_preserved')).lower()}</span>
  <span class="audit-tag {'audit-pass' if not model.get('trained') else 'audit-fail'}">model.trained: {str(model.get('trained')).lower()}</span>
  <span class="muted small">model.type: <code>{_esc(model.get('type', '?'))}</code></span>
  <span class="muted small">data_source: <code>{_esc(model.get('data_source', '?'))}</code></span>
  <span class="muted small">kept_features: <strong>{len(kept)}</strong></span>
</div>

<h2>Title × Genre 별 Episode Arc</h2>
<p class="muted small">{n_titles} title × {len({r.get('genre_id', '') for r in records})} genre = {len(groups)} arc.
   막대 높이 = intensity_score (0-1).</p>

<section class="title-grid">
  {''.join(arc_cards)}
</section>

<h2>전체 Intensity Matrix</h2>
<p class="muted small">{intensity['n_records']} records × {intensity['n_genres']} genres = {len(records)} 개 intensity 결과.</p>
<table>
  <thead>
    <tr><th>record</th><th>genre</th><th>intensity</th><th>fit</th><th>feature contributions (top 4)</th></tr>
  </thead>
  <tbody>
    {''.join(matrix_rows)}
  </tbody>
</table>

<details>
  <summary>Score 공식 (설명 가능)</summary>
  <ul style="margin-top:0.5em">
    <li>annotation feature 각 annotator 점수 평균 → 0-5 → 0.0-1.0 normalize</li>
    <li><strong>intensity_score</strong> = Σ (normalized × profile.feature_weights[f]) — KEEP feature만</li>
    <li>fit_label: ≥ 0.7 strong / ≥ 0.5 moderate / ≥ 0.25 weak / 그 외 no_fit</li>
    <li>profile.feature_weights는 Phase 3.0 reliability KEEP 통과 후 정규화 (sum=1)</li>
  </ul>
</details>

<details>
  <summary>Technical Appendix</summary>
  <ul style="margin-top:0.5em">
    <li>schema: <code>{_esc(intensity['schema_version'])}</code></li>
    <li>kept_features_used ({len(kept)}): <code>{_esc(', '.join(kept))}</code></li>
    <li>model: <code>{_esc(model.get('type', '?'))}</code> · trained={str(model.get('trained')).lower()}</li>
    <li>raw text 사용 0 / 학습 0 / fine-tuning 0 / 대사 생성 0</li>
    <li>flesh_baseline (seed × profile)와 *다른 layer*: episode × profile 답변</li>
  </ul>
</details>

<footer>
  <p>WITNESS Phase 3.1 prep · No-ML weighted rule score per episode.<br>
     CLI: <code>scripts/annotation/run_episode_intensity.py</code> + <code>build_episode_intensity_demo.py</code></p>
</footer>

</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--intensity", required=True, type=Path,
                     help="episode_intensity.json (run_episode_intensity.py 출력)")
    ap.add_argument("--output", required=True, type=Path,
                     help="output dir (e.g. docs/portfolio/demo_episode_intensity)")
    ap.add_argument("--fixture-only", action="store_true",
                     help="prominent 'Fictional fixture-only' banner 표시 "
                          "(Operating Guide §9 deploy 카테고리, cycle 40)")
    args = ap.parse_args(argv)

    if not args.intensity.exists():
        print(f"ERROR: intensity not found: {args.intensity}", file=sys.stderr)
        return 2

    intensity = json.loads(args.intensity.read_text(encoding="utf-8"))

    args.output.mkdir(parents=True, exist_ok=True)
    html_path = args.output / "index.html"
    md_path = args.output / "intensity.md"
    json_path = args.output / "episode_intensity.json"

    html_path.write_text(
        render_html(intensity, fixture_only=args.fixture_only),
        encoding="utf-8",
    )
    md_path.write_text(
        render_markdown(intensity, fixture_only=args.fixture_only),
        encoding="utf-8",
    )
    json_path.write_text(
        json.dumps(intensity, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    n = intensity.get("n_records", 0)
    print(f"OK: episode intensity demo → {args.output}")
    print(f"  html: {html_path.name}")
    print(f"  md:   {md_path.name}")
    print(f"  json: {json_path.name}")
    print(f"  records: {n} / genres: {intensity.get('n_genres', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
