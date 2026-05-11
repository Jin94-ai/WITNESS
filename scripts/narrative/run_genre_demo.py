"""CLI: SkeletonOutput + GenreRulebook → portfolio demo (self-contained HTML).

Per `docs/WITNESS_PHASE_2_75_GENRE_ADAPTER_MVP_PLAN.md` §9.2 + §10.

산출:
    {output_dir}/genre_adapted_output.json   (machine-readable)
    {output_dir}/genre_adapted_output.md     (human-readable)
    {output_dir}/evidence_audit.md           (audit detail)
    {output_dir}/index.html                  (self-contained — Hero / Original /
                                              Adapted / Episode Flow / Evidence)

사용:
    python scripts/narrative/run_genre_demo.py \\
        --skeleton docs/portfolio/demo/skeleton_output.json \\
        --genre korean_morning_melodrama \\
        --output docs/portfolio/demo_genre
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
from engine.observer.genre_audit import GenreAuditResult, audit_genre_output  # noqa: E402
from engine.observer.genre_rulebook import (  # noqa: E402
    load_audit_blocklist, load_rulebook,
)
from engine.observer.skeleton_output import SkeletonOutput  # noqa: E402
from scripts.narrative.apply_genre_adapter import _load_skeleton_output  # noqa: E402


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def _render_markdown(
    skeleton: SkeletonOutput,
    adapted: GenreAdaptedOutput,
    audit: GenreAuditResult,
) -> str:
    """Phase 2.8: structured outline + lens + quality_warnings 반영."""
    from engine.observer.genre_rulebook import (
        archetype_plain_ko, flow_role_plain_ko,
    )
    from engine.observer.universal_story_seed import (
        load_conflict_axes, load_pressure_taxonomy, load_desire_taxonomy,
    )
    axes_taxo = load_conflict_axes()
    pressures_taxo = load_pressure_taxonomy()
    desires_taxo = load_desire_taxonomy()

    def _axis_label(aid: str) -> str:
        return (axes_taxo.get(aid, {}).get("plain_label_ko") or aid)

    def _press_labels(ids: tuple[str, ...]) -> str:
        return ", ".join(
            (pressures_taxo.get(p, {}).get("plain_label_ko") or p) for p in ids
        )

    def _desire_labels(ids: tuple[str, ...]) -> str:
        return ", ".join(
            (desires_taxo.get(d, {}).get("plain_label_ko") or d) for d in ids
        )

    flow = adapted.adapted_flow
    lines: list[str] = []
    lines.append(f"# {flow.title_ko}")
    lines.append("")
    lines.append(f"> **장르**: {adapted.genre_id}  ")
    lines.append(f"> **원본 skeleton**: {adapted.source_skeleton_version}  ")
    lines.append(f"> **변환 단계**: structure_only  ")
    lines.append(f"> **audit**: {audit.overall} (quality warnings: {len(audit.quality_warnings)})")
    lines.append("")
    if flow.genre_lens_ko:
        lines.append(f"> **장르 렌즈**: {flow.genre_lens_ko}")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 원본 뼈대")
    lines.append("")
    for seed in skeleton.seeds:
        lines.append(
            f"- **{seed.seed_id}** [{flow_role_plain_ko(seed.flow_role)}]"
        )
        lines.append(f"  - 갈등 축: {_axis_label(seed.conflict_axis_id)} (`{seed.conflict_axis_id}`)")
        lines.append(f"  - 인물 유형: {archetype_plain_ko(seed.main_archetype)} (`{seed.main_archetype}`)")
        if seed.dominant_pressures:
            lines.append(f"  - 압력: {_press_labels(seed.dominant_pressures)}")
        if seed.dominant_desires:
            lines.append(f"  - 욕망: {_desire_labels(seed.dominant_desires)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 장르 변환 결과")
    lines.append("")
    lines.append(f"### {flow.title_ko}")
    lines.append("")
    lines.append(flow.premise_ko or "(전제 없음)")
    lines.append("")
    lines.append("### 인물 배치")
    lines.append("")
    for sid, role in flow.role_map.items():
        lines.append(f"- {sid} → {role}")
    lines.append("")
    lines.append("### 회차 흐름")
    lines.append("")
    if flow.adapted_outline_steps:
        for step in flow.adapted_outline_steps:
            lines.append(f"- **{step.step}**")
            lines.append(f"  - {step.line_ko}")
            lines.append(f"  - <small>seed: {step.source_seed_id} ({step.source_flow_role})</small>")
    else:
        for line in flow.adapted_outline_ko:
            lines.append(f"- {line}")
    lines.append("")
    lines.append("### 마지막 질문 (cliffhanger)")
    lines.append("")
    lines.append(f"> {flow.cliffhanger_ko}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 변환 seed 상세")
    lines.append("")
    for s in adapted.adapted_seeds:
        lines.append(f"### {s.source_seed_id} → {s.genre_role}")
        lines.append("")
        lines.append(f"- 원본 갈등: {_axis_label(s.source_conflict_axis_id)} (`{s.source_conflict_axis_id}`)")
        lines.append(f"- 원본 압력: {_press_labels(s.source_pressures) or '(없음)'}")
        lines.append(f"- 원본 욕망: {_desire_labels(s.source_desires) or '(없음)'}")
        lines.append(f"- 장르 압력: {', '.join(s.genre_pressure) or '(없음)'}")
        lines.append(f"- 장르 증폭기: `{s.genre_conflict_amplifier}`")
        lines.append(f"- 변환 전제: {s.adapted_premise_ko}")
        lines.append(f"- 기능: {s.adapted_function_ko}")
        lines.append(f"- 개별 클리프행어: {s.cliffhanger_ko}")
        lines.append("")
    return "\n".join(lines)


def _render_audit_markdown(
    adapted: GenreAdaptedOutput, audit: GenreAuditResult,
) -> str:
    lines: list[str] = []
    lines.append("# Genre Adapter Evidence / Audit")
    lines.append("")
    lines.append(f"> **장르**: {adapted.genre_id}  ")
    lines.append(f"> **원본 seed ids**: {', '.join(adapted.source_seed_ids)}  ")
    lines.append(f"> **변환 단계**: structure_only  ")
    lines.append(f"> **audit overall**: **{audit.overall}**")
    lines.append("")
    lines.append("## 보존 검증")
    lines.append("")
    summary = adapted.adapted_flow.evidence_summary
    lines.append(f"- 원본 seed 수: {summary.get('source_seed_count')}")
    lines.append(f"- 보존된 갈등 축: {', '.join(summary.get('preserved_conflict_axes', []))}")
    lines.append(f"- 보존된 압력: {', '.join(summary.get('preserved_pressures', []))}")
    lines.append(f"- 보존된 욕망: {', '.join(summary.get('preserved_desires', []))}")
    lines.append("")
    lines.append("## audit 결과")
    lines.append("")
    for label, items in (
        ("Forbidden event", audit.forbidden_event_violations),
        ("Dialogue", audit.dialogue_violations),
        ("Source imitation", audit.source_imitation_violations),
        ("Evidence preservation", audit.evidence_violations),
    ):
        lines.append(f"### {label}")
        lines.append("")
        if items:
            for v in items:
                lines.append(f"- ⚠ {v}")
        else:
            lines.append("- 위반 0건.")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML render (self-contained, Plan §10)
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _render_html(
    skeleton: SkeletonOutput,
    adapted: GenreAdaptedOutput,
    audit: GenreAuditResult,
) -> str:
    """Phase 2.8: structured outline + lens + plain Korean labels + quality_warnings."""
    from engine.observer.genre_rulebook import (
        archetype_plain_ko, flow_role_plain_ko,
    )
    from engine.observer.universal_story_seed import (
        load_conflict_axes, load_pressure_taxonomy, load_desire_taxonomy,
    )
    axes_taxo = load_conflict_axes()
    pressures_taxo = load_pressure_taxonomy()
    desires_taxo = load_desire_taxonomy()

    def _axis_label(aid: str) -> str:
        return (axes_taxo.get(aid, {}).get("plain_label_ko") or aid)

    def _press_labels(ids: tuple[str, ...]) -> str:
        return ", ".join(
            (pressures_taxo.get(p, {}).get("plain_label_ko") or p) for p in ids
        )

    def _desire_labels(ids: tuple[str, ...]) -> str:
        return ", ".join(
            (desires_taxo.get(d, {}).get("plain_label_ko") or d) for d in ids
        )

    flow = adapted.adapted_flow
    audit_class = "audit-pass" if audit.overall == "pass" else "audit-fail"
    quality_count = len(audit.quality_warnings)
    quality_class = "quality-clean" if quality_count == 0 else "quality-warn"

    seed_rows = []
    by_id = {s.source_seed_id: s for s in adapted.adapted_seeds}
    for orig in skeleton.seeds:
        adp = by_id.get(orig.seed_id)
        if adp is None:
            continue
        seed_rows.append(f"""
        <tr>
          <td>
            <strong>{_esc(orig.seed_id)}</strong>
            <br><small class="muted">{_esc(flow_role_plain_ko(orig.flow_role))}</small>
            <br><small class="muted" style="opacity:0.6">{_esc(orig.flow_role)}</small>
          </td>
          <td>
            <div>{_esc(_axis_label(orig.conflict_axis_id))}</div>
            <small class="muted">{_esc(orig.conflict_axis_id)}</small>
            <div>{_esc(archetype_plain_ko(orig.main_archetype))}</div>
            <small class="muted">압력: {_esc(_press_labels(orig.dominant_pressures))}</small><br>
            <small class="muted">욕망: {_esc(_desire_labels(orig.dominant_desires))}</small>
          </td>
          <td>
            <div><strong>{_esc(adp.genre_role)}</strong></div>
            <div class="muted small">압력: {_esc(', '.join(adp.genre_pressure))}</div>
            <div>{_esc(adp.adapted_premise_ko)}</div>
            <div class="muted small">기능: {_esc(adp.adapted_function_ko)}</div>
          </td>
        </tr>""")

    # Phase 2.8: structured outline if available
    if flow.adapted_outline_steps:
        outline_lines = "\n".join(
            f'<li><div class="step-name">{_esc(s.step)}</div>'
            f'<div class="step-line">{_esc(s.line_ko)}</div>'
            f'<small class="muted">seed: {_esc(s.source_seed_id)} · '
            f'{_esc(flow_role_plain_ko(s.source_flow_role))}</small></li>'
            for s in flow.adapted_outline_steps
        )
    else:
        outline_lines = "\n".join(
            f'<li>{_esc(line)}</li>' for line in flow.adapted_outline_ko
        )

    role_map_rows = "\n".join(
        f'<tr><td>{_esc(sid)}</td><td>{_esc(role)}</td></tr>'
        for sid, role in flow.role_map.items()
    )

    lens_block = ""
    if flow.genre_lens_ko:
        lens_block = f"""
    <section class="genre-lens">
      <div class="lens-label">장르 렌즈</div>
      <p>{_esc(flow.genre_lens_ko)}</p>
    </section>"""

    quality_html = ""
    if audit.quality_warnings:
        quality_html = "<ul>" + "".join(
            f'<li class="muted small">⚠ {_esc(w)}</li>' for w in audit.quality_warnings
        ) + "</ul>"

    audit_summary = f"""
    <div class="audit-row">
      <span class="audit {audit_class}">audit: {audit.overall}</span>
      <span class="audit {quality_class}">quality warnings: {quality_count}</span>
    </div>
    <ul class="muted small">
      <li>forbidden event 위반: {len(audit.forbidden_event_violations)}건</li>
      <li>dialogue 위반: {len(audit.dialogue_violations)}건</li>
      <li>source imitation 위반: {len(audit.source_imitation_violations)}건</li>
      <li>evidence preservation 위반: {len(audit.evidence_violations)}건</li>
    </ul>
    {quality_html}"""

    summary = flow.evidence_summary
    evidence_block = f"""
    <details>
      <summary>Evidence / Audit (펼쳐서 보기)</summary>
      <ul>
        <li>source seed ids: {_esc(', '.join(adapted.source_seed_ids))}</li>
        <li>변환 단계: <code>structure_only</code></li>
        <li>보존된 갈등 축: {_esc(', '.join(summary.get('preserved_conflict_axes', [])))}</li>
        <li>보존된 압력: {_esc(', '.join(summary.get('preserved_pressures', [])))}</li>
        <li>보존된 욕망: {_esc(', '.join(summary.get('preserved_desires', [])))}</li>
        <li>대사 생성 0건 / 출생의 비밀 같은 막장 사건 추가 0건 — audit 자동 검증.</li>
      </ul>
      {audit_summary}
    </details>"""

    appendix = f"""
    <details>
      <summary>Technical Appendix</summary>
      <ul>
        <li>schema: <code>{_esc(adapted.schema_version)}</code></li>
        <li>source skeleton: <code>{_esc(adapted.source_skeleton_version)}</code></li>
        <li>genre rulebook: <code>{_esc(adapted.genre_id)}</code> (genre_rulebook_v1)</li>
        <li>변환 입력 게이트: flow != null / unknown_axis_count == 0 /
            forbidden_event_additions == 0 / forbidden_dialogue_generation == 0</li>
        <li>이 데모는 <strong>외부 의존 0</strong>: LLM API / 실제 줄거리 fetch / 학습 모델 없음.</li>
      </ul>
    </details>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>WITNESS · 장르 어댑터 데모 — {_esc(flow.title_ko)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          max-width: 880px; margin: 2em auto; padding: 0 1em; line-height: 1.55;
          color: #222; }}
  h1 {{ font-size: 1.7em; margin-bottom: 0.2em; }}
  h2 {{ margin-top: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #eee; }}
  h3 {{ margin-top: 1.5em; }}
  .hero {{ background: #f7f5f0; padding: 1.5em; border-radius: 8px; margin: 1.5em 0; }}
  .hero p {{ margin: 0.4em 0; }}
  .muted {{ color: #777; font-size: 0.9em; }}
  .small {{ font-size: 0.88em; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ text-align: left; padding: 0.6em; border-bottom: 1px solid #eee;
           vertical-align: top; }}
  th {{ background: #fafafa; font-weight: 600; }}
  ol {{ padding-left: 1.4em; }}
  ol li {{ margin: 0.6em 0; }}
  .step-name {{ font-weight: 600; color: #555; font-size: 0.92em; }}
  .step-line {{ margin-top: 0.15em; }}
  blockquote {{ border-left: 3px solid #c9a; background: #fbf8f3; padding: 0.6em 1em;
                margin: 1em 0; border-radius: 4px; }}
  details {{ margin: 1em 0; padding: 0.8em 1em; background: #fafafa;
             border-radius: 6px; }}
  summary {{ cursor: pointer; font-weight: 600; }}
  .genre-lens {{ margin: 1em 0 1.5em; padding: 0.9em 1.1em; background: #f5f1e8;
                  border-left: 3px solid #c9a; border-radius: 5px; }}
  .genre-lens .lens-label {{ font-size: 0.78em; color: #888; font-weight: 600;
                              text-transform: uppercase; letter-spacing: 0.06em; }}
  .genre-lens p {{ margin: 0.2em 0 0 0; font-size: 0.98em; line-height: 1.5; }}
  .audit-row {{ margin: 0.6em 0; }}
  .audit {{ display: inline-block; padding: 0.2em 0.7em; border-radius: 4px;
            font-size: 0.88em; font-weight: 600; margin-right: 0.4em; }}
  .audit-pass {{ background: #e9f5ec; color: #2c6c3d; }}
  .audit-fail {{ background: #fbe9e9; color: #a23030; }}
  .quality-clean {{ background: #e9f5ec; color: #2c6c3d; }}
  .quality-warn {{ background: #fdf3e3; color: #946a1f; }}
  code {{ background: #f0f0f0; padding: 1px 5px; border-radius: 3px;
          font-size: 0.9em; }}
</style>
</head>
<body>

<header>
  <h1>WITNESS · 장르 어댑터 데모</h1>
  <p class="muted">세계 시뮬레이션에서 나온 보편 이야기 뼈대를
    {_esc(adapted.genre_id)}의 <em>구조 문법</em>으로 변환합니다.</p>
</header>
{lens_block}

<section class="hero">
  <h2 style="margin-top:0;border:none">{_esc(flow.title_ko)}</h2>
  <p>{_esc(flow.premise_ko)}</p>
  <p class="muted"><strong>마지막 질문:</strong> {_esc(flow.cliffhanger_ko)}</p>
</section>

<h2>원본 Skeleton vs 장르 변환</h2>
<table>
  <thead>
    <tr><th>seed</th><th>원본 (universal)</th><th>장르 변환 결과</th></tr>
  </thead>
  <tbody>
    {''.join(seed_rows)}
  </tbody>
</table>

<h2>회차 흐름</h2>
<ol>
  {outline_lines}
</ol>

<h2>인물 배치</h2>
<table>
  <thead>
    <tr><th>seed_id</th><th>장르 역할</th></tr>
  </thead>
  <tbody>
    {role_map_rows}
  </tbody>
</table>

<h2>Evidence / Audit</h2>
{evidence_block}

<h2>Technical Appendix</h2>
{appendix}

<footer style="margin-top:3em; padding-top:1em; border-top:1px solid #eee;
              color:#999; font-size:0.85em;">
  <p>WITNESS Phase 2.75 · Rule-based Genre Adapter MVP · structure-only.
     본 데모는 외부 LLM / 데이터 fetch 없이 SkeletonOutput v1.1 + rulebook으로 생성.</p>
</footer>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skeleton", required=True, type=Path)
    ap.add_argument("--genre", required=True)
    ap.add_argument("--output", required=True, type=Path,
                     help="output dir (e.g. docs/portfolio/demo_genre)")
    ap.add_argument("--strict-audit", action="store_true",
                     help="audit fail 시 exit 1")
    args = ap.parse_args(argv)

    if not args.skeleton.exists():
        print(f"ERROR: skeleton not found: {args.skeleton}", file=sys.stderr)
        return 2

    skeleton = _load_skeleton_output(args.skeleton)
    rulebook = load_rulebook(args.genre)
    blocklist = load_audit_blocklist(args.genre)

    try:
        adapted = adapt_skeleton_to_genre(skeleton, rulebook)
    except ValueError as e:
        print(f"ERROR: skeleton fails input gate: {e}", file=sys.stderr)
        return 1
    audit = audit_genre_output(adapted, blocklist)

    args.output.mkdir(parents=True, exist_ok=True)
    json_path = args.output / "genre_adapted_output.json"
    md_path = args.output / "genre_adapted_output.md"
    audit_path = args.output / "evidence_audit.md"
    html_path = args.output / "index.html"

    out_dict = adapted.to_dict()
    out_dict["audit"] = audit.to_dict()
    json_path.write_text(
        json.dumps(out_dict, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    md_path.write_text(_render_markdown(skeleton, adapted, audit), encoding="utf-8")
    audit_path.write_text(_render_audit_markdown(adapted, audit), encoding="utf-8")
    html_path.write_text(_render_html(skeleton, adapted, audit), encoding="utf-8")

    print(f"OK: demo generated → {args.output}")
    print(f"  json:  {json_path.name}")
    print(f"  md:    {md_path.name}")
    print(f"  audit: {audit_path.name}")
    print(f"  html:  {html_path.name}")
    print(f"  audit overall: {audit.overall}")

    if args.strict_audit and audit.overall == "fail":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
