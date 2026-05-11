"""Phase 3.1 §22.3 Target C — adaptation_recommendation.json → portfolio demo.

Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §22.3 + §28.

산출 (self-contained, 외부 CDN 0):
    {output_dir}/index.html
    {output_dir}/recommendations.md
    {output_dir}/adaptation_recommendation.json (machine-readable mirror)

목적:
    seed별 *top-K genre 추천*을 한 페이지로 시각화. ranked card view —
    Target A의 flat comparison table과 *다른 형태*. 리뷰어 진입 시
    "이 seed에는 어떤 장르가 어울리는가"가 한눈에 보임.

원칙 (Phase 3.05 정직성 4 layer):
    - JSON layer: source artifact의 schema_version + calibration_status mirror
    - Demo HTML layer: Non-Claims banner + rulebook-only mode 명시 + Rule #14
    - score_breakdown 노출 없음 (Target C는 ranked top-K view — score만 충분)
    - raw text 노출 0 (source artifact가 audit_raw_text_used=False)

사용:
    python scripts/narrative/build_adaptation_recommendation_demo.py \\
        --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \\
        --output docs/portfolio/demo_adaptation_recommendation
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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


def _fit_class(label: str) -> str:
    return {
        "strong_fit": "fit-strong",
        "moderate_fit": "fit-moderate",
        "weak_fit": "fit-weak",
        "no_fit": "fit-no",
    }.get(label, "fit-unknown")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def compute_top_genre_counts(payload: dict) -> list[tuple[str, int]]:
    """seed별 1순위 genre 빈도."""
    counter: Counter = Counter()
    for rec in payload.get("recommendations", []):
        modes = rec.get("recommended_modes", [])
        if modes:
            counter[modes[0]["genre_id"]] += 1
    return counter.most_common()


# ---------------------------------------------------------------------------
# Markdown render
# ---------------------------------------------------------------------------

def render_markdown(payload: dict) -> str:
    lines: list[str] = []
    is_rulebook_only = (
        payload.get("model", {}).get("data_source") == "rulebook_only"
    )

    lines.append("# Phase 3.1 §22.3 Target C — Adaptation Recommendation")
    lines.append("")

    lines.append("## Non-Claims (Phase 3.05 review §3)")
    lines.append("")
    lines.append("- 이 recommendation은 *truth claim*이 아닌 **adaptation candidate**다.")
    lines.append("- 학습 0 / 외부 fetch 0 / raw text 사용 0.")
    lines.append("- 모든 threshold는 `uncalibrated_phase3_placeholder` (Phase 5+ 실측 보정 전).")
    lines.append("- Rule #14 — rubric/recommendation은 학습 loss로 사용되지 않음.")
    lines.append("")

    if is_rulebook_only:
        lines.append(
            "> **📐 Prep mode (rulebook-only)** — 현재 score는 *실제 annotation 기반 추천이 아니라* "
            "rulebook compatibility (seed의 conflict_axis / dominant_pressures가 장르 rulebook과 호환되는 정도)다. "
            "Phase 3.0 pilot 데이터가 들어와야 annotation component가 추가되어 *data-backed* recommendation이 된다.",
        )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 메타")
    lines.append("")
    lines.append(f"- **schema**: `{payload['schema_version']}`")
    lines.append(f"- **source skeleton**: `{payload['source_skeleton_id']}` ({payload['source_skeleton_version']})")
    lines.append(f"- **profiles**: {', '.join(payload['genre_profiles_used'])}")
    lines.append(f"- **top_k**: {payload['top_k']}")
    model = payload.get("model", {})
    lines.append(
        f"- **model**: {model.get('type', '?')} "
        f"(trained={model.get('trained')}, data_source={model.get('data_source')})",
    )
    audit = payload.get("audit", {})
    lines.append(
        f"- **audit**: raw_text_used={audit.get('raw_text_used')} / "
        f"evidence_preserved={audit.get('evidence_preserved')}",
    )
    lines.append(f"- **calibration**: `{payload.get('calibration_status', '?')}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    label_suffix = " (rulebook-only)" if is_rulebook_only else ""

    # Top-genre distribution
    top_counts = compute_top_genre_counts(payload)
    if top_counts:
        lines.append("## 1순위 장르 분포 (seed별 top-1 빈도)")
        lines.append("")
        for genre, count in top_counts:
            lines.append(f"- `{genre}`: {count} seeds")
        lines.append("")

    lines.append("## Seed별 Ranked Recommendations")
    lines.append("")

    for rec in payload["recommendations"]:
        sid = rec["source_seed_id"]
        modes = rec.get("recommended_modes", [])
        if not modes:
            lines.append(f"### {sid}")
            lines.append("")
            lines.append("- (no modes above min_score)")
            lines.append("")
            continue
        top = modes[0]
        lines.append(f"### {sid}")
        lines.append("")
        lines.append(
            f"- **1순위**: `{top['genre_id']}` — "
            f"score {top['score']:.3f} ({top['fit_label']}{label_suffix})",
        )
        lines.append(f"- **이유**: {top['reason']}")
        lines.append(f"- **mode**: `{top.get('mode', 'rulebook_only')}`")
        if len(modes) > 1:
            lines.append("- **대안 후보**:")
            for alt in modes[1:]:
                lines.append(
                    f"  - `{alt['genre_id']}`: {alt['score']:.3f} "
                    f"({alt['fit_label']}{label_suffix}) — {alt['reason']}",
                )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 재현 명령")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/narrative/run_adaptation_recommendation.py \\")
    lines.append("    --skeleton docs/portfolio/demo/skeleton_output.json \\")
    lines.append("    --profiles data/narrative/phase3_1_demo/genre_profiles.json \\")
    lines.append("    --output data/narrative/phase3_1_demo/adaptation_recommendation.json \\")
    lines.append("    --top-k 3")
    lines.append("```")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/narrative/build_adaptation_recommendation_demo.py \\")
    lines.append("    --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \\")
    lines.append("    --output docs/portfolio/demo_adaptation_recommendation")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML render
# ---------------------------------------------------------------------------

_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       max-width: 960px; margin: 2em auto; padding: 0 1em; color: #222;
       line-height: 1.5; background: #fafafa; }
h1 { color: #1a1a1a; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
h2 { color: #2a2a2a; margin-top: 1.5em; }
h3 { color: #444; margin-top: 1.2em; }
.banner { background: #fff8e1; border-left: 4px solid #ffa000;
          padding: 0.7em 1em; margin: 1em 0; border-radius: 0 4px 4px 0; }
.banner.nc { background: #ffebee; border-left-color: #c62828; }
.banner.calibration { background: #e3f2fd; border-left-color: #1565c0; }
.meta { background: #f5f5f5; padding: 0.7em 1em; border-radius: 4px;
        font-size: 0.9em; color: #555; }
.meta code { background: #eee; padding: 0.1em 0.4em; border-radius: 3px; }
.seed-card { background: #fff; border: 1px solid #ddd; border-radius: 6px;
             padding: 1em 1.2em; margin: 0.8em 0;
             box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.seed-id { font-weight: bold; color: #2962ff; font-size: 1.1em; }
.top-rec { margin: 0.5em 0; font-size: 1em; }
.fit-strong { color: #1b5e20; font-weight: 600; }
.fit-moderate { color: #5d4037; }
.fit-weak { color: #757575; }
.fit-no { color: #b71c1c; }
.alt-list { font-size: 0.9em; color: #555; margin-top: 0.5em; }
.alt-list code { background: #f0f0f0; padding: 0.05em 0.3em; border-radius: 3px; }
.dist-bar { display: inline-block; height: 14px; background: #2962ff;
            vertical-align: middle; margin-right: 0.5em; border-radius: 2px; }
.dist-row { padding: 0.3em 0; }
.reason { color: #555; font-style: italic; font-size: 0.9em; }
footer { color: #888; font-size: 0.85em; margin-top: 2em; padding-top: 1em;
         border-top: 1px solid #ddd; }
""".strip()


