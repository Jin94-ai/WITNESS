"""Phase G Step G2 — Run rubric on 45 reference trajectories.

Loads data/reference/witness_trajectories_45.json and applies the
RubricEvaluator to each trajectory. Saves results to
data/reference/evaluation_results.json.

Usage:
    python scripts/v3_measurement/run_reference_evaluation.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.constraint.hard_constraints import HardConstraintChecker  # noqa: E402
from engine.constraint.soft_constraints import SoftConstraintScorer  # noqa: E402
from engine.rubric import (  # noqa: E402
    CanonCritic,
    CausalCritic,
    CharacterCritic,
    ContextBreakCritic,
    NoveltyCritic,
    RubricEvaluator,
    SceneResponseCritic,
)
from engine.rubric.reference_loader import (  # noqa: E402
    ReferenceTrajectory,
    default_path,
    load_reference_set,
)


# =============================================================================
# Adapter: reference tick → rubric record shape
# =============================================================================

# Same mapping as PersonV3Loop._action_kind (kept in-sync manually since
# there's no single source of truth yet).
_ACTION_KIND_MAP: dict[str, str] = {
    # avoid
    "flee": "avoid", "withdraw_in_fear": "avoid",
    "stay_hiding": "avoid", "follow_at_distance": "avoid",
    # approach
    "follow_closely": "approach", "assert_loyalty": "approach",
    "draw_sword": "approach", "run_to_tomb": "approach",
    # express
    "pray": "express", "weep": "express", "confess": "express",
    # defensive
    "deny": "defensive", "fall_asleep": "defensive",
    # neutral default
}


def _action_kind(action_id: str) -> str:
    return _ACTION_KIND_MAP.get(action_id, "neutral")


def _event_category(event_in: list[str], event_out: str | None) -> str:
    if event_in:
        return "canonical"
    if event_out:
        return "action_caused"
    return "voluntary"


def _scalar_love(state: dict) -> float:
    love = state.get("love", {})
    if not love:
        return 0.0
    return float(max(love.values()))


def _derived_stress(state: dict) -> float:
    """Match engine/person/state_derived._stress:
    0.4*fear + 0.3*confusion + 0.3*fatigue."""
    return float(
        0.4 * state.get("fear", 0.0)
        + 0.3 * state.get("confusion", 0.0)
        + 0.3 * state.get("fatigue", 0.0)
    )


def _scalar_target(state: dict, field: str, key: str = "primary_figure") -> float:
    """Extract scalar from a target-aware dict field."""
    d = state.get(field, {})
    if isinstance(d, dict):
        return float(d.get(key, 0.0))
    return float(d) if isinstance(d, (int, float)) else 0.0


def trajectory_to_records(t: ReferenceTrajectory) -> list[dict]:
    out = []
    for tr in t.ticks:
        s = tr.state
        flat_state = {
            "fear": s.get("fear", 0.0),
            "hope": s.get("hope", 0.0),
            "grief": s.get("grief", 0.0),
            "confusion": s.get("confusion", 0.0),
            "anger": s.get("anger", 0.0),
            "awe": s.get("awe", 0.0),
            "fatigue": s.get("fatigue", 0.0),
            "love": _scalar_love(s),
            # Phase H additions: target-aware scalars for character_critic
            "loyalty_pf": _scalar_target(s, "loyalty"),
            "trust_pf": _scalar_target(s, "trust"),
            # Guilt/grief used by character_critic spike detection
            "guilt": s.get("guilt", {}),
            "exhaustion_emotional": _derived_stress(s),
        }
        out.append({
            "tick": tr.tick,
            "action_id": tr.action,
            "action_kind": _action_kind(tr.action),
            "fear_like": float(s.get("fear", 0.0)),
            "event_in": list(tr.event_in),  # Phase H: scene_response + context_break
            "event_out": tr.event_out,
            "event_triggered": len(tr.event_in) > 0,
            "event_category": _event_category(tr.event_in, tr.event_out),
            "visible_signal": "",
            "is_sacred": False,
            "state": flat_state,
        })
    return out


# =============================================================================
# Evaluator factory (Peter scenario — same as run_peter_v3)
# =============================================================================

CANONICAL_SEQUENCE = [
    (5, "discuss_with_disciples"),
    (10, "stay_awake"),
    (12, "draw_sword"),
    (13, "flee"),
    (17, "deny"),
    (18, "deny"),
    (19, "deny"),
    (20, "weep"),
    (28, "confess"),
]

ACTION_VOCAB = {
    "follow_closely", "pray", "weep", "deny", "confess", "withdraw_in_fear",
    "flee", "draw_sword", "stay_awake", "fall_asleep", "assert_loyalty",
    "discuss_with_disciples", "follow_at_distance", "stay_hiding", "run_to_tomb",
    # Plausible-alternative / noise trajectory vocabulary items
    "jump_into_sea", "accept_washing", "resist_washing", "watch_quietly",
    "stay_on_boat", "join_crowd",
}


def build_evaluator(
    *,
    reproduction_threshold: float = 28.3,  # Phase G calibrated P90
    character_min: float = 0.4,
    scene_fit_min: float = 0.5,
    # Phase H calibration target: canonical max 0.067 << alt median 0.233
    # Using midpoint between alt median (0.233) and noise median (0.400) = 0.3
    break_threshold: float = 0.30,
    novelty_low: float = 0.25,
    novelty_high: float = 0.75,
    # Legacy kwargs accepted for backward compatibility (ignored by Phase H critics)
    noise_threshold: float | None = None,
    copy_threshold: float | None = None,
) -> RubricEvaluator:
    """Phase H 4축 독립 rubric factory."""
    hard = HardConstraintChecker(action_vocabulary=ACTION_VOCAB)
    soft = SoftConstraintScorer(canonical_sequence=CANONICAL_SEQUENCE)
    character = CharacterCritic(
        unexplained_drop_threshold=2.0,
        minimum_final_identity=4.0,
        repentance_response_window=5,
        spike_threshold=2.0,
    )
    scene_response = SceneResponseCritic(fit_threshold=scene_fit_min)
    context_break = ContextBreakCritic(break_threshold=break_threshold)
    canon = CanonCritic(
        hard=hard, soft=soft, reproduction_threshold=reproduction_threshold,
    )
    causal = CausalCritic(
        jump_threshold=4.0,
        state_fields=["fear", "hope", "grief", "confusion", "fatigue"],
    )
    novelty = NoveltyCritic(
        meaningful_low=novelty_low, meaningful_high=novelty_high,
    )
    return RubricEvaluator(
        character=character,
        scene_response=scene_response,
        context_break=context_break,
        canon=canon, causal=causal, novelty=novelty,
        character_min_composite=character_min,
        scene_fit_min=scene_fit_min,
    )


# =============================================================================
# Main
# =============================================================================

def evaluate_all(
    ref_path: Path | None = None,
    out_path: Path | None = None,
    *,
    evaluator: RubricEvaluator | None = None,
) -> dict:
    ref_path = ref_path or default_path()
    out_path = out_path or (ROOT / "data" / "reference" / "evaluation_results.json")
    evaluator = evaluator or build_evaluator()

    ref = load_reference_set(ref_path)
    results = []
    for t in ref.trajectories:
        records = trajectory_to_records(t)
        report = evaluator.evaluate(records)
        results.append({
            "trajectory_id": t.trajectory_id,
            "category": t.category,
            "noise_level": t.noise_level,
            "scores": {
                # Phase H 4축
                "character_composite": float(report.character.composite),
                "character_relation_stability": float(report.character.relation_stability),
                "character_identity_retention": float(report.character.identity_retention),
                "character_recovery_plausibility": float(report.character.recovery_plausibility),
                "scene_response_fit": float(report.scene_response.fit_rate),
                "scene_response_n_observed": int(report.scene_response.n_scenes_observed),
                "context_break_rate": float(report.context_break.break_rate),
                "context_break_affordance": int(report.context_break.affordance_violations),
                "context_break_scene_mismatch": int(report.context_break.scene_mismatch_count),
                "context_break_motive_gap": int(report.context_break.motive_gap_count),
                "context_coherent": bool(report.context_break.is_context_coherent),
                "novelty_band": str(report.novelty.novelty_band),
                "novelty_family_variation": float(report.novelty.response_family_variation),
                "novelty_branching_coherence": float(report.novelty.branching_coherence),
                "novelty_action_diversity": float(report.novelty.action_diversity),
                "novelty_structured_deviation": float(report.novelty.structured_deviation),
                # Canon + Causal (gates)
                "canon_valid": bool(report.canon.is_canon_valid),
                "canon_soft_drift": float(report.canon.soft_drift),
                "canon_is_reproducing": bool(report.canon.is_canon_reproducing),
                "causal_smoothness": float(report.causal.smoothness_score),
                "causal_unexplained_jumps": int(report.causal.unexplained_jumps),
            },
            "discovery_class": report.discovery_class.value,
            "justification": report.justification,
        })

    # Summary
    by_cat_class: dict[str, Counter] = {
        "canonical_like": Counter(),
        "plausible_alternative": Counter(),
        "obvious_noise": Counter(),
    }
    for r in results:
        by_cat_class[r["category"]][r["discovery_class"]] += 1

    summary = {
        "n_trajectories": len(results),
        "class_distribution_by_category": {
            k: dict(v) for k, v in by_cat_class.items()
        },
        "evaluator_thresholds": {
            "reproduction_threshold": evaluator._canon._repro_t,
            "character_min_composite": evaluator._char_min,
            "scene_fit_min": evaluator._scene_fit_min,
            "novelty_meaningful_low": evaluator._novelty._low,
            "novelty_meaningful_high": evaluator._novelty._high,
            "context_break_threshold": evaluator._ctx._break_t,
        },
    }

    payload = {
        "schema_version": "witness.v3.evaluation-results.0.1",
        "summary": summary,
        "results": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload


def main() -> int:
    payload = evaluate_all()
    s = payload["summary"]
    print(f"[G2] Evaluated {s['n_trajectories']} trajectories\n")
    print("Discovery class distribution by category:")
    for cat, counts in s["class_distribution_by_category"].items():
        print(f"  {cat}:")
        for cls, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {cls:<40} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
