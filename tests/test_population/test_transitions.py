"""Role transition tests (B direction Batch 6)."""

from __future__ import annotations

import random

import pytest

from engine.persona.profile import DEFAULT_PROFILE
from engine.population import (
    apply_role_transition,
    blend_profile_toward_role,
    instantiate_agent,
)
from engine.population.generator import AgentConfig


def _sample_fisher() -> "object":
    """Build a fisher_laborer agent with default perturbation."""
    cfg = AgentConfig(
        agent_id="agent_fisher_test",
        role_cluster="fisher_laborer",
        relation_seeds={"peer_group": "peers_a", "family": "kin_a"},
        seed=7,
    )
    return instantiate_agent(cfg)


# -----------------------------------------------------------------
# blend_profile_toward_role
# -----------------------------------------------------------------


def test_blend_factor_zero_returns_equivalent_profile():
    fisher = _sample_fisher()
    blended = blend_profile_toward_role(
        fisher.profile, "disciple_follower", blend_factor=0.0,
    )
    # Every numeric field should equal original (modulo baseline-drift 0)
    for attr in fisher.profile.pressure_sensitivity.__dict__:
        orig = getattr(fisher.profile.pressure_sensitivity, attr)
        new = getattr(blended.pressure_sensitivity, attr)
        assert new == pytest.approx(orig, abs=1e-9)


def test_blend_factor_one_moves_toward_target_role():
    fisher = _sample_fisher()
    blended = blend_profile_toward_role(
        fisher.profile, "disciple_follower", blend_factor=1.0,
    )
    # disciple_follower has motif_tendency.seek_repair = 1.2
    assert blended.motif_tendency.seek_repair == pytest.approx(1.2, abs=0.01)
    # disciple_follower has pressure_sensitivity.sacred_salience = 1.4
    assert blended.pressure_sensitivity.sacred_salience == pytest.approx(
        1.4, abs=0.01,
    )


def test_blend_middle_interpolates():
    fisher = _sample_fisher()
    orig_sacred = fisher.profile.pressure_sensitivity.sacred_salience
    blended = blend_profile_toward_role(
        fisher.profile, "disciple_follower", blend_factor=0.5,
    )
    new_sacred = blended.pressure_sensitivity.sacred_salience
    # Should be between orig and 1.4
    assert min(orig_sacred, 1.4) <= new_sacred <= max(orig_sacred, 1.4)


def test_blend_clamps_to_range():
    fisher = _sample_fisher()
    blended = blend_profile_toward_role(
        fisher.profile, "authority_priest", blend_factor=1.0,
        rng=random.Random(0),
    )
    for obj in (
        blended.pressure_sensitivity,
        blended.motif_tendency,
        blended.recovery_bias,
        blended.relation_bias,
    ):
        for v in obj.__dict__.values():
            assert 0.0 <= v <= 2.0


def test_blend_uses_target_role_priors_when_set():
    """Iter 7/11 semantics: if target role has motif_action_priors,
    those override the current profile's priors. This is the root
    mechanism for behavioral divergence after role transition."""
    fisher = _sample_fisher()
    fisher.profile.motif_action_priors["conceal"] = {
        "deny": 0.7, "withdraw_in_fear": 0.3,
    }
    blended = blend_profile_toward_role(
        fisher.profile, "disciple_follower", blend_factor=0.7,
    )
    # disciple_follower has motif_action_priors populated in Iter 11,
    # so blended priors should reflect the target role, not input.
    from engine.population import ROLE_CLUSTERS
    expected_conceal = ROLE_CLUSTERS["disciple_follower"].motif_action_priors["conceal"]
    assert blended.motif_action_priors["conceal"] == expected_conceal


def test_blend_rejects_out_of_range_factor():
    fisher = _sample_fisher()
    with pytest.raises(ValueError):
        blend_profile_toward_role(
            fisher.profile, "disciple_follower", blend_factor=-0.1,
        )
    with pytest.raises(ValueError):
        blend_profile_toward_role(
            fisher.profile, "disciple_follower", blend_factor=1.1,
        )


# -----------------------------------------------------------------
# apply_role_transition
# -----------------------------------------------------------------