def _render_seed_card(rec: dict, label_suffix: str) -> str:
    sid = _esc(rec["source_seed_id"])
    modes = rec.get("recommended_modes", [])
    if not modes:
        return (
            f'<div class="seed-card"><div class="seed-id">{sid}</div>'
            f'<div class="top-rec">(no modes above min_score)</div></div>'
        )
    top = modes[0]
    fit_cls = _fit_class(top["fit_label"])
    parts = [
        f'<div class="seed-card">',
        f'<div class="seed-id">{sid}</div>',
        f'<div class="top-rec">1순위: <code>{_esc(top["genre_id"])}</code> '
        f'— <span class="{fit_cls}">{top["score"]:.3f} '
        f'({_esc(top["fit_label"])}{_esc(label_suffix)})</span></div>',
        f'<div class="reason">이유: {_esc(top["reason"])}</div>',
        f'<div class="reason">mode: <code>{_esc(top.get("mode", "rulebook_only"))}</code></div>',
    ]
    if len(modes) > 1:
        alts: list[str] = []
        for alt in modes[1:]:
            alts.append(
                f'<code>{_esc(alt["genre_id"])}</code>: '
                f'<span class="{_fit_class(alt["fit_label"])}">'
                f'{alt["score"]:.3f} ({_esc(alt["fit_label"])}{_esc(label_suffix)})</span>',
            )
        parts.append(
            '<div class="alt-list">대안: ' + " · ".join(alts) + "</div>",
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_html(payload: dict) -> str:
    is_rulebook_only = (
        payload.get("model", {}).get("data_source") == "rulebook_only"
    )
    label_suffix = " (rulebook-only)" if is_rulebook_only else ""

    top_counts = compute_top_genre_counts(payload)
    max_count = max((c for _, c in top_counts), default=1)

    dist_rows: list[str] = []
    for genre, count in top_counts:
        bar_width = int(200 * count / max_count) if max_count > 0 else 0
        dist_rows.append(
            f'<div class="dist-row">'
            f'<span class="dist-bar" style="width: {bar_width}px"></span>'
            f'<code>{_esc(genre)}</code>: {count} seeds</div>',
        )

    seed_cards = "\n".join(
        _render_seed_card(rec, label_suffix)
        for rec in payload["recommendations"]
    )

    prep_banner = (
        '<div class="banner">📐 <b>Prep mode (rulebook-only)</b> — 현재 score는 '
        '<i>실제 annotation 기반 추천이 아니라</i> rulebook compatibility다. '
        'Phase 3.0 pilot 데이터가 들어와야 annotation component가 추가되어 '
        '<i>data-backed</i> recommendation이 된다.</div>'
        if is_rulebook_only else ""
    )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>Phase 3.1 Target C — Adaptation Recommendation</title>
<style>{_CSS}</style>
</head>
<body>
<h1>Phase 3.1 §22.3 Target C — Adaptation Recommendation</h1>

<div class="banner nc"><b>Non-Claims (Phase 3.05 review §3)</b> —
이 recommendation은 <i>truth claim</i>이 아닌 <b>adaptation candidate</b>다.
학습 0 / 외부 fetch 0 / raw text 사용 0.
Rule #14 — rubric/recommendation은 학습 loss로 사용되지 않음.</div>

<div class="banner calibration"><b>Calibration</b> — 모든 score / threshold는
<code>{_esc(payload.get('calibration_status', '?'))}</code>이며 Phase 5+ 실측 보정 전이다.</div>

{prep_banner}

<div class="meta">
<b>schema</b>: <code>{_esc(payload['schema_version'])}</code> ·
<b>source skeleton</b>: <code>{_esc(payload['source_skeleton_id'])}</code>
({_esc(payload['source_skeleton_version'])}) ·
<b>profiles</b>: {_esc(', '.join(payload['genre_profiles_used']))} ·
<b>top_k</b>: {payload['top_k']} ·
<b>model</b>: {_esc(payload.get('model', {}).get('type', '?'))}
(trained={payload.get('model', {}).get('trained')},
data_source={_esc(payload.get('model', {}).get('data_source', '?'))}) ·
<b>raw_text_used</b>: {payload.get('audit', {}).get('raw_text_used')}
</div>

<h2>1순위 장르 분포 (seed별 top-1 빈도)</h2>
{"".join(dist_rows) if dist_rows else "<p>(no recommendations)</p>"}

<h2>Seed별 Ranked Recommendations</h2>
{seed_cards}

<h2>재현 명령</h2>
<pre><code>python scripts/narrative/run_adaptation_recommendation.py \\
    --skeleton docs/portfolio/demo/skeleton_output.json \\
    --profiles data/narrative/phase3_1_demo/genre_profiles.json \\
    --output data/narrative/phase3_1_demo/adaptation_recommendation.json \\
    --top-k 3

python scripts/narrative/build_adaptation_recommendation_demo.py \\
    --recommendation data/narrative/phase3_1_demo/adaptation_recommendation.json \\
    --output docs/portfolio/demo_adaptation_recommendation</code></pre>

<footer>
Phase 3.1 §22.3 Target C · No-ML weighted score · Witness v3.0 ·
{_esc(payload.get('calibration_status', '?'))}
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--recommendation", required=True, type=Path,
                     help="adaptation_recommendation.json (run_adaptation_recommendation.py 출력)")
    ap.add_argument("--output", required=True, type=Path,
                     help="portfolio demo output directory")
    args = ap.parse_args(argv)

    if not args.recommendation.exists():
        print(f"ERROR: recommendation not found: {args.recommendation}",
              file=sys.stderr)
        return 2

    payload = json.loads(args.recommendation.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "adaptation_recommendation_v1":
        print(
            f"WARNING: schema_version mismatch: {payload.get('schema_version')} "
            f"!= adaptation_recommendation_v1",
            file=sys.stderr,
        )

    args.output.mkdir(parents=True, exist_ok=True)
    md_path = args.output / "recommendations.md"
    html_path = args.output / "index.html"
    json_mirror = args.output / "adaptation_recommendation.json"

    md_path.write_text(render_markdown(payload), encoding="utf-8")
    html_path.write_text(render_html(payload), encoding="utf-8")
    json_mirror.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK: portfolio demo → {args.output}")
    print(f"  HTML: {html_path}")
    print(f"  MD:   {md_path}")
    print(f"  JSON: {json_mirror}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
