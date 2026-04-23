"""Multi-seed ensemble runner (C2).

Phase 2 v2 Dynamics + B2 retune 검증: single-seed=0 결과가 대표성 있는가?
10 seeds 에서 drift / discovery_class / action_counts 분포 수집.

Run:
    python scripts/v3_measurement/run_peter_v3_ensemble.py [n_seeds=10] [n_ticks=30]

Outputs:
    docs/person/v3_measurement/peter_v3_ensemble_N<n_seeds>.json
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
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


def build_evaluator(records: list[dict]) -> RubricEvaluator:
    vocab = {r["action_id"] for r in records}
    vocab.update({
        "follow_closely", "pray", "weep", "deny", "confess", "withdraw_in_fear",
        "flee", "draw_sword", "stay_awake", "fall_asleep", "assert_loyalty",
        "discuss_with_disciples", "follow_at_distance", "stay_hiding", "run_to_tomb",
    })
    canonical_sequence = [
        (5, "discuss_with_disciples"), (10, "stay_awake"), (12, "draw_sword"),
        (13, "flee"), (17, "deny"), (18, "deny"), (19, "deny"), (20, "weep"),
        (28, "confess"),
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
                          state_fields=["fear", "hope", "grief", "confusion", "fatigue"])
    novelty = NoveltyCritic(copy_threshold=2.0, noise_threshold=20.0)
    return RubricEvaluator(
        character=character, canon=canon, causal=causal, novelty=novelty,
        character_min_composite=0.4,
    )


def run_one(seed: int, n_ticks: int) -> dict:
    loop = PersonV3Loop(
        initial_state_path=CONTENT / "initial_state.json",
        canonical_events_path=CONTENT / "canonical_events.json",
        seed=seed,
    )
    records = loop.run(n_ticks)
    rubric_records = records_to_rubric_format(records)
    evaluator = build_evaluator(rubric_records)
    report = evaluator.evaluate(rubric_records)

    action_counts = Counter(r.action_id for r in records)
    canonical_ticks = {
        5: "discuss_with_disciples", 10: "stay_awake", 12: "draw_sword",
        13: "flee", 17: "deny", 18: "deny", 19: "deny", 20: "weep",
        28: "confess",
    }
    canonical_matches = sum(
        1 for r in records
        if r.tick in canonical_ticks and r.action_id == canonical_ticks[r.tick]
    )
    return {
        "seed": seed,
        "discovery_class": report.discovery_class.value,
        "canon_soft_drift": report.canon.soft_drift,
        "canon_valid": report.canon.is_canon_valid,
        "character_composite": report.character.composite,
        "causal_smoothness": report.causal.smoothness_score,
        "causal_unexplained_jumps": report.causal.unexplained_jumps,
        "novelty_band": report.novelty.novelty_band,
        "action_counts": dict(action_counts),
        "canonical_matches": canonical_matches,
        "deny_count": action_counts.get("deny", 0),
        "weep_count": action_counts.get("weep", 0),
        "confess_count": action_counts.get("confess", 0),
        "run_to_tomb_count": action_counts.get("run_to_tomb", 0),
        "final_fear": records[-1].state.get("fear", 0.0),
        "final_grief": records[-1].state.get("grief", 0.0),
    }


def aggregate(runs: list[dict]) -> dict:
    def stats(key: str) -> dict:
        vals = [r[key] for r in runs]
        return {
            "mean": statistics.mean(vals),
            "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals),
            "max": max(vals),
            "median": statistics.median(vals),
        }

    discovery_classes = Counter(r["discovery_class"] for r in runs)
    return {
        "n_seeds": len(runs),
        "canon_soft_drift": stats("canon_soft_drift"),
        "character_composite": stats("character_composite"),
        "causal_smoothness": stats("causal_smoothness"),
        "canonical_matches": stats("canonical_matches"),
        "deny_count": stats("deny_count"),
        "weep_count": stats("weep_count"),
        "confess_count": stats("confess_count"),
        "run_to_tomb_count": stats("run_to_tomb_count"),
        "final_fear": stats("final_fear"),
        "final_grief": stats("final_grief"),
        "discovery_class_distribution": dict(discovery_classes),
        "canon_valid_rate": sum(1 for r in runs if r["canon_valid"]) / len(runs),
    }


def main() -> int:
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    n_ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    out_dir = ROOT / "docs" / "person" / "v3_measurement"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[v3 ensemble] n_seeds={n_seeds} ticks={n_ticks}")
    runs = []
    for seed in range(n_seeds):
        r = run_one(seed, n_ticks)
        runs.append(r)
        print(f"  seed={seed:>2}: drift={r['canon_soft_drift']:>5.2f} "
              f"class={r['discovery_class']:>24} "
              f"matches={r['canonical_matches']}/9 "
              f"deny={r['deny_count']} weep={r['weep_count']} "
              f"confess={r['confess_count']} "
              f"run_to_tomb={r['run_to_tomb_count']}")

    agg = aggregate(runs)
    print("\n[Aggregate]")
    d = agg["canon_soft_drift"]
    print(f"  drift: mean={d['mean']:.2f} stdev={d['stdev']:.2f} "
          f"[{d['min']:.1f}, {d['max']:.1f}] median={d['median']:.1f}")
    m = agg["canonical_matches"]
    print(f"  canonical_matches: mean={m['mean']:.2f} "
          f"stdev={m['stdev']:.2f} [{m['min']}, {m['max']}]")
    print(f"  discovery_class distribution: {agg['discovery_class_distribution']}")
    print(f"  canon_valid_rate: {agg['canon_valid_rate']:.0%}")
    cc = agg["character_composite"]
    print(f"  character_composite: mean={cc['mean']:.3f} stdev={cc['stdev']:.3f}")

    payload = {
        "n_seeds": n_seeds,
        "n_ticks": n_ticks,
        "runs": runs,
        "aggregate": agg,
    }
    out_json = out_dir / f"peter_v3_ensemble_N{n_seeds}.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\n  saved: {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
