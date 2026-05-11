"""Demo Seed Diversity — show that data-driven body text varies by seed.

Per `WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN.md` 후속 directive (data-driven
synthesizer). Runs N seeds through engine + NarrativeEvidence + body
synthesizer and prints a side-by-side comparison table — both stdout
(human readable) and a markdown file at
`docs/portfolio/demo/seed_diversity_demo.md` (portfolio asset).

This is *not* a test — it's a portfolio asset showing reviewers that the
body text genuinely differs across simulation outputs.

Usage:
    python scripts/narrative/demo_seed_diversity.py
    python scripts/narrative/demo_seed_diversity.py --seeds 0,3,7,11
    python scripts/narrative/demo_seed_diversity.py --anchor peter_scarcity_baseline
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "visual"))

from engine.observer.data_narrative import (  # noqa: E402
    evidence_to_act_summary,
    evidence_to_logline,
    extract_narrative_evidence,
)
from engine.observer.episode_outline import resolve_korean_josa  # noqa: E402

# Display-name overrides for general-audience surface (per directive 2026-05-08).
# evidence-driven text는 raw English name을 박아 넣으므로 사용자가 보는
# markdown surface 출력 시점에 한국어로 매핑한다. data layer (raw evidence
# 자체)는 영어 이름 유지.
_NAME_OVERRIDES_KO: dict[str, str] = {
    "Peter":    "베드로",
    "Andrew":   "안드레",
    "James":    "야고보",
    "John":     "요한",
    "Judas":    "유다",
    "Caiaphas": "가야바",
}


def _ko_names(text: str) -> str:
    for raw, ko in _NAME_OVERRIDES_KO.items():
        text = text.replace(raw, ko)
    return text
from engine.observer.identity_resolver import IdentityResolver  # noqa: E402
from engine.observer.moment_extractor import extract_moments  # noqa: E402
from engine.observer.story_candidate_builder import (  # noqa: E402
    build_story_candidates,
)
from engine.observer.thread_builder import (  # noqa: E402
    build_story_threads, link_moments,
)
from export_dot_observer_data import export_dot_observer_data  # noqa: E402


def _run_seed(anchor: str, seed: int, ticks: int) -> dict:
    """Run engine + extract evidence for one seed; return summary dict."""
    observer = export_dot_observer_data(
        anchor_id=anchor, seed=seed, n_ticks=ticks,
    )
    moments = extract_moments(observer)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(observer)
    candidates = build_story_candidates(threads, moments, identity)
    if not candidates or not candidates[0].main_characters:
        return {"seed": seed, "skipped": True}
    main_name = candidates[0].main_characters[0]
    ev = extract_narrative_evidence(observer, main_name, identity_resolver=identity)
    fear = next((p for p in ev.main_agent_pressure_peaks if p.pressure == "fear"), None)
    return {
        "seed": seed,
        "main": main_name,
        "total_ticks": ev.total_ticks,
        "fear_sustained": fear.sustained_ticks if fear else 0,
        "fear_peak_tick": fear.peak_tick if fear else 0,
        "action_early": ev.main_agent_action_count_early,
        "action_late": ev.main_agent_action_count_late,
        "crowd_tense_ticks": ev.crowd_tense_ticks,
        "tense_pct": (
            ev.crowd_tense_ticks * 100 // max(1, ev.total_ticks)
        ),
        "logline": _ko_names(resolve_korean_josa(evidence_to_logline(ev))),
        "act3": _ko_names(resolve_korean_josa(evidence_to_act_summary(ev, 2))),
        "transitions_count": len(ev.main_agent_state_transitions),
        "co_occurrences_count": len(ev.world_co_occurrences),
        "skipped": False,
    }


def _markdown_table(rows: list[dict]) -> str:
    rows = [r for r in rows if not r.get("skipped")]
    if not rows:
        return "_(no data)_"

    out_lines: list[str] = []
    out_lines.append(
        "| seed | 두려움 지속 (단계) | 행동 수 (초반→후반) | 분위기 긴장 | 상태 변화 | 압력 동시 등장 |"
    )
    out_lines.append("|---:|---:|:---:|---:|---:|---:|")
    for r in rows:
        out_lines.append(
            f"| {r['seed']} | {r['fear_sustained']}/{r['total_ticks']} "
            f"| {r['action_early']} → {r['action_late']} "
            f"| {r['tense_pct']}% "
            f"| {r['transitions_count']} 회 "
            f"| {r['co_occurrences_count']} 회 |"
        )
    return "\n".join(out_lines)


def _markdown_loglines(rows: list[dict]) -> str:
    rows = [r for r in rows if not r.get("skipped")]
    out_lines: list[str] = []
    for r in rows:
        out_lines.append(f"### seed {r['seed']}")
        out_lines.append("")
        out_lines.append(f"**Logline**: {r['logline']}")
        out_lines.append("")
        out_lines.append(f"**Act 3**: {r['act3']}")
        out_lines.append("")
    return "\n".join(out_lines)


def _identical_check(rows: list[dict]) -> tuple[bool, list[str]]:
    rows = [r for r in rows if not r.get("skipped")]
    if len(rows) < 2:
        return True, []
    differences: list[str] = []
    if len({r["logline"] for r in rows}) > 1:
        differences.append("logline")
    if len({r["act3"] for r in rows}) > 1:
        differences.append("act3")
    if len({r["fear_sustained"] for r in rows}) > 1:
        differences.append("fear_sustained")
    if len({r["tense_pct"] for r in rows}) > 1:
        differences.append("tense_pct")
    return (not differences), differences


def run(anchor: str, seeds: list[int], ticks: int, out_path: Path | None) -> int:
    rows: list[dict] = []
    for seed in seeds:
        print(f"[seed {seed}] running engine...", flush=True)
        rows.append(_run_seed(anchor, seed, ticks))

    table = _markdown_table(rows)
    loglines = _markdown_loglines(rows)
    all_identical, fields_that_differ = _identical_check(rows)

    md = f"""# Seed Diversity — Data-driven Body Verification

