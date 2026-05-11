"""Tests for PopulationCritic (Rubric Level 4, B direction Phase 7)."""

from __future__ import annotations

import re
from pathlib import Path

from engine.rubric import PopulationCritic


def test_empty_trajectories_zero_diversity() -> None:
    critic = PopulationCritic()
    report = critic.evaluate({}, {}, [])
    assert report.n_agents == 0
    assert report.motif_diversity_index == 0.0


def test_uniform_motif_single_bucket() -> None:
    """All agents always use same motif → low diversity."""
    critic = PopulationCritic()
    trajectories = {
        f"a{i}": [{"selected_motif": "remain_present"} for _ in range(10)]
        for i in range(5)
    }
    roles = {f"a{i}": "fisher_laborer" for i in range(5)}
    report = critic.evaluate(trajectories, roles, [])
    assert report.motif_diversity_index == 0.0  # 1 bucket


def test_high_motif_diversity() -> None:
    """Different motifs evenly distributed → high diversity."""
    critic = PopulationCritic()
    motifs = ["remain_present", "conceal", "withdraw", "grieve", "confess"]
    trajectories = {
        f"a{i}": [{"selected_motif": motifs[i % 5]} for _ in range(10)]
        for i in range(10)
    }
    roles = {f"a{i}": "fisher_laborer" for i in range(10)}
    report = critic.evaluate(trajectories, roles, [])
    assert report.motif_diversity_index > 0.9  # near max entropy


def test_role_archetype_distinctness_high() -> None:
    """Same role agents with different motif distributions → high distinctness."""
    critic = PopulationCritic()
    trajectories = {
        "a1": [{"selected_motif": "conceal"}] * 10,   # role X, mostly conceal
        "a2": [{"selected_motif": "confront"}] * 10,  # role X, mostly confront
        "a3": [{"selected_motif": "withdraw"}] * 10,  # role X, mostly withdraw
    }
    roles = {"a1": "fisher_laborer", "a2": "fisher_laborer",
             "a3": "fisher_laborer"}
    report = critic.evaluate(trajectories, roles, [])
    assert report.role_archetype_distinctness > 0.5


def test_role_archetype_distinctness_low_when_uniform() -> None:
    critic = PopulationCritic()
    trajectories = {
        f"a{i}": [{"selected_motif": "remain_present"}] * 10 for i in range(4)
    }
    roles = {f"a{i}": "fisher_laborer" for i in range(4)}
    report = critic.evaluate(trajectories, roles, [])
    assert report.role_archetype_distinctness < 0.1


def test_emergent_fraction() -> None:
    critic = PopulationCritic()
    event_log = [
        {"tick": 1, "event_id": "seed_x", "by": None},
        {"tick": 2, "event_id": "seed_y", "by": None},
        {"tick": 3, "event_id": "public_denial", "by": "a1"},
        {"tick": 4, "event_id": "public_confession", "by": "a2"},
    ]
    report = critic.evaluate({}, {}, event_log)
    assert report.emergent_event_fraction == 0.5


def test_pressure_response_variance() -> None:
    """Different agents, different actions → variance positive."""
    critic = PopulationCritic()
    trajectories = {
        "a1": [{"action_id": "deny"}] * 10,
        "a2": [{"action_id": "confess"}] * 10,
        "a3": [{"action_id": "follow_closely"}] * 10,
    }
    report = critic.evaluate(trajectories, {}, [])
    assert report.pressure_response_variance > 0.8


def test_role_motif_correlation_high_when_role_predictive() -> None:
    """If role strongly predicts motif → correlation high."""
    critic = PopulationCritic()
    trajectories = {
        "p1": [{"selected_motif": "conceal"}] * 10,
        "p2": [{"selected_motif": "conceal"}] * 10,
        "s1": [{"selected_motif": "confront"}] * 10,
        "s2": [{"selected_motif": "confront"}] * 10,
    }
    roles = {"p1": "priest", "p2": "priest", "s1": "soldier", "s2": "soldier"}
    report = critic.evaluate(trajectories, roles, [])
    # Role fully predicts motif → reduction maximal → normalized ~1
    assert report.role_motif_correlation > 0.9


def test_role_motif_correlation_low_when_no_predictive() -> None:
    """If motifs random regardless of role → correlation low."""
    critic = PopulationCritic()
    motifs = ["conceal", "confront", "withdraw", "grieve"]
    trajectories = {
        f"a{i}": [{"selected_motif": motifs[j % 4]} for j in range(8)]
        for i in range(4)
    }
    # All same role
    roles = {f"a{i}": "crowd" for i in range(4)}
    report = critic.evaluate(trajectories, roles, [])
    # Only one role — no predictive reduction possible
    assert report.role_motif_correlation < 0.1


def test_composite_mean() -> None:
    critic = PopulationCritic()
    motifs = ["conceal", "confront", "grieve", "withdraw"]
    trajectories = {
        f"a{i}": [{"selected_motif": motifs[i % 4], "action_id": f"act_{i}"}] * 5
        for i in range(6)
    }
    roles = {f"a{i}": f"role_{i % 2}" for i in range(6)}
    events = [{"tick": 1, "by": "a1"}, {"tick": 2, "by": None}]
    report = critic.evaluate(trajectories, roles, events)
    assert 0 <= report.composite <= 1.0


# -----------------------------------------------------------------
# Rule #1 on new module
# -----------------------------------------------------------------

def test_population_critic_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    src = (root / "engine" / "rubric" / "population_critic.py").read_text(
        encoding="utf-8"
    ).lower()
    for b in banned:
        if re.search(rf"\b{b}\b", src):
            raise AssertionError(f"population_critic.py contains '{b}' -- Rule #1")
