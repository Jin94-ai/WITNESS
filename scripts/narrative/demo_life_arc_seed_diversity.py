"""Demo Life Arc Seed Diversity — show that life arc choices vary by seed.

Per user directive (2026-05-08): 베드로의 인생 timeline이 *engine-driven*임을
입증. 다른 seed로 시뮬레이션하면 *같은 정경 사건*에 대해 베드로가 *다른 행동*을
선택한다.

이 스크립트는 N seeds를 한 번에 실행해 시뮬레이션 베드로의 *선택 차이*를
markdown 표로 자동 생성. 산출물은 portfolio reviewer가 한 눈에
"engine-driven 맞다"를 확인할 수 있는 검증 자료.

Usage:
    python scripts/narrative/demo_life_arc_seed_diversity.py
    python scripts/narrative/demo_life_arc_seed_diversity.py --seeds 0,7,11
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ensure_utf8_stdout() -> None:
    if sys.platform == "win32" and not isinstance(
        sys.stdout, io.TextIOWrapper,
    ):
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace",
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace",
        )
    elif sys.platform == "win32":
        # Already wrapped (e.g. by demo_phased.main); switch encoding to utf-8
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass

from engine.observer.life_arc_narrative import build_life_arc_narrative  # noqa: E402
from engine.simulation.phased_world import PhasedSimulationWorld  # noqa: E402

# demo_phased.py wraps stdout at main() time only — safe to import here
from examples.demo_phased import _build_config, _rules  # noqa: E402
from scripts.narrative.run_life_arc_demo import (  # noqa: E402
    PETER_PHASE_LABELS_KO,
)


def _run_arc_for_seed(seed: int, with_passion: bool = True):
    config = _build_config(with_passion=with_passion)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=seed)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or [])
        if p.canonical_events_path
    }
    return build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=seed,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
    )


def _flatten_events(arc) -> dict[str, dict]:
    """event_id → {description, scripture_ref, chosen_action, chosen_action_description, days}."""
    out: dict[str, dict] = {}
    for w in arc.windows:
        for e in w.canonical_events:
            out[e.event_id] = {
                "description": e.description,
                "scripture_ref": e.scripture_ref,
                "chosen_action": e.chosen_action,
                "chosen_action_description": e.chosen_action_description,
                "days": e.absolute_days,
            }
    return out


def _short(s: str, n: int = 30) -> str:
    if len(s) <= n:
        return s
    return s[:n - 1] + "…"


def _format_choice(record: dict | None) -> str:
    if record is None:
        return "_(미발화)_"
    if record["chosen_action_description"]:
        return f"**{_short(record['chosen_action_description'], 22)}** `{record['chosen_action']}`"
    return f"`{record['chosen_action']}`"


def run(seeds: list[int], with_passion: bool, out_path: Path | None) -> int:
    arcs = {}
    flat = {}
    for s in seeds:
        print(f"[seed {s}] running phased simulation...", flush=True)
        arcs[s] = _run_arc_for_seed(s, with_passion=with_passion)
        flat[s] = _flatten_events(arcs[s])

    # 모든 seed에서 등장한 event_id의 합집합
    all_event_ids: list[str] = []
    seen: set[str] = set()
    # 첫 seed의 시간순으로 정렬한 후 나머지 seed에서만 등장한 것 추가
    primary = list(flat[seeds[0]].items())
    primary.sort(key=lambda kv: kv[1]["days"])
    for eid, _ in primary:
        if eid not in seen:
            all_event_ids.append(eid)
            seen.add(eid)
    for s in seeds[1:]:
        for eid in flat[s]:
            if eid not in seen:
                all_event_ids.append(eid)
                seen.add(eid)

    # 차이 카운트
    differing_events: list[str] = []
    for eid in all_event_ids:
        choices = {flat[s].get(eid, {}).get("chosen_action") for s in seeds}
        choices.discard(None)
        if len(choices) >= 2:
            differing_events.append(eid)

    # Markdown table
    lines: list[str] = []
    lines.append("# Life Arc Seed Diversity — Engine-driven 검증")
    lines.append("")
    lines.append(
        f"> *anchor: peter, seeds: {seeds}, full_passion: {with_passion}*"
    )
    lines.append("")
    lines.append(
        "이 문서는 *베드로 공생애 시뮬레이션*이 진짜 engine-driven임을 보여준다. "
        "다른 seed → 다른 observer dump → 같은 정경 사건에 대해 베드로가 *다른 행동*을 선택. "
        "사건 description / scripture_ref는 `canonical_events.json`에서 verbatim, 선택은 "
        "engine `action_histories`에서 직접 인용된다."
    )
    lines.append("")

    lines.append(f"**총 {len(all_event_ids)}개 정경 사건 중 {len(differing_events)}개에서 seed별 다른 선택.**")
    lines.append("")

    # Header row
    header = "| 일째 | 사건 | " + " | ".join(f"seed {s}" for s in seeds) + " |"
    sep = "|---:|:---|" + "|".join(":---" for _ in seeds) + "|"
    lines.append(header)
    lines.append(sep)

    for eid in all_event_ids:
        # 어느 seed든 days가 있는 첫 record
        rec_for_label = next((flat[s].get(eid) for s in seeds if eid in flat[s]), None)
        if rec_for_label is None:
            continue
        days = rec_for_label["days"]
        desc = _short(rec_for_label["description"], 35)
        ref = rec_for_label["scripture_ref"]
        if ref and f"({ref})" not in desc:
            label = f"{desc} *({ref})*"
        else:
            label = desc

        # 다른 선택 highlighting
        choices = {flat[s].get(eid, {}).get("chosen_action") for s in seeds}
        choices.discard(None)
        diff_marker = " ⚡" if len(choices) >= 2 else ""

        cells = [_format_choice(flat[s].get(eid)) for s in seeds]
        lines.append(
            f"| {days:.1f}{diff_marker} | {label} | " + " | ".join(cells) + " |"
        )

    lines.append("")
    lines.append("⚡ = 같은 정경 사건에 대해 두 seed 이상이 다른 선택")
    lines.append("")
    lines.append(
        "*이 표는 `scripts/narrative/demo_life_arc_seed_diversity.py`에서 자동 생성. "
        "선택 텍스트는 `canonical_events.json` action_options.description (한국어)에서, "
        "선택 자체는 engine action_histories에서 인용된다.*"
    )

    md = "\n".join(lines)
    print()
    print(md)

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"\nWrote: {out_path}")

    if not differing_events:
        print("\n[FAIL] no event differs across seeds — narrative may not be engine-driven",
              file=sys.stderr)
        return 1
    return 0


def parse_seeds(s: str) -> list[int]:
    return [int(x.strip()) for x in s.split(",") if x.strip()]


def cli() -> int:
    _ensure_utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", default="0,7,11")
    ap.add_argument("--no-passion", action="store_true",
                    help="skip phase 5 (use 4-phase 101-day arc)")
    ap.add_argument("--output",
                    default="docs/portfolio/demo/life_arc_seed_diversity.md")
    args = ap.parse_args()
    out = (ROOT / args.output) if args.output else None
    return run(parse_seeds(args.seeds), with_passion=not args.no_passion,
                out_path=out)


if __name__ == "__main__":
    sys.exit(cli())