def test_apply_transition_returns_record():
    fisher = _sample_fisher()
    result = apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="disciple_follower",
        tick=7,
        reason="miracle_witness",
    )
    assert result.record.tick == 7
    assert result.record.from_role == "fisher_laborer"
    assert result.record.to_role == "disciple_follower"
    assert result.record.reason == "miracle_witness"


def test_apply_transition_updates_affordances():
    fisher = _sample_fisher()
    result = apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="disciple_follower",
        tick=5,
    )
    # disciple_follower pack includes "pray" and "confess"
    assert "pray" in result.new_affordance_pack
    assert "confess" in result.new_affordance_pack


def test_apply_transition_rejects_same_role():
    fisher = _sample_fisher()
    with pytest.raises(ValueError, match="same as current"):
        apply_role_transition(
            current_profile=fisher.profile,
            current_role_id="fisher_laborer",
            new_role_id="fisher_laborer",
            tick=0,
        )


def test_apply_transition_updates_info_access():
    fisher = _sample_fisher()
    assert fisher.info_access_level == "peer_network_medium"
    result = apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="elite_strategist",
        tick=3,
        reason="covert_bargain",
    )
    assert result.new_info_access_level == "cross_network_high"


def test_full_transition_shifts_dominant_motif_bias():
    fisher = _sample_fisher()
    # fisher_laborer motif_tendency: remain_present=1.2, confront=1.1
    # disciple_follower: remain_present=1.1, seek_repair=1.2
    result = apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="disciple_follower",
        tick=10,
        blend_factor=1.0,
    )
    # After full blend, seek_repair should dominate over confront
    new_mt = result.new_profile.motif_tendency
    assert new_mt.seek_repair > new_mt.confront


def test_transition_description_includes_history():
    fisher = _sample_fisher()
    result = apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="disciple_follower",
        tick=12,
        blend_factor=0.5,
    )
    assert "transitioned" in result.new_profile.description
    assert "disciple_follower" in result.new_profile.description


def test_transition_with_perturbation_stays_in_range():
    fisher = _sample_fisher()
    rng = random.Random(123)
    for _ in range(20):
        result = apply_role_transition(
            current_profile=fisher.profile,
            current_role_id="fisher_laborer",
            new_role_id="soldier_enforcer",
            tick=5,
            blend_factor=0.7,
            rng=rng,
        )
        for obj in (
            result.new_profile.pressure_sensitivity,
            result.new_profile.motif_tendency,
            result.new_profile.recovery_bias,
            result.new_profile.relation_bias,
        ):
            for v in obj.__dict__.values():
                assert 0.0 <= v <= 2.0


def test_nontarget_fields_drift_toward_baseline():
    """Fields not in target role prior should drift toward 1.0 baseline."""
    fisher = _sample_fisher()
    # fisher has peer_dependence=1.3 (from role prior); elite_strategist
    # prior has peer_dependence=0.8
    result = apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="elite_strategist",
        tick=5,
        blend_factor=1.0,
    )
    # elite_strategist specifies peer_dependence=0.8 → blended to 0.8
    assert result.new_profile.relation_bias.peer_dependence == pytest.approx(
        0.8, abs=0.01,
    )


def test_transition_does_not_mutate_input_profile():
    fisher = _sample_fisher()
    original_sacred = fisher.profile.pressure_sensitivity.sacred_salience
    apply_role_transition(
        current_profile=fisher.profile,
        current_role_id="fisher_laborer",
        new_role_id="spiritual_wanderer",
        tick=1,
        blend_factor=1.0,
    )
    # Input should be untouched
    assert (
        fisher.profile.pressure_sensitivity.sacred_salience == original_sacred
    )


def test_role_cluster_no_person_hardcoding():
    """Rule #1 integrity — transition module uses no canonical names."""
    from pathlib import Path

    txt = Path("engine/population/transitions.py").read_text(encoding="utf-8")
    lower = txt.lower()
    for forbidden in ("peter", "judas", "caiaphas", "baptist", "jesus", "vangogh"):
        assert forbidden not in lower, (
            f"transitions.py should not reference '{forbidden}'"
        )