> *anchor: `{anchor}`, seeds: {seeds}, ticks: {ticks}*

이 문서는 *데이터 기반 본문 합성기*가 실제로 작동함을 보여준다.
다른 seed로 시뮬레이션하면 observer dump의 수치가 달라지고, 그 수치를
본문이 직접 인용하므로 텍스트 자체가 달라진다.

## 수치 비교

{table}

## Logline / Act 3 본문

{loglines}

## 검증 결과

- 다른 본문이 나온 필드: {", ".join(fields_that_differ) if fields_that_differ else "(없음)"}
- 모든 seed가 동일한 본문인가: **{"YES (실패)" if all_identical else "NO (성공)"}**

이 산출물은 `engine/observer/data_narrative.py`의 `extract_narrative_evidence()` +
`evidence_to_logline / _act_summary`를 통해 자동 생성되었다.
"""
    print()
    print(md)

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"\nWrote: {out_path}")

    if all_identical:
        print("\n[FAIL] all seeds produced identical body text", file=sys.stderr)
        return 1
    return 0


def parse_seeds(s: str) -> list[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def main_cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--anchor", default="peter_scarcity_baseline")
    ap.add_argument("--seeds", default="0,3,7", help="comma-separated seeds")
    ap.add_argument("--ticks", type=int, default=200)
    ap.add_argument(
        "--output", default="docs/portfolio/demo/seed_diversity_demo.md",
        help='set to "" to skip writing the markdown file',
    )
    args = ap.parse_args()

    out_path = (ROOT / args.output) if args.output else None
    return run(
        anchor=args.anchor,
        seeds=parse_seeds(args.seeds),
        ticks=args.ticks,
        out_path=out_path,
    )


if __name__ == "__main__":
    sys.exit(main_cli())
