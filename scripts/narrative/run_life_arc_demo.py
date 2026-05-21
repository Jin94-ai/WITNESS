"""Run Life Arc Demo — phased simulation → time-windowed narrative timeline.

Per user directive (2026-05-08): "이야기의 흐름을 특정한 시간대로 두고 확인할 수
있도록 결과물을 만들자. 베드로의 인생 / 예수님의 공생애 3년 이런식으로."

이 스크립트는:
    1. PhasedSimulationWorld로 베드로 (또는 다른 agent) 생애 phased run
    2. action_histories + canonical_events.json + emotion trajectory 결합
    3. 시간대별 한국어 narrative timeline markdown 생성

산출:
    docs/portfolio/demo/life_arc_demo.md   — 한국어 timeline (메인)
    docs/portfolio/demo/life_arc_demo.json — 데이터 raw (자동화 도구용)

Usage:
    python scripts/narrative/run_life_arc_demo.py
    python scripts/narrative/run_life_arc_demo.py --seed 7
    python scripts/narrative/run_life_arc_demo.py --full-passion --seed 0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse the existing phase config + rule engine. demo_phased.py wraps stdout
# at import time on Windows; do not double-wrap here.
from engine.observer.life_arc_narrative import (  # noqa: E402
    build_life_arc_narrative,
    render_life_arc_html,
    render_life_arc_md,
)
from engine.simulation.phased_world import PhasedSimulationWorld  # noqa: E402
from examples.demo_phased import _build_config, _rules  # noqa: E402

# Content-layer human-readable Korean labels for the standard 5-phase
# arc. Lives in the orchestrator (not engine) so the engine module stays
# content-agnostic.
PETER_PHASE_LABELS_KO: dict[str, str] = {
    "01_calling":              "1막: 부르심",
    "02_galilean":             "2막: 갈릴리 사역",
    "03_confession":           "3막: 신앙 고백과 변화산",
    "04_journey":              "4막: 예루살렘으로",
    "04_journey_to_jerusalem": "4막: 예루살렘으로",
    "05_passion":              "5막: 수난과 부인",
}


def main(
    seed: int,
    with_passion: bool,
    output_dir: Path,
    window_strategy: str = "by_phase",
) -> int:
    print(f"[1/3] Running phased simulation (seed={seed}, full_passion={with_passion})...")
    config = _build_config(with_passion=with_passion)
    world = PhasedSimulationWorld(config, rule_engine=_rules(False))
    result = world.run(seed=seed)

    # Map phase_id → canonical_events_path (handles passion's non-standard
    # location at content/peter/canonical_events.json)
    phase_event_paths = {
        p.phase_id: p.canonical_events_path
        for p in (config.phases or [])
        if p.canonical_events_path
    }

    print(f"[2/3] Building life arc narrative (window_strategy={window_strategy})...")
    arc = build_life_arc_narrative(
        result, agent_id="peter", agent_label="베드로", seed=seed,
        phase_event_paths=phase_event_paths,
        plain_phase_labels=PETER_PHASE_LABELS_KO,
        window_strategy=window_strategy,
    )

    print("[3/3] Writing outputs...")
    output_dir.mkdir(parents=True, exist_ok=True)
    md = render_life_arc_md(arc)
    html = render_life_arc_html(arc)
    suffix = "" if window_strategy == "by_phase" else f"_{window_strategy}"
    (output_dir / f"life_arc_demo{suffix}.md").write_text(md, encoding="utf-8")
    (output_dir / f"life_arc_demo{suffix}.html").write_text(html, encoding="utf-8")
    (output_dir / f"life_arc_demo{suffix}.json").write_text(
        json.dumps(arc.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total_events = sum(len(w.canonical_events) for w in arc.windows)
    suffix = "" if window_strategy == "by_phase" else f"_{window_strategy}"
    print()
    print(f"Done. {arc.total_days:.1f} days, "
          f"{len(arc.windows)} windows, {total_events} canonical events fired.")
    print(f"  {output_dir / f'life_arc_demo{suffix}.md'}")
    print(f"  {output_dir / f'life_arc_demo{suffix}.html'}")
    print(f"  {output_dir / f'life_arc_demo{suffix}.json'}")
    return 0


def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--full-passion", action="store_true",
                     help="include 5th phase (passion arc, ~42 days)")
    ap.add_argument(
        "--window", choices=["by_phase", "by_week"], default="by_phase",
        help="time window strategy (by_phase = 4-5 wide bands, "
             "by_week = ~20 narrow weekly bands)",
    )
    ap.add_argument(
        "--output", default="docs/portfolio/demo",
        help="output directory (defaults to portfolio demo folder)",
    )
    args = ap.parse_args()
    return main(seed=args.seed, with_passion=args.full_passion,
                output_dir=ROOT / args.output,
                window_strategy=args.window)


if __name__ == "__main__":
    sys.exit(cli())
