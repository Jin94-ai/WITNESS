"""Tests for role_cluster + generator + history_tags (Steps H + K)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from engine.population import (
    HISTORY_TAG_DELTAS,
    ROLE_CLUSTERS,
    AgentConfig,
    RoleCluster,
    apply_recent_history,
    generate_population,
    get_role_cluster,
    instantiate_agent,
)
from engine.population.role_cluster import RelationTemplate

# -----------------------------------------------------------------
# RoleCluster registry
# -----------------------------------------------------------------

def test_ten_role_clusters_defined() -> None:
    """Lee §H requirement: 6+ role clusters. We have 10."""
    assert len(ROLE_CLUSTERS) == 10


def test_each_cluster_has_profile_prior_and_relation_template() -> None:
    for role_id, cluster in ROLE_CLUSTERS.items():
        assert isinstance(cluster, RoleCluster), role_id
        assert cluster.profile_prior, f"{role_id} missing profile_prior"
        assert isinstance(cluster.relation_template, RelationTemplate), role_id


def test_get_role_cluster_known() -> None:
    c = get_role_cluster("fisher_laborer")
    assert c.role_id == "fisher_laborer"
    assert "peer_group" in c.relation_template.required


def test_get_role_cluster_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_role_cluster("nonexistent_role")


# -----------------------------------------------------------------
# Rule #1: generic names only
# -----------------------------------------------------------------

def test_role_clusters_no_person_hardcoding() -> None:
    """Rule #1: role cluster file must not contain proper names."""
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate",
              "disciples", "jerusalem"]
    root = Path(__file__).resolve().parents[2]
    src = (root / "engine" / "population" / "role_cluster.py").read_text(
        encoding="utf-8"
    ).lower()
    for b in banned:
        if re.search(rf"\b{b}\b", src):
            raise AssertionError(f"role_cluster.py contains '{b}' -- Rule #1")


# -----------------------------------------------------------------
# History tags
# -----------------------------------------------------------------

def test_history_tags_positive_raises_hope() -> None:
    state = {"hope": 5.0, "awe": 3.0, "grief": 0.0}
    out = apply_recent_history(state, "witnessed miracle last week")
    assert out["hope"] > 5.0
    assert out["awe"] > 3.0


def test_history_tags_loss_raises_grief() -> None:
    state = {"grief": 0.0, "fatigue": 2.0, "fear": 1.0}
    out = apply_recent_history(state, "bereavement in the family")
    assert out["grief"] > 0.0


def test_history_tags_clip_to_10() -> None:
    state = {"awe": 9.0, "hope": 9.0}
    out = apply_recent_history(state, "witnessed miracle and another miracle")
    assert 0.0 <= out["awe"] <= 10.0
    assert 0.0 <= out["hope"] <= 10.0


def test_empty_history_no_change() -> None:
    state = {"hope": 5.0, "fear": 2.0}
    out = apply_recent_history(state, "")
    assert out == {"hope": 5.0, "fear": 2.0}


def test_history_tag_registry_nonempty() -> None:
    assert len(HISTORY_TAG_DELTAS) > 10


# -----------------------------------------------------------------
# Agent instantiation
# -----------------------------------------------------------------

def test_instantiate_simple_agent() -> None:
    config = AgentConfig(
        agent_id="test_fisher_01",
        role_cluster="fisher_laborer",
        relation_seeds={
            "peer_group": ["peer_a", "peer_b"],
            "family": "fisher_family_01",
        },
        seed=42,
    )
    agent = instantiate_agent(config)
    assert agent.agent_id == "test_fisher_01"
    assert agent.role_id == "fisher_laborer"
    assert agent.profile.name == "test_fisher_01"
    assert agent.relations["peer_group"] == ["peer_a", "peer_b"]
    # fisher_laborer prior applied
    assert agent.profile.relation_bias.peer_dependence > 1.0


def test_instantiate_requires_required_relations() -> None:
    config = AgentConfig(
        agent_id="bad_fisher",
        role_cluster="fisher_laborer",
        relation_seeds={},  # missing required peer_group and family
        seed=1,
    )
    with pytest.raises(ValueError, match="requires relation"):
        instantiate_agent(config)


def test_instantiate_applies_profile_overrides() -> None:
    config = AgentConfig(
        agent_id="tough_fisher",
        role_cluster="fisher_laborer",
        profile_overrides={
            "motif_tendency": {"confront": 1.8},
        },
        relation_seeds={"peer_group": ["p1"], "family": "f1"},
        seed=7,
    )
    agent = instantiate_agent(config)
    # Overridden value should be reflected (within perturbation window)
    assert agent.profile.motif_tendency.confront > 1.4


