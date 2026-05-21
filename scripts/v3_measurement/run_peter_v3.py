"""v3 Phase 5+ -- Peter scenario 실측.

Content (Peter v3) → PersonV3Loop → Trajectory → RubricEvaluator → DiscoveryClass.

Spec: WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md §5 + WITNESS_V3_REDESIGN.md §6.
"""

from __future__ import annotations

import json
import os
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

CONTENT = ROOT / "content" / "peter" / "v3"


def run_simulation(seed: int = 0, n_ticks: int = 30) -> list[TrajectoryRecord]:
    loop = PersonV3Loop(
        initial_state_path=CONTENT / "initial_state.json",
        canonical_events_path=CONTENT / "canonical_events.json",
        seed=seed,
    )
    return loop.run(n_ticks)


def records_to_rubric_format(records: list[TrajectoryRecord]) -> list[dict]:
    """Translate TrajectoryRecord into the flat dict shape the rubric expects."""
    out = []
    for r in records:
        out.append({
            "tick": r.tick,
            "action_id": r.action_id,
            "action_kind": r.action_kind,
            "fear_like": r.fear_like,
            "event_triggered": len(r.fired_events) > 0,
            "event_category": r.event_category,
            "visible_signal": "",  # not used for peter scenario; content can fill
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
    # Vocabulary from observed trajectory (anachronism guard)
    vocab = set()
    for r in records:
        vocab.add(r["action_id"])
    # Add standard Peter canonical actions even if not observed in this run
    vocab.update({
        "follow_closely", "pray", "weep", "deny", "confess", "withdraw_in_fear",
        "flee", "draw_sword", "stay_awake", "fall_asleep", "assert_loyalty",
        "discuss_with_disciples", "follow_at_distance", "stay_hiding", "run_to_tomb",
    })

    # Canonical reference: a simplified Peter passion sequence
    canonical_sequence = [
        (5, "discuss_with_disciples"),  # last supper
        (10, "stay_awake"),              # gethsemane
        (12, "draw_sword"),              # arrest
        (13, "flee"),                    # after weapon drawn
        (17, "deny"),                    # denial 1
        (18, "deny"),                    # denial 2
        (19, "deny"),                    # denial 3
        (20, "weep"),                    # after eye contact
        (28, "confess"),                 # restoration
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
                          state_fields=["fear", "hope", "grief",
                                        "confusion", "fatigue"])
    novelty = NoveltyCritic(copy_threshold=2.0, noise_threshold=20.0)

    return RubricEvaluator(
        character=character, canon=canon, causal=causal, novelty=novelty,
        character_min_composite=0.4,
    )


def summarize(records: list[TrajectoryRecord]) -> dict:
    from collections import Counter
    action_counts = Counter(r.action_id for r in records)
    event_counts = Counter()
    for r in records:
        for e in r.fired_events:
            event_counts[e] += 1
    # Final state values
    final = records[-1]
    return {
        "n_ticks": len(records),
        "action_counts": dict(action_counts),
        "event_counts": dict(event_counts),
        "final_state": final.state,
        "final_pressures": final.pressures,
        "final_derived": final.derived,
    }


def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    out_dir = ROOT / "docs" / "person" / "v3_measurement"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[v3 run] seed={seed} ticks={n_ticks}")
    records = run_simulation(seed=seed, n_ticks=n_ticks)
    print(f"  trajectory: {len(records)} records")

    # Print side-by-side timeline
    print("\n  tick | action                  | event(s)           | fear | grief | loyalty[pf]")
    print("  " + "-" * 90)
    for r in records:
        loyalty_pf = r.state.get("loyalty", {}).get("primary_figure", 0.0)
        ev_str = ",".join(r.fired_events[:2])[:18]
        print(f"  {r.tick:>4} | {r.action_id:<23} | {ev_str:<18} | "
              f"{r.fear_like:>4.1f} | {r.state.get('grief', 0):>5.1f} | "
              f"{loyalty_pf:>5.1f}")

    # Summary
    summary = summarize(records)
    print(f"\n  action distribution: {summary['action_counts']}")
    # faith_stage is Derived now (Dynamics Step 1). Compute via state_derived.
    from engine.person.state_derived import faith_stage_tag
    from engine.person.state_v3 import ActiveState
    final_active = ActiveState(**{
        k: v for k, v in summary["final_state"].items()
        if k in {"fear", "hope", "grief", "confusion", "joy", "anger", "awe",
                 "fatigue", "hunger", "vitality", "doubt", "resolve", "trauma",
                 "love", "loyalty", "trust", "belonging", "guilt", "shame"}
    })
    fs_tag = faith_stage_tag(final_active)
    print(f"  final state sample: fear={summary['final_state'].get('fear'):.2f}, "
          f"faith_stage_tag={fs_tag} (derived)")
    print(f"  final pressures: social_threat={summary['final_pressures'].get('social_threat'):.2f}, "
          f"shame_exposure={summary['final_pressures'].get('shame_exposure'):.2f}")

    # Rubric evaluation
    rubric_records = records_to_rubric_format(records)
    evaluator = build_rubric_evaluator(rubric_records)
    report = evaluator.evaluate(rubric_records)
    print(f"\n[Rubric] DiscoveryClass: {report.discovery_class.value}")
    print(f"  Character composite: {report.character.composite:.3f}")
    print(f"  Canon valid: {report.canon.is_canon_valid}, soft_drift: {report.canon.soft_drift:.2f}")
    print(f"  Causal smoothness: {report.causal.smoothness_score:.3f}, "
          f"unexplained_jumps: {report.causal.unexplained_jumps}")
    print(f"  Novelty band: {report.novelty.novelty_band}")
    print(f"  Justification: {report.justification}")

    # Save artifacts -- Dynamics Step 6 uses _v2 suffix to preserve baseline
    suffix = "_v2" if os.environ.get("WITNESS_DYNAMICS_RUN") == "1" else ""
    out_json = out_dir / f"peter_v3_seed{seed}_ticks{n_ticks}{suffix}.json"
    payload = {
        "seed": seed,
        "n_ticks": n_ticks,
        "summary": summary,
        "rubric": {
            "discovery_class": report.discovery_class.value,
            "character_composite": report.character.composite,
            "canon_valid": report.canon.is_canon_valid,
            "canon_soft_drift": report.canon.soft_drift,
            "causal_smoothness": report.causal.smoothness_score,
            "causal_unexplained_jumps": report.causal.unexplained_jumps,
            "novelty_band": report.novelty.novelty_band,
            "canon_distance": report.novelty.canon_distance,
            "justification": report.justification,
        },
        "trajectory_summary": [
            {"tick": r.tick, "action": r.action_id, "events": r.fired_events,
             "fear": r.fear_like, "event_category": r.event_category}
            for r in records
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  saved: {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
