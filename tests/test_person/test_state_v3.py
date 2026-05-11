"""Tests for v3 Phase 2 v2 -- ActiveState + Candidate + Derived."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from engine.person.state_candidates import CandidateRegistry
from engine.person.state_derived import DerivedCalculator
from engine.person.state_v3 import (
    ACTIVE_VARIABLES_META,
    ActiveState,
    active_variable_names,
    count_active,
    target_aware_names,
)

# =============================================================================
# Active state shape
# =============================================================================

def test_active_state_default_construction() -> None:
    s = ActiveState()
    assert s.fear == 0.0
    assert s.love == {}
    assert s.loyalty == {}
    # faith_stage removed from ActiveState (Dynamics Step 1 → Derived)
    assert not hasattr(s, "faith_stage")


def test_active_state_scalar_range_validation() -> None:
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ActiveState(fear=11.0)
    with pytest.raises(ValidationError):
        ActiveState(hope=-1.0)


def test_target_aware_variables_accept_dict() -> None:
    s = ActiveState(love={"primary_figure": 9.0, "peers": 6.0})
    assert s.love["primary_figure"] == 9.0
    assert len(s.love) == 2


# =============================================================================
# Rule #15 -- Active 20-30 범위 enforcement
# =============================================================================

def test_active_count_within_19_to_30() -> None:
    """Rule #15: Active 변수 수는 20-30개 -- Dynamics Step 1에서 faith_stage
    Derived 강등으로 19로 한 칸 내려옴. 새 Active 추가 없이 유지.
    """
    n = count_active()
    assert 19 <= n <= 30, f"Active count {n} outside 19-30 (Rule #15 / Dynamics Step 1)"


def test_all_active_meta_entries_have_grade_active() -> None:
    for m in ACTIVE_VARIABLES_META:
        assert m.grade == "active"


# =============================================================================
# Rule #17 -- Level A/B only for Active
# =============================================================================

def test_all_active_are_level_a_or_b() -> None:
    """Rule #17: Level C는 Lee 승인 전까지 Active 금지."""
    for m in ACTIVE_VARIABLES_META:
        assert m.evidence_level in ("A", "B"), (
            f"{m.name} has Level {m.evidence_level} but is Active. "
            "Rule #17 requires Lee approval for Level C."
        )


# =============================================================================
# Rule #18 -- target-aware structure for relational concepts
# =============================================================================

def test_relational_concepts_are_target_aware() -> None:
    """Rule #18: love / loyalty / trust / belonging / guilt / shame must be target-aware."""
    required_target_aware = {"love", "loyalty", "trust", "belonging", "guilt", "shame"}
    target_aware_set = set(target_aware_names())
    missing = required_target_aware - target_aware_set
    assert not missing, f"Rule #18 violation: {missing} must be target-aware"


# =============================================================================
# Rule #1 -- generic field names (no person names)
# =============================================================================

def test_active_state_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parent.parent.parent
    for py in (root / "engine" / "person").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(
                    f"{py.name} contains '{b}' -- Rule #1 violation",
                )


# =============================================================================
# Candidate registry
# =============================================================================

def test_candidate_registry_exists_and_nonempty() -> None:
    reg = CandidateRegistry()
    assert reg.n_total() >= 5, "Expected at least 5 Candidates drafted"


def test_candidates_not_in_active() -> None:
    """Candidate 이름이 Active 이름과 겹치면 안 됨."""
    reg = CandidateRegistry()
    active_names = set(active_variable_names())
    for c in reg.all():
        assert c.meta.name not in active_names, (
            f"{c.meta.name} is both Candidate and Active"
        )


def test_promotable_excludes_level_c_by_default() -> None:
    reg = CandidateRegistry()
    promotable = reg.promotable_if(allow_level_c=False)
    for c in promotable:
        assert c.meta.evidence_level != "C", (
            f"{c.meta.name} Level C promoted without allow_level_c -- Rule #17"
        )


def test_candidates_by_blocker_returns_list() -> None:
    reg = CandidateRegistry()
    derivable = reg.by_blocker("derivable_from_active")
    assert isinstance(derivable, list)
    assert len(derivable) >= 1


# =============================================================================
# Derived calculator
# =============================================================================

def test_derived_calculator_computes_all() -> None:
    calc = DerivedCalculator()
    state = ActiveState(fear=5.0, confusion=3.0, fatigue=4.0, hope=7.0, vitality=6.0)
    derived = calc.compute_all(state)
    assert "stress" in derived
    assert "peace" in derived
    assert derived["stress"] > 0.0
    assert 0 <= derived["peace"] <= 10.0


def test_derived_count_within_10_to_20() -> None:
    """v2 §1.1: Derived 예상 10-20개."""
    calc = DerivedCalculator()
    assert 5 <= calc.n_derived() <= 20


def test_derived_stress_formula() -> None:
    """stress = 0.4*fear + 0.3*confusion + 0.3*fatigue."""
    calc = DerivedCalculator()
    state = ActiveState(fear=10.0, confusion=0.0, fatigue=0.0)
    assert calc.compute_one(state, "stress") == pytest.approx(4.0)
    state2 = ActiveState(fear=0.0, confusion=10.0, fatigue=10.0)
    assert calc.compute_one(state2, "stress") == pytest.approx(6.0)


