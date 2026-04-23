"""Tests for Phase 4 rubric critics + evaluator."""

from __future__ import annotations

from engine.constraint.hard_constraints import HardConstraintChecker
from engine.constraint.soft_constraints import SoftConstraintScorer
from engine.rubric import (
    CanonCritic,
    CausalCritic,
    CharacterCritic,
    DiscoveryClass,
    NoveltyCritic,
    RubricEvaluator,
)


def test_character_critic_composite_range() -> None:
    c = CharacterCritic()
    report = c.evaluate([{"action_kind": "a", "fear_like": 3}])
    assert 0 <= report.composite <= 1.0


def test_character_critic_impulsivity_high_when_flips() -> None:
    c = CharacterCritic(impulsivity_threshold=0.3)
    records = [
        {"action_kind": "approach"},
        {"action_kind": "retreat"},
        {"action_kind": "approach"},
        {"action_kind": "retreat"},
    ]
    r = c.evaluate(records)
    # 3 flips over 3 windows = rate 1.0 → score = min(1, 1/0.3) = 1.0
    assert r.impulsivity_score == 1.0


def test_canon_critic_no_violation_clean_trajectory() -> None:
    hard = HardConstraintChecker(action_vocabulary={"pray", "follow"})
    soft = SoftConstraintScorer(canonical_sequence=[(1, "pray"), (2, "follow")])
    canon = CanonCritic(hard=hard, soft=soft, reproduction_threshold=2.0)
    records = [
        {"tick": 1, "action_id": "pray"},
        {"tick": 2, "action_id": "follow"},
    ]
    r = canon.evaluate(records)
    assert r.is_canon_valid
    assert r.is_canon_reproducing


def test_canon_critic_hard_violation_detected() -> None:
    hard = HardConstraintChecker(action_vocabulary={"pray"})
    canon = CanonCritic(hard=hard)
    records = [{"tick": 1, "action_id": "tweet"}]
    r = canon.evaluate(records)
    assert not r.is_canon_valid
    assert len(r.hard_violations) == 1


def test_causal_critic_flags_unexplained_jumps() -> None:
    critic = CausalCritic(jump_threshold=3.0, state_fields=["fear"])
    records = [
        {"state": {"fear": 1.0}},
        {"state": {"fear": 1.5}, "event_triggered": False},
        {"state": {"fear": 8.0}, "event_triggered": False},  # jump
        {"state": {"fear": 8.5}, "event_triggered": False},
    ]
    r = critic.evaluate(records)
    assert r.unexplained_jumps >= 1


def test_causal_critic_event_explains_jump() -> None:
    critic = CausalCritic(jump_threshold=3.0, state_fields=["fear"])
    records = [
        {"state": {"fear": 1.0}},
        {"state": {"fear": 9.0}, "event_triggered": True},  # explained
    ]
    r = critic.evaluate(records)
    assert r.unexplained_jumps == 0


def test_novelty_critic_bands() -> None:
    critic = NoveltyCritic(copy_threshold=1.5, noise_threshold=15.0)
    assert critic.evaluate(0.0).novelty_band == "copy"
    assert critic.evaluate(5.0).novelty_band == "meaningful"
    assert critic.evaluate(20.0).novelty_band == "noise"


def test_rubric_evaluator_invalid_on_hard_violation() -> None:
    hard = HardConstraintChecker(action_vocabulary={"pray"})
    soft = SoftConstraintScorer(canonical_sequence=[(1, "pray")])
    evaluator = RubricEvaluator(
        character=CharacterCritic(),
        canon=CanonCritic(hard=hard, soft=soft),
        causal=CausalCritic(),
        novelty=NoveltyCritic(),
    )
    records = [{"tick": 1, "action_id": "unknown_action"}]
    r = evaluator.evaluate(records)
    assert r.discovery_class == DiscoveryClass.INVALID


def test_rubric_evaluator_canonical_reproduction() -> None:
    canon_seq = [(1, "pray"), (2, "follow")]
    hard = HardConstraintChecker(action_vocabulary={"pray", "follow"})
    soft = SoftConstraintScorer(canonical_sequence=canon_seq)
    evaluator = RubricEvaluator(
        character=CharacterCritic(),
        canon=CanonCritic(hard=hard, soft=soft, reproduction_threshold=1.0),
        causal=CausalCritic(),
        novelty=NoveltyCritic(copy_threshold=1.5),
    )
    records = [
        {"tick": 1, "action_id": "pray"},
        {"tick": 2, "action_id": "follow"},
    ]
    r = evaluator.evaluate(records)
    assert r.discovery_class == DiscoveryClass.CANONICAL_REPRODUCTION


def test_rubric_evaluator_not_discovery_when_hardcoded() -> None:
    hard = HardConstraintChecker(action_vocabulary={"pray"})
    soft = SoftConstraintScorer(canonical_sequence=[(1, "pray")])
    evaluator = RubricEvaluator(
        character=CharacterCritic(),
        canon=CanonCritic(hard=hard, soft=soft),
        causal=CausalCritic(),
        novelty=NoveltyCritic(),
    )
    records = [{"tick": 1, "action_id": "pray"}]
    r = evaluator.evaluate(records, is_all_hardcoded=True)
    assert r.discovery_class == DiscoveryClass.NOT_DISCOVERY_HARDCODED


def test_rubric_evaluator_noise_band() -> None:
    canon_seq = [(i, "pray") for i in range(1, 6)]
    hard = HardConstraintChecker(action_vocabulary={"pray", "random_a", "random_b"})
    soft = SoftConstraintScorer(canonical_sequence=canon_seq)
    evaluator = RubricEvaluator(
        character=CharacterCritic(),
        canon=CanonCritic(hard=hard, soft=soft, reproduction_threshold=1.0),
        causal=CausalCritic(),
        novelty=NoveltyCritic(copy_threshold=1.5, noise_threshold=3.0),
    )
    # Massively divergent trajectory
    records = [
        {"tick": i, "action_id": "random_a" if i % 2 == 0 else "random_b"}
        for i in range(1, 11)
    ]
    r = evaluator.evaluate(records)
    # Drift should exceed noise threshold
    assert r.discovery_class == DiscoveryClass.NOT_DISCOVERY_NOISE


def test_rubric_engine_no_person_hardcoding() -> None:
    """Rule #1 on engine/rubric/."""
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    for py in (root / "engine" / "rubric").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")
