"""Phase G Step G6 — Generate 9-trajectory sanity check summaries.

Lee examines these 9 trajectories only. Claude Code writes summaries.

Selected (per spec §6.2):
  canonical_like: can_03, can_08, can_12
  plausible_alternative: alt_02, alt_07, alt_13
  obvious_noise: noi_03 (L1), noi_08 (L2), noi_13 (L3)

Output:
  docs/person/V3_SANITY_CHECK_SUMMARIES.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.rubric.reference_loader import (  # noqa: E402
    ReferenceTrajectory,
    default_path,
    load_reference_set,
)

TARGET_IDS = [
    "can_03", "can_08", "can_12",
    "alt_02", "alt_07", "alt_13",
    "noi_03", "noi_08", "noi_13",
]

KEY_TICKS = [5, 7, 10, 12, 13, 17, 18, 19, 20, 21, 22, 28]


def load_eval(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_result(eval_payload: dict, traj_id: str) -> dict:
    for r in eval_payload["results"]:
        if r["trajectory_id"] == traj_id:
            return r
    raise KeyError(traj_id)


def summarize_actions(t: ReferenceTrajectory) -> str:
    """Action summary at key canonical tick points."""
    action_by_tick = {tr.tick: tr.action for tr in t.ticks}
    parts = []
    for tk in KEY_TICKS:
        if tk in action_by_tick:
            parts.append(f"T{tk:>2}: {action_by_tick[tk]}")
    return " | ".join(parts)


def state_trajectory_signal(t: ReferenceTrajectory) -> str:
    """Show the evolution of key state variables at canonical ticks."""
    s = {}
    for tr in t.ticks:
        if tr.tick in (17, 19, 20, 21, 28):
            s[tr.tick] = tr.state
    if not s:
        return "(no key-tick state snapshot)"
    lines = []
    for tk in sorted(s.keys()):
        st = s[tk]
        guilt_pf = st.get("guilt", {}).get("primary_figure", 0)
        loyalty_pf = st.get("loyalty", {}).get("primary_figure", 0)
        lines.append(
            f"    T{tk:>2}: fear={st['fear']:>4.1f}  grief={st['grief']:>4.1f}  "
            f"guilt={guilt_pf:>4.1f}  loyalty_pf={loyalty_pf:>4.1f}  "
            f"hope={st['hope']:>4.1f}"
        )
    return "\n".join(lines)


def trajectory_arc_reading(t: ReferenceTrajectory) -> str:
    """Claude's interpretation of the narrative arc."""
    # Extract action sequence at canonical denial+weep+confess ticks
    at = {tr.tick: tr.action for tr in t.ticks}
    d17 = at.get(17, "-")
    d18 = at.get(18, "-")
    d19 = at.get(19, "-")
    w20 = at.get(20, "-")
    w21 = at.get(21, "-")
    c28 = at.get(28, "-")

    denial_count = sum(1 for a in (d17, d18, d19) if a == "deny")
    wept = any(a == "weep" for a in (w20, w21))
    confessed = c28 == "confess"

    fragments = []

    # Denial analysis
    if denial_count == 3:
        fragments.append("tick 17/18/19 deny 3회 완벽 재현")
    elif denial_count == 2:
        fragments.append(f"deny 2회 (T17={d17}, T18={d18}, T19={d19})")
    elif denial_count == 1:
        fragments.append(f"deny 1회만 (T17={d17}, T18={d18}, T19={d19})")
    else:
        fragments.append(f"deny 없음 — 대체: T17={d17}, T18={d18}, T19={d19}")

    if wept:
        fragments.append(f"tick {20 if w20 == 'weep' else 21}에서 통곡 ✓")
    else:
        fragments.append(f"통곡 없음 (T20={w20}, T21={w21})")

    if confessed:
        fragments.append("tick 28 confess (복귀) ✓")
    else:
        fragments.append(f"T28 복귀 없음 (={c28})")

    return ". ".join(fragments) + "."


