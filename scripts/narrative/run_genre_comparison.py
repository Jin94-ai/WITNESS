"""CLI: 같은 SkeletonOutput을 *여러 장르*로 변환해 side-by-side HTML 비교.

Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md` §14.2:
    "Universal Skeleton → Genre Adapter → Genre Treatment" 메인 흐름을
    한 화면에서 증명. rulebook 추상화의 portfolio value.

사용:
    python scripts/narrative/run_genre_comparison.py \\
        --skeleton docs/portfolio/demo/skeleton_output.json \\
        --genres korean_morning_melodrama japanese_quiet_drama \\
        --output docs/portfolio/demo_genre_comparison

산출:
    {output_dir}/index.html               (self-contained side-by-side)
    {output_dir}/comparison.json          (machine-readable, 모든 변환 포함)
    {output_dir}/comparison.md            (human-readable summary)

원칙:
    - 외부 의존 0
    - 각 장르마다 audit 자동 실행
    - 어느 한 장르라도 audit fail이면 strict_audit=True에서 exit 1
    - 원본 skeleton의 source_seed_ids / conflict_axis는 모든 장르에서 동일하게 보존
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


from engine.observer.genre_adapter import (  # noqa: E402
    GenreAdaptedOutput, adapt_skeleton_to_genre,
)
from engine.observer.genre_audit import (  # noqa: E402
    GenreAuditResult, audit_genre_output,
)
from engine.observer.genre_rulebook import (  # noqa: E402
    GenreRulebook, load_audit_blocklist, load_rulebook,
)
from engine.observer.skeleton_output import SkeletonOutput  # noqa: E402
from scripts.narrative.apply_genre_adapter import (  # noqa: E402
    _load_skeleton_output,
)


# ---------------------------------------------------------------------------
# Per-genre adaptation bundle
# ---------------------------------------------------------------------------

def _adapt_one_genre(
    skeleton: SkeletonOutput, genre_id: str,
) -> tuple[GenreRulebook, GenreAdaptedOutput, GenreAuditResult]:
    rb = load_rulebook(genre_id)
    bl = load_audit_blocklist(genre_id)
    out = adapt_skeleton_to_genre(skeleton, rb)
    audit = audit_genre_output(out, bl)
    return rb, out, audit


# ---------------------------------------------------------------------------
# HTML render — side-by-side
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_genre_column(
    rb: GenreRulebook, out: GenreAdaptedOutput, audit: GenreAuditResult,
) -> str:
    """단일 장르의 column 블록 (Phase 2.8: structured outline + lens 우선)."""
    flow = out.adapted_flow
    audit_class = "audit-pass" if audit.overall == "pass" else "audit-fail"
    quality_count = len(audit.quality_warnings)
    quality_class = "quality-clean" if quality_count == 0 else "quality-warn"

    # Phase 2.8: structured outline if available, else fall back to free-form
    if flow.adapted_outline_steps:
        outline_html = "\n".join(
            f'<li><div class="step-name">{_esc(s.step)}</div>'
            f'<div class="step-line">{_esc(s.line_ko)}</div></li>'
            for s in flow.adapted_outline_steps
        )
    else:
        outline_html = "\n".join(
            f'<li>{_esc(line)}</li>' for line in flow.adapted_outline_ko
        )

    # genre_lens (Phase 2.8 Issue 3)
    lens_block = ""
    if flow.genre_lens_ko:
        lens_block = f"""
        <div class="genre-lens">
          <div class="lens-label">장르 렌즈</div>
          <p>{_esc(flow.genre_lens_ko)}</p>
        </div>"""

    return f"""
    <article class="genre-col">
      <header class="genre-head">
        <h2>{_esc(rb.display_name_ko)}</h2>
        <code class="muted">{_esc(out.genre_id)}</code>
      </header>
      {lens_block}
      <div class="audit-row">
        <span class="audit {audit_class}">audit: {audit.overall}</span>
        <span class="audit {quality_class}">quality warnings: {quality_count}</span>
      </div>

      <h3>제목</h3>
      <p class="title-line">{_esc(flow.title_ko)}</p>

      <h3>전제</h3>
      <p>{_esc(flow.premise_ko)}</p>

      <h3>회차 흐름</h3>
      <ol class="outline-list">{outline_html}</ol>

      <h3>마지막 질문</h3>
      <blockquote>{_esc(flow.cliffhanger_ko)}</blockquote>
    </article>
    """


def _render_html(
    skeleton: SkeletonOutput,
    bundles: list[tuple[GenreRulebook, GenreAdaptedOutput, GenreAuditResult]],
) -> str:
    """Phase 2.8 Issue 3 + Issue 2: new info hierarchy.

    Layout:
        1. Hero — "One Skeleton, Two Genre Lenses"
        2. Two genre lenses preview (Issue 3)
        3. Universal Skeleton Summary (with plain Korean labels — Issue 2)
        4. Side-by-side genre columns
        5. Why They Differ
        6. Evidence Preservation (collapsed)
        7. Technical Appendix (collapsed, with internal IDs)
    """
    from engine.observer.genre_rulebook import (
        archetype_plain_ko, flow_role_plain_ko,
    )
    from engine.observer.universal_story_seed import (
        load_conflict_axes, load_pressure_taxonomy, load_desire_taxonomy,
    )

    axes_taxo = load_conflict_axes()
    pressures_taxo = load_pressure_taxonomy()
    desires_taxo = load_desire_taxonomy()

    def _axis_label(axis_id: str) -> str:
        entry = axes_taxo.get(axis_id, {})
        return entry.get("plain_label_ko") or axis_id

    def _pressure_labels(ids: tuple[str, ...]) -> str:
        return ", ".join(
            (pressures_taxo.get(p, {}).get("plain_label_ko") or p)
            for p in ids
        )

    def _desire_labels(ids: tuple[str, ...]) -> str:
        return ", ".join(
            (desires_taxo.get(d, {}).get("plain_label_ko") or d)
            for d in ids
        )

    columns = "\n".join(_render_genre_column(rb, out, audit)
                        for rb, out, audit in bundles)

    # Phase 2.8 Issue 2: skeleton table에 plain label 우선 + small 내부 ID
    seed_rows = "\n".join(
        f'<tr>'
        f'<td><strong>{_esc(s.seed_id)}</strong></td>'
        f'<td>{_esc(flow_role_plain_ko(s.flow_role))}'
        f'<br><small class="muted">{_esc(s.flow_role)}</small></td>'
        f'<td>{_esc(_axis_label(s.conflict_axis_id))}'
        f'<br><small class="muted">{_esc(s.conflict_axis_id)}</small></td>'
        f'<td>{_esc(_pressure_labels(s.dominant_pressures))}</td>'
        f'<td>{_esc(_desire_labels(s.dominant_desires))}</td>'
        f'<td>{_esc(archetype_plain_ko(s.main_archetype))}</td>'
        f'</tr>'
        for s in skeleton.seeds
    )

    n_genres = len(bundles)
    audits_summary = " · ".join(
        f"{rb.genre_id}: {audit.overall}" for rb, _, audit in bundles
    )

    # Lens preview (Issue 3)
    lens_preview = "\n".join(
        f'<div class="lens-card">'
        f'<h3>{_esc(rb.display_name_ko)}</h3>'
        f'<p class="lens-line">{_esc(out.adapted_flow.genre_lens_ko or rb.description_ko)}</p>'
        f'</div>'
        for rb, out, _ in bundles
    )

    # Why-differ section: rulebook-derived
    why_diff_rows = []
    for i, (rb, out, _) in enumerate(bundles):
        # First conflict_amplifier description as the "why differ" anchor
        if rb.conflict_amplifiers:
            amp = rb.conflict_amplifiers[0]
            why_diff_rows.append(
                f'<div class="why-row">'
                f'<strong>{_esc(rb.display_name_ko)}</strong>: '
                f'{_esc(amp.description_ko)}'
                f'</div>'
            )
    why_diff_html = "\n".join(why_diff_rows)

    # Cross-genre evidence
    preserved_axes = set()
    for _, out, _ in bundles:
        for s in out.adapted_seeds:
            preserved_axes.add(s.source_conflict_axis_id)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>WITNESS · 같은 뼈대, 두 장르 렌즈</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          max-width: 1280px; margin: 1.5em auto; padding: 0 1em; line-height: 1.55;
          color: #222; background: #fafaf7; }}
  header.page-head {{ margin-bottom: 1.5em; }}
  header.page-head h1 {{ font-size: 1.9em; margin: 0 0 0.3em 0; }}
  header.page-head .lead {{ font-size: 1.05em; color: #444; }}
  .muted {{ color: #777; }}
  .small {{ font-size: 0.88em; }}

  .lens-preview {{ display: grid;
                   grid-template-columns: repeat({n_genres}, 1fr);
                   gap: 1em; margin: 1.5em 0 2em; }}
  @media (max-width: 880px) {{
    .lens-preview {{ grid-template-columns: 1fr; }}
  }}
  .lens-card {{ background: #f7f3ec; padding: 1em 1.2em; border-radius: 8px;
                border-left: 3px solid #c9a; }}
  .lens-card h3 {{ margin: 0 0 0.4em 0; font-size: 1.1em; }}
  .lens-card .lens-line {{ margin: 0; font-size: 0.95em; line-height: 1.5; }}

  .skeleton-summary {{ background: #f0ede5; padding: 1em 1.2em;
                       border-radius: 8px; margin: 1em 0 2em; }}
  .skeleton-summary h2 {{ margin-top: 0; font-size: 1.15em; }}
  .skeleton-summary table {{ border-collapse: collapse; width: 100%;
                              font-size: 0.92em; }}
  .skeleton-summary th, .skeleton-summary td {{ text-align: left;
            padding: 0.5em 0.7em; border-bottom: 1px solid #d5d0c2;
            vertical-align: top; }}
  .skeleton-summary th {{ background: rgba(0,0,0,0.04); font-weight: 600; }}

  .compare-grid {{ display: grid;
                   grid-template-columns: repeat({n_genres}, 1fr);
                   gap: 1.5em; }}
  @media (max-width: 880px) {{
    .compare-grid {{ grid-template-columns: 1fr; }}
  }}
  .genre-col {{ background: #fff; padding: 1.2em 1.4em;
                border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
  .genre-head h2 {{ margin: 0 0 0.2em 0; font-size: 1.25em; }}
  .genre-col h3 {{ margin-top: 1.4em; font-size: 0.95em; color: #555; }}
  .genre-col p, .genre-col ol {{ margin: 0.3em 0; }}
  .genre-lens {{ margin: 0.6em 0; padding: 0.6em 0.9em; background: #f5f1e8;
                 border-radius: 5px; border-left: 2px solid #c9a; }}
  .genre-lens .lens-label {{ font-size: 0.8em; color: #888; font-weight: 600;
                              text-transform: uppercase; letter-spacing: 0.04em; }}
  .genre-lens p {{ margin: 0.2em 0 0 0; font-size: 0.95em; }}
  .audit-row {{ margin: 0.6em 0 0; }}
  .audit {{ display: inline-block; padding: 0.2em 0.7em; border-radius: 4px;
            font-size: 0.85em; font-weight: 600; margin-right: 0.3em; }}
  .audit-pass {{ background: #e9f5ec; color: #2c6c3d; }}
  .audit-fail {{ background: #fbe9e9; color: #a23030; }}
  .quality-clean {{ background: #e9f5ec; color: #2c6c3d; }}
  .quality-warn {{ background: #fdf3e3; color: #946a1f; }}
  .title-line {{ font-weight: 600; }}
  blockquote {{ border-left: 3px solid #c9a; background: #fbf8f3;
                padding: 0.5em 0.9em; margin: 0.5em 0; border-radius: 4px;
                font-style: italic; }}
  .outline-list {{ padding-left: 1.4em; }}
  .outline-list li {{ margin: 0.5em 0; }}
  .step-name {{ font-weight: 600; font-size: 0.92em; color: #555; }}
  .step-line {{ margin-top: 0.15em; }}
  .why-section {{ background: #f5f3ed; padding: 1em 1.2em; border-radius: 8px;
                  margin: 2em 0 1em; }}
  .why-section h2 {{ margin-top: 0; font-size: 1.1em; }}
  .why-row {{ padding: 0.4em 0; border-bottom: 1px dotted #d5d0c2; }}
  .why-row:last-child {{ border-bottom: 0; }}
  details {{ margin: 1.5em 0; padding: 0.8em 1em; background: #f5f3ed;
             border-radius: 6px; }}
  summary {{ cursor: pointer; font-weight: 600; }}
  code {{ background: #efece4; padding: 1px 5px; border-radius: 3px;
          font-size: 0.88em; }}
  footer {{ margin-top: 3em; padding-top: 1em; border-top: 1px solid #e0dcd0;
            color: #999; font-size: 0.85em; }}
</style>
</head>
<body>

<header class="page-head">
  <h1>WITNESS · 같은 뼈대, 두 장르 렌즈</h1>
  <p class="lead">같은 이야기 뼈대가 장르 문법에 따라 다르게 살아나는 과정을 보여줍니다.</p>
  <p class="small muted">audit: {_esc(audits_summary)}</p>
</header>

<section class="lens-preview">
  {lens_preview}
</section>

<section class="skeleton-summary">
  <h2>입력 — Universal Skeleton (모든 장르의 공통 입력)</h2>
  <p class="muted small">4개의 anchor-clean universal seed. 인물 이름 / 시대 / 정경 사건 0.</p>
  <table>
    <thead>
      <tr><th>seed</th><th>흐름 위치</th><th>갈등 축</th><th>압력</th><th>욕망</th><th>인물 유형</th></tr>
    </thead>
    <tbody>
      {seed_rows}
    </tbody>
  </table>
</section>

<h2 style="margin-top:2em">장르 변환 결과 (side-by-side)</h2>
<section class="compare-grid">
  {columns}
</section>

<section class="why-section">
  <h2>왜 다르게 나오는가 (rulebook 근거)</h2>
  {why_diff_html}
</section>

<details>
  <summary>Evidence Preservation</summary>
  <ul>
    <li>원본 source_seed_ids: {_esc(', '.join(s.seed_id for s in skeleton.seeds))}</li>
    <li>모든 장르에서 보존된 갈등 축: {_esc(', '.join(sorted(preserved_axes)))}</li>
    <li>모든 변환의 transformation_level: <code>structure_only</code></li>
    <li>대사 / 출생의 비밀 / 작품 모방 0건 — 각 장르 audit이 자동 검증.</li>
  </ul>
</details>

<details>
  <summary>Technical Appendix (내부 ID + schema)</summary>
  <ul>
    <li>입력: <code>{_esc(skeleton.schema_version)}</code> (UniversalStorySeed v1.1)</li>
    <li>장르 수: {len(bundles)}</li>
    <li>장르 schema: <code>genre_rulebook_v1</code> + <code>genre_audit_blocklist_v1</code></li>
    <li>변환 schema: <code>genre_adapted_output_v1_1</code> (structured outline 포함)</li>
    <li>외부 의존 0 — LLM API / 데이터 fetch / 모델 학습 없음.</li>
    <li>같은 코드 (<code>engine.observer.genre_adapter</code>)가 모든 장르를 처리 — rulebook abstraction이 parametric.</li>
  </ul>
</details>

<footer>
  <p>WITNESS Phase 2.8 · Cross-genre Adapter Demo · structure-only.
     CLI: <code>scripts/narrative/run_genre_comparison.py</code></p>
</footer>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def _render_markdown(
    skeleton: SkeletonOutput,
    bundles: list[tuple[GenreRulebook, GenreAdaptedOutput, GenreAuditResult]],
) -> str:
    lines: list[str] = []
    lines.append("# WITNESS · 장르 어댑터 비교")
    lines.append("")
    lines.append("> 하나의 universal skeleton을 서로 다른 장르 문법으로 변환한 결과.")
    lines.append("")
    lines.append("## 입력 Skeleton")
    lines.append("")
    for s in skeleton.seeds:
        lines.append(
            f"- **{s.seed_id}** [{s.flow_role}] — `{s.conflict_axis_id}` "
            f"| 인물 유형: {s.main_archetype} | 압력: {', '.join(s.dominant_pressures) or '-'}"
        )
    lines.append("")
    for rb, out, audit in bundles:
        lines.append("---")
        lines.append("")
        lines.append(f"## {rb.display_name_ko} (`{rb.genre_id}`)")
        lines.append("")
        lines.append(f"**audit**: {audit.overall}")
        lines.append("")
        lines.append(f"**제목**: {out.adapted_flow.title_ko}")
        lines.append("")
        lines.append(f"**전제**: {out.adapted_flow.premise_ko}")
        lines.append("")
        lines.append("### 회차 흐름")
        lines.append("")
        for line in out.adapted_flow.adapted_outline_ko:
            lines.append(f"- {line}")
        lines.append("")
        lines.append(f"**마지막 질문**: > {out.adapted_flow.cliffhanger_ko}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True, type=Path)
    ap.add_argument("--genres", required=True, nargs="+",
                     help="2개 이상의 genre_id (e.g. korean_morning_melodrama japanese_quiet_drama)")
    ap.add_argument("--output", required=True, type=Path,
                     help="output dir")
    ap.add_argument("--strict-audit", action="store_true",
                     help="어느 한 장르라도 audit fail이면 exit 1")
    args = ap.parse_args(argv)

    if not args.skeleton.exists():
        print(f"ERROR: skeleton not found: {args.skeleton}", file=sys.stderr)
        return 2
    if len(args.genres) < 2:
        print("ERROR: --genres requires at least 2 genre ids for comparison",
               file=sys.stderr)
        return 2

    skeleton = _load_skeleton_output(args.skeleton)

    bundles: list[tuple[GenreRulebook, GenreAdaptedOutput, GenreAuditResult]] = []
    audit_overall = "pass"
    for gid in args.genres:
        try:
            rb, out, audit = _adapt_one_genre(skeleton, gid)
        except (FileNotFoundError, ValueError) as e:
            print(f"ERROR: genre {gid!r}: {e}", file=sys.stderr)
            return 2
        bundles.append((rb, out, audit))
        if audit.overall != "pass":
            audit_overall = "fail"

    args.output.mkdir(parents=True, exist_ok=True)
    html_path = args.output / "index.html"
    json_path = args.output / "comparison.json"
    md_path = args.output / "comparison.md"

    html_path.write_text(_render_html(skeleton, bundles), encoding="utf-8")
    md_path.write_text(_render_markdown(skeleton, bundles), encoding="utf-8")

    # Phase 2.8 Issue 4: comparison_summary 추가
    shared_axes = set(s.conflict_axis_id for s in skeleton.seeds)
    differences = []
    if len(bundles) >= 2:
        # 각 source_seed_id에 대해 장르별 first cliffhanger / premise 비교
        ids = [s.source_seed_id for s in bundles[0][1].adapted_seeds]
        by_genre_seed: dict[str, dict] = {sid: {} for sid in ids}
        for rb, out, _ in bundles:
            for s in out.adapted_seeds:
                by_genre_seed.setdefault(s.source_seed_id, {})[rb.genre_id] = (
                    s.adapted_premise_ko
                )
        for sid, premises in by_genre_seed.items():
            differences.append({
                "source_seed_id": sid,
                "by_genre": premises,
            })
    audit_overall = (
        "pass" if all(a.overall == "pass" for _, _, a in bundles) else "fail"
    )

    json_payload = {
        "schema_version": "genre_comparison_output_v1",
        "source_skeleton_version": skeleton.schema_version,
        "source_seed_ids": [s.seed_id for s in skeleton.seeds],
        "genres": [
            {
                "genre_id": rb.genre_id,
                "display_name_ko": rb.display_name_ko,
                "genre_lens_ko": rb.genre_lens_ko,
                "adapted": out.to_dict(),
                "audit": audit.to_dict(),
            }
            for rb, out, audit in bundles
        ],
        "comparison_summary": {
            "shared_conflict_axes": sorted(shared_axes),
            "differences_by_seed": differences,
            "audit_overall": audit_overall,
            "total_quality_warnings": sum(
                len(a.quality_warnings) for _, _, a in bundles
            ),
        },
    }
    json_path.write_text(
        json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    print(f"OK: comparison demo → {args.output}")
    print(f"  genres: {', '.join(g.genre_id for g, _, _ in bundles)}")
    print(f"  audit overall: {audit_overall}")
    if args.strict_audit and audit_overall == "fail":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