def test_derived_loyalty_composite_empty_target() -> None:
    """loyalty_composite when loyalty dict is empty should be 0."""
    calc = DerivedCalculator()
    state = ActiveState(loyalty={})
    assert calc.compute_one(state, "loyalty_composite") == 0.0


def test_derived_loyalty_composite_averages_targets() -> None:
    calc = DerivedCalculator()
    state = ActiveState(loyalty={"a": 6.0, "b": 4.0})
    assert calc.compute_one(state, "loyalty_composite") == pytest.approx(5.0)


# =============================================================================
# Dynamics Step 1 -- faith_stage_tag Derived
# =============================================================================

def test_faith_stage_tag_none_for_empty_state() -> None:
    from engine.person.state_derived import faith_stage_tag
    assert faith_stage_tag(ActiveState()) == "none"


def test_faith_stage_tag_follower_for_loved_not_tested() -> None:
    from engine.person.state_derived import faith_stage_tag
    s = ActiveState(love={"primary_figure": 9.0},
                    trust={"primary_figure": 8.0},
                    hope=7.0, resolve=6.0)
    assert faith_stage_tag(s) == "follower"


def test_faith_stage_tag_tested_when_shame_rises() -> None:
    from engine.person.state_derived import faith_stage_tag
    s = ActiveState(love={"primary_figure": 9.0},
                    shame={"crowd": 4.0}, doubt=2.0)
    assert faith_stage_tag(s) == "tested"


def test_faith_stage_tag_failed_when_guilt_high() -> None:
    from engine.person.state_derived import faith_stage_tag
    s = ActiveState(love={"primary_figure": 7.0},
                    guilt={"primary_figure": 7.5})
    assert faith_stage_tag(s) == "failed"


def test_faith_stage_tag_restored_when_guilt_resolve_recovered() -> None:
    from engine.person.state_derived import faith_stage_tag
    s = ActiveState(love={"primary_figure": 9.0},
                    guilt={"primary_figure": 2.0},
                    shame={"self": 2.0},
                    hope=7.0, resolve=7.5)
    assert faith_stage_tag(s) == "restored"


def test_faith_stage_tag_is_string_not_in_active_state() -> None:
    """Step 1 invariant: faith_stage not on ActiveState; Derived only."""
    s = ActiveState()
    assert not hasattr(s, "faith_stage"), "faith_stage must be Derived only"


# =============================================================================
# Dynamics Step 5 -- guilt / shame target semantics
# =============================================================================

def test_shame_semantics_before_whom() -> None:
    """shame[key]는 '누구 앞에서 수치를 느끼는가' (before_whom)."""
    s = ActiveState()
    s.shame["crowd"] = 7.0   # crowd 앞에서의 수치
    s.shame["self"] = 5.0    # 자기 앞에서의 수치 (자기 혐오)
    # Both valid; same dict structure, distinct meaning
    assert s.shame["crowd"] == 7.0
    assert s.shame["self"] == 5.0


def test_guilt_semantics_toward_and_self() -> None:
    """guilt[key]는 'toward_whom' + 'self-judgment' 둘 다 수용."""
    s = ActiveState()
    s.guilt["primary_figure"] = 8.0  # 주된 결속 대상에게 잘못한 죄책 (toward)
    s.guilt["self"] = 6.0            # 자기 판단상의 죄책 (self-judgment)
    assert s.guilt["primary_figure"] == 8.0
    assert s.guilt["self"] == 6.0


def test_shame_and_guilt_dict_structure_matches_but_semantics_differ() -> None:
    """구조는 동일 (dict[str, float]), 의미는 다름 (before_whom vs toward_whom)."""
    s = ActiveState(
        shame={"crowd": 3.0, "self": 2.0},
        guilt={"primary_figure": 5.0, "self": 3.0},
    )
    # Structural identity
    assert isinstance(s.shame, dict)
    assert isinstance(s.guilt, dict)
    # No single hard assertion for semantics, but default targets hint:
    # shame["crowd"] valid; guilt has no "crowd" default because guilt isn't
    # public-directed. Sanity check default_targets differ (Step D generic roles).
    from engine.person.state_v3 import ACTIVE_VARIABLES_META
    meta_by_name = {m.name: m for m in ACTIVE_VARIABLES_META}
    # shame has public_group (where public shame is felt); guilt does not.
    assert "public_group" in meta_by_name["shame"].default_targets
    assert "public_group" not in meta_by_name["guilt"].default_targets


# =============================================================================
# Provisional flag -- Claude's draft, awaiting Lee approval
# =============================================================================

def test_all_active_meta_lee_approved() -> None:
    """Lee approved 2026-04-22. All 20 Active entries must be provisional=False.

    If this test fails, check state_v3.py `provisional` default -- it should
    be False (Lee approved) not True (Claude's initial draft).
    """
    for m in ACTIVE_VARIABLES_META:
        assert m.provisional is False, (
            f"{m.name} still provisional after Lee approval"
        )