def make_summary(
    t: ReferenceTrajectory, eval_result: dict,
) -> str:
    scores = eval_result["scores"]
    cls = eval_result["discovery_class"]

    # Pretty-print score block
    score_lines = [
        f"  character_composite: {scores['character_composite']:.3f}",
        f"  canon_valid:         {scores['canon_valid']}",
        f"  canon_soft_drift:    {scores['canon_soft_drift']:.2f}",
        f"  causal_smoothness:   {scores['causal_smoothness']:.3f}",
        f"  novelty_band:        {scores['novelty_band']}",
        f"  novelty_drift:       {scores['novelty_drift']:.2f}",
        f"  discovery_class:     {cls}",
    ]

    noise_lv = t.noise_level
    noise_lv_str = f" (Level {noise_lv})" if noise_lv else ""

    lines = [
        f"### Trajectory: **{t.trajectory_id}**",
        f"",
        f"- **Category:** {t.category}{noise_lv_str}",
        f"- **Rubric scores:**",
        *score_lines,
        "",
        "- **Action summary at key ticks:**",
        "  ```",
        f"  {summarize_actions(t)}",
        "  ```",
        "",
        "- **State at canonical decision points:**",
        "  ```",
        f"{state_trajectory_signal(t)}",
        "  ```",
        "",
        f"- **Trajectory-level reading:**",
        f"  {trajectory_arc_reading(t)}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ref = load_reference_set(default_path())
    eval_path = ROOT / "data" / "reference" / "evaluation_results_calibrated.json"
    if not eval_path.exists():
        # Fall back to pre-calibration
        eval_path = ROOT / "data" / "reference" / "evaluation_results.json"
    eval_payload = load_eval(eval_path)

    # Build full report
    lines: list[str] = []
    lines.append("# V3 Phase G — Sanity Check Summaries (9 trajectories)\n")
    lines.append("**Generated:** 2026-04-23")
    lines.append(f"**Evaluator source:** `{eval_path.relative_to(ROOT)}`")
    thresholds = eval_payload["summary"]["evaluator_thresholds"]
    lines.append(f"**Thresholds:** rep={thresholds['reproduction_threshold']:.2f}, "
                 f"noise={thresholds['noise_threshold']:.2f}, "
                 f"copy={thresholds['copy_threshold']:.2f}, "
                 f"char_min={thresholds['character_min_composite']:.3f}")
    lines.append("")
    lines.append("Lee 검토 항목 (각 trajectory):")
    lines.append("- (a) 이건 정말 {category}처럼 보인다 → OK")
    lines.append("- (b) 어색하다 / 왜 이 category 인가 → Flag (GPT 품질 이슈)")
    lines.append("- (c) Rubric 판정이 이상하다 → Flag (rubric 이슈)")
    lines.append("")
    lines.append("---")

    for section_name, traj_ids in (
        ("## Section 1 — Canonical-like (3 samples)", TARGET_IDS[0:3]),
        ("## Section 2 — Plausible alternative (3 samples)", TARGET_IDS[3:6]),
        ("## Section 3 — Obvious noise (3 samples, one per level)", TARGET_IDS[6:9]),
    ):
        lines.append(f"\n{section_name}\n")
        for tid in traj_ids:
            try:
                t = ref.get(tid)
                er = find_result(eval_payload, tid)
            except KeyError:
                lines.append(f"### Trajectory: {tid} — NOT FOUND\n")
                continue
            lines.append(make_summary(t, er))
            lines.append("---\n")

    # Add a summary table at top-level
    lines.append("\n## Summary table\n")
    lines.append("| trajectory | category | drift | char | class |")
    lines.append("|---|---|---:|---:|---|")
    for tid in TARGET_IDS:
        try:
            er = find_result(eval_payload, tid)
        except KeyError:
            continue
        sc = er["scores"]
        lines.append(
            f"| {tid} | {er['category']}"
            f"{' L' + str(er['noise_level']) if er.get('noise_level') else ''}"
            f" | {sc['canon_soft_drift']:.1f}"
            f" | {sc['character_composite']:.2f}"
            f" | {er['discovery_class']} |"
        )

    # HARNESS H4 note
    lines.append("\n## Phase G 상태 (for Lee 판단)\n")
    lines.append("- **Step G1:** Reference loader + schema 검증 완료 (14 tests green).")
    lines.append("- **Step G2:** 45 trajectories rubric 평가. Default threshold로 **45/45 NOT_DISCOVERY_NOISE**.")
    lines.append("- **Step G3:** 분포 리포트 작성 (`V3_REFERENCE_DISTRIBUTION_REPORT.md`).")
    lines.append("")
    lines.append("  - **Canonical drift median: 25.00** (range 22.5-28.5)")
    lines.append("  - **Alternative drift median: 29.50** (range 27-35.5)")
    lines.append("  - **Noise drift median: 29.00** (range 29-30)")
    lines.append("  - canonical vs noise: **NO OVERLAP** (분리 가능)")
    lines.append("  - **Character composite가 backwards**: canonical=0.67 (최저), alt=0.88, noise=0.81")
    lines.append("")
    lines.append("- **Step G4:** Percentile-based calibration:")
    lines.append(f"  - reproduction_threshold = canonical.drift P90 = **28.30**")
    lines.append(f"  - noise_threshold = noise.drift P10 = **29.00**")
    lines.append(f"  - character_min = alt.character P25 = **0.843**")
    lines.append(f"  - copy_threshold = canonical.novelty_drift P10 = **23.50**")
    lines.append("")
    lines.append("  Confusion matrix (target in parens):")
    lines.append("  | actual | canonical% | alternative% | noise% |")
    lines.append("  |---|---:|---:|---:|")
    lines.append("  | canonical | **87%** (>80 ✓) | 13% (<15 ✓) | 0% (<5 ✓) |")
    lines.append("  | alternative | 13% (<10 ✗) | **33%** (>70 ✗) | 53% (<20 ✗) |")
    lines.append("  | noise | 0% (<5 ✓) | 67% (<10 ✗) | **33%** (>85 ✗) |")
    lines.append("")
    lines.append("  **Target partially met (canonical only).** Alternative/noise classification failed.")
    lines.append("")
    lines.append("- **Step G5:** Variable-specific recovery profile.")
    lines.append("  - fear: HL=4.5, floor=0.0 (fast decay)")
    lines.append("  - confusion: HL=7.0, floor=0.0")
    lines.append("  - grief: HL=13.0, floor=0.15 (long tail)")
    lines.append("  - guilt: HL=11.0, floor=0.10 (long tail)")
    lines.append("  - shame: HL=6.0, floor=0.05")
    lines.append("  - anger: HL=6.0, floor=0.0")
    lines.append("  - awe: HL=10.0, floor=0.0")
    lines.append("")
    lines.append("  Peter 100-tick: guilt 0.11 (floor), shame 0.05 (floor), others → 0 ✓")
    lines.append("")
    lines.append("- **Tests:** 348 v3-local green (+ 14 reference + 8 calibration).")
    lines.append("")
    lines.append("## Case 판정 (spec §7.1)\n")
    lines.append("**Case β (Rubric 재설계 필요) 신호 뚜렷:**")
    lines.append("1. Alternative/noise 분포 중첩 심함 (P10 vs P90 gap = 29.0 - 28.3 = 0.7)")
    lines.append("2. Character composite가 canonical에서 최저 — rubric 작동 방향 반대")
    lines.append("3. Causal smoothness 세 category 모두 0.85-0.88 — 구분력 없음")
    lines.append("4. Confusion matrix 3 행 중 1 행만 target 달성")
    lines.append("")
    lines.append("Phase H (rubric 재설계) 후보:")
    lines.append("- 축 재정의 (character critic 로직 점검)")
    lines.append("- Canon soft_drift 계산법 재검토 (현재 edit distance가 너무 블런트)")
    lines.append("- Novelty critic를 canon에서 독립 (현재 novelty_drift == canon_soft_drift)")

    out_path = ROOT / "docs" / "person" / "V3_SANITY_CHECK_SUMMARIES.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[G6] Saved sanity-check summaries: {out_path}")
    print(f"     9 trajectories: {TARGET_IDS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