def test_instantiate_applies_recent_history() -> None:
    config = AgentConfig(
        agent_id="shaken_fisher",
        role_cluster="fisher_laborer",
        relation_seeds={"peer_group": ["p1"], "family": "f1"},
        recent_history="brother arrested by Romans last month",
        seed=10,
    )
    agent = instantiate_agent(config)
    # brother arrested → anger + grief + fear rise
    assert agent.initial_state["anger"] > 2.0
    assert agent.initial_state["fear"] > 2.0


def test_instantiate_dict_config_works() -> None:
    """Dict config should also work."""
    agent = instantiate_agent({
        "agent_id": "dict_agent",
        "role_cluster": "fisher_laborer",
        "relation_seeds": {"peer_group": ["a"], "family": "fam"},
        "seed": 0,
    })
    assert agent.agent_id == "dict_agent"


# -----------------------------------------------------------------
# Three-agent example (Lee §15 completion criterion)
# -----------------------------------------------------------------

def test_three_named_agents_no_handcraft() -> None:
    """Lee §15 completion: handcraft 없이 임의 agent 3명 초기화 가능."""

    # Agent 1: Galilean fisher
    jonah = instantiate_agent(AgentConfig(
        agent_id="jonah_bar_simon",
        role_cluster="fisher_laborer",
        profile_overrides={"motif_tendency": {"observe_wait": 1.1}},
        relation_seeds={
            "peer_group": ["peer_01", "peer_02"],
            "family": "jonah_family",
        },
        initial_state_seed={"fatigue": 6.0, "hope": 5.0},
        recent_history="good catch yesterday",
        faction_affiliation={"in_group": "galilean_fishers"},
        seed=100,
    ))

    # Agent 2: merchant
    eliezer = instantiate_agent(AgentConfig(
        agent_id="eliezer_merchant",
        role_cluster="merchant",
        relation_seeds={
            "peer_group": ["competitor_1"],
            "public_group": "marketplace_patrons",
            "family": "eliezer_family",
        },
        initial_state_seed={"doubt": 3.0, "resolve": 6.0},
        recent_history="tax increase notice received",
        seed=101,
    ))

    # Agent 3: crowd participant
    zealot = instantiate_agent(AgentConfig(
        agent_id="zealot_bystander_47",
        role_cluster="crowd_participant",
        profile_overrides={
            "motif_tendency": {"confront": 1.4, "observe_wait": 0.6}
        },
        relation_seeds={},  # crowd_participant has no required relations
        initial_state_seed={"anger": 5.0, "hope": 4.0},
        recent_history="brother arrested by Romans 6 months ago",
        faction_affiliation={"in_group": "sympathizers_group"},
        seed=102,
    ))

    # All three instantiated without errors
    assert jonah.role_id == "fisher_laborer"
    assert eliezer.role_id == "merchant"
    assert zealot.role_id == "crowd_participant"

    # All three have valid profile
    for agent in (jonah, eliezer, zealot):
        assert agent.profile.validate() == [], (
            f"{agent.agent_id} profile invalid"
        )


# -----------------------------------------------------------------
# Bulk generation
# -----------------------------------------------------------------

def test_generate_population_basic() -> None:
    distribution = {
        "fisher_laborer": 0.5,
        "family_anchor": 0.3,
        "crowd_participant": 0.2,
    }
    pop = generate_population(distribution, total_agents=20, seed_base=0)
    assert len(pop) >= 15  # rough: rounding may vary
    role_counts = {}
    for agent in pop:
        role_counts[agent.role_id] = role_counts.get(agent.role_id, 0) + 1
    assert "fisher_laborer" in role_counts
    assert "family_anchor" in role_counts
    assert "crowd_participant" in role_counts


def test_generate_population_deterministic_with_seed() -> None:
    d = {"fisher_laborer": 1.0}
    p1 = generate_population(d, total_agents=5, seed_base=42)
    p2 = generate_population(d, total_agents=5, seed_base=42)
    # Same seed → same profile values (motif_tendency.confront, for instance)
    for a1, a2 in zip(p1, p2):
        assert a1.profile.motif_tendency.confront == pytest.approx(
            a2.profile.motif_tendency.confront
        )
