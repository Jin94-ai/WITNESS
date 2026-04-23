"""v3 Phase 2 v2 -- Judas scenario 실측 (engine universality 검증).

Rule #5: 3번째 시나리오 전까지 universality 금지. 이 script는 engine이
2번째 scenario를 수용하는지 부분 검증용. Peter-specific 발견 주장 없음.

Run:
    python scripts/v3_measurement/run_judas_v3.py [seed=0] [ticks=30]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.constraint.hard_constraints import HardConstraintChecker  # noqa: E402
from engine.constraint.soft_constraints import SoftConstraintScorer  # noqa: E402
from engine.person.loop import PersonV3Loop, TrajectoryRecord  # noqa: E402
from engine.rubric import (  # noqa: E402
    CanonCritic,
    CausalCritic,
    CharacterCritic,
    NoveltyCritic,
    RubricEvaluator,
)

CONTENT = ROOT / "content" / "judas" / "v3"


def run_simulation(seed: int = 0, n_ticks: int = 30) -> list[TrajectoryRecord]:
    loop = PersonV3Loop(
        initial_state_path=CONTENT / "initial_state.json",
        canonical_events_path=CONTENT / "canonical_events.json",
        seed=seed,
    )
    return loop.run(n_ticks)


def records_to_rubric_format(records: list[TrajectoryRecord]) -> list[dict]:
    out = []
    for r in records:
        out.append({
            "tick": r.tick,
            "action_id": r.action_id,
            "action_kind": r.action_kind,
            "fear_like": r.fear_like,
            "event_triggered": len(r.fired_events) > 0,
            "event_category": r.event_category,
            "visible_signal": "",
            "is_sacred": False,
            "state": {
                "fear": r.state.get("fear", 0.0),
                "hope": r.state.get("hope", 0.0),
                "grief": r.state.get("grief", 0.0),
                "confusion": r.state.get("confusion", 0.0),
                "love": max((r.state.get("love") or {"_": 0}).values()),
                "fatigue": r.state.get("fatigue", 0.0),
                "exhaustion_emotional": r.derived.get("stress", 0.0),
            },
        })
    return out


def build_rubric_evaluator(records: list[dict]) -> RubricEvaluator:
    vocab = set(r["action_id"] for r in records)
    vocab.update({
        "follow_closely", "pray", "weep", "deny", "confess", "withdraw_in_fear",
        "flee", "draw_sword", "stay_awake", "fall_asleep", "assert_loyalty",
        "discuss_with_disciples", "follow_at_distance", "stay_hiding", "run_to_tomb",
    })

    # Canonical reference: Judas passion sequence
    # Note: vocabulary limits — no "betray_with_kiss" / "return_silver" /
    # "self_harm" actions in ACTIONS tuple. Alignment uses closest proxies.
    canonical_sequence = [
        (3, "discuss_with_disciples"),   # bargaining meeting
        (5, "discuss_with_disciples"),   # last supper
        (7, "withdraw_in_fear"),         # exposed by Jesus, retreat
        (8, "flee"),                     # leaves last supper
        (13, "assert_loyalty"),          # false greeting (kiss)
        (20, "weep"),                    # remorse onset
        (22, "confess"),                 # returns silver (symbolic confession)
    ]

    hard = HardConstraintChecker(action_vocabulary=vocab)
    soft = SoftConstraintScorer(canonical_sequence=canonical_sequence)

    character = CharacterCritic(
        impulsivity_threshold=0.15,
        relationship_patterns={
            "canonical": {"approach", "express", "avoid", "defensive", "neutral"},
        },
        oscillation_target=0.2,
    )
    canon = CanonCritic(hard=hard, soft=soft, reproduction_threshold=3.0)
    causal = CausalCritic(jump_threshold=4.0,
                          state_fields=["fear", "hope", "grief", "confusion",
                                        "fatigue"])
    novelty = NoveltyCritic(copy_threshold=2.0, noise_threshold=20.0)

    return RubricEvaluator(
        character=character, canon=canon, causal=causal, novelty=novelty,
        character_min_composite=0.4,
    )


def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    out_dir = ROOT / "docs" / "person" / "v3_measurement"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[v3 Judas run] seed={seed} ticks={n_ticks}")
    records = run_simulation(seed=seed, n_ticks=n_ticks)
    print(f"  trajectory: {len(records)} records")

    print("\n  tick | action                  | event(s)           | guilt | grief | doubt")
    print("  " + "-" * 80)
    for r in records:
        guilt_pf = r.state.get("guilt", {}).get("primary_figure", 0.0)
        ev_str = ",".join(r.fired_events[:2])[:18]
        print(f"  {r.tick:>4} | {r.action_id:<23} | {ev_str:<18} | "
              f"{guilt_pf:>5.1f} | {r.state.get('grief', 0):>5.1f} | "
              f"{r.state.get('doubt', 0):>5.1f}")

    rubric_records = records_to_rubric_format(records)
    evaluator = build_rubric_evaluator(rubric_records)
    report = evaluator.evaluate(rubric_records)
    print(f"\n[Rubric] DiscoveryClass: {report.discovery_class.value}")
    print(f"  Character composite: {report.character.composite:.3f}")
    print(f"  Canon valid: {report.canon.is_canon_valid}, "
          f"soft_drift: {report.canon.soft_drift:.2f}")
    print(f"  Causal smoothness: {report.causal.smoothness_score:.3f}, "
          f"unexplained_jumps: {report.causal.unexplained_jumps}")
    print(f"  Novelty band: {report.novelty.novelty_band}")

    out_json = out_dir / f"judas_v3_seed{seed}_ticks{n_ticks}.json"
    payload = {
        "seed": seed,
        "n_ticks": n_ticks,
        "rubric": {
            "discovery_class": report.discovery_class.value,
            "character_composite": report.character.composite,
            "canon_valid": report.canon.is_canon_valid,
            "canon_soft_drift": report.canon.soft_drift,
            "causal_smoothness": report.causal.smoothness_score,
            "causal_unexplained_jumps": report.causal.unexplained_jumps,
            "novelty_band": report.novelty.novelty_band,
        },
        "trajectory_summary": [
            {"tick": r.tick, "action": r.action_id, "events": r.fired_events}
            for r in records
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\n  saved: {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
