"""Tests for WorldCritic (Rubric Level 5)."""

from __future__ import annotations

import re
from pathlib import Path

from dataclasses import dataclass, field


@dataclass
class MockWorldStep:
    tick: int
    agent_actions: dict = field(default_factory=dict)
    agent_motifs: dict = field(default_factory=dict)
    crowd_state_snapshot: dict = field(default_factory=dict)
    rumor_snapshot: list = field(default_factory=list)
    spawned_events: list = field(default_factory=list)


from engine.rubric import WorldCritic


# -----------------------------------------------------------------
# Empty / short history
# -----------------------------------------------------------------

def test_empty_history() -> None:
    critic = WorldCritic()
    report = critic.evaluate([])
    assert report.n_ticks == 0
    assert report.total_phase_transitions == 0
    assert not report.is_living_world


def test_short_history_returns_zero_path_dependence() -> None:
    critic = WorldCritic()
    history = [MockWorldStep(tick=i) for i in range(1, 4)]
    report = critic.evaluate(history)
    assert report.path_dependence_evidence == 0.0


# -----------------------------------------------------------------
# Phase transitions
# -----------------------------------------------------------------

def test_no_transitions_when_steady() -> None:
    critic = WorldCritic()
    history = [
        MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "idle", "alignment": 0.1}},
        )
        for i in range(1, 11)
    ]
    report = critic.evaluate(history)
    assert report.total_phase_transitions == 0


def test_single_transition() -> None:
    critic = WorldCritic()
    history = []
    for i in range(1, 6):
        history.append(MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "idle", "alignment": 0.1}},
        ))
    for i in range(6, 11):
        history.append(MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "gathered", "alignment": 0.5}},
        ))
    report = critic.evaluate(history)
    assert report.total_phase_transitions == 1
    assert report.phase_transitions["c1"][0]["tick"] == 6
    assert report.phase_transitions["c1"][0]["from"] == "idle"
    assert report.phase_transitions["c1"][0]["to"] == "gathered"


def test_multi_transition_chain() -> None:
    critic = WorldCritic()
    phases = ["idle"] * 3 + ["gathered"] * 3 + ["aligned"] * 3 + ["lynch_mode"] * 3
    history = [
        MockWorldStep(
            tick=i + 1,
            crowd_state_snapshot={"c1": {"phase": ph, "alignment": 0.7}},
        )
        for i, ph in enumerate(phases)
    ]
    report = critic.evaluate(history)
    assert report.total_phase_transitions == 3  # idle→gathered→aligned→lynch


# -----------------------------------------------------------------
# Cross-layer activations
# -----------------------------------------------------------------

def test_cross_layer_zero_when_no_overlap() -> None:
    critic = WorldCritic()
    history = [
        MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "idle", "alignment": 0.0, "blame": {}}},
            rumor_snapshot=[],
        )
        for i in range(1, 11)
    ]
    report = critic.evaluate(history)
    assert report.cross_layer_activations == 0


def test_cross_layer_counted_when_both_active() -> None:
    critic = WorldCritic()
    history = [
        MockWorldStep(
            tick=i,
            crowd_state_snapshot={
                "c1": {"phase": "gathered", "alignment": 0.5,
                       "blame": {"target": 0.3}},
            },
            rumor_snapshot=[{"id": "r1", "intensity": 0.5}],
        )
        for i in range(1, 6)
    ]
    report = critic.evaluate(history)
    assert report.cross_layer_activations == 5


# -----------------------------------------------------------------
# Story density
# -----------------------------------------------------------------

def test_story_density_calculation() -> None:
    critic = WorldCritic()
    history = []
    for i in range(1, 11):  # 10 ticks
        history.append(MockWorldStep(
            tick=i,
            crowd_state_snapshot={
                "c1": {"phase": ["idle", "gathered"][i % 2], "alignment": 0.5},
            },
        ))
    report = critic.evaluate(history)
    # 9 phase transitions / 10 ticks × 100 = 90
    assert report.story_density == 90.0


# -----------------------------------------------------------------
# World coherence
# -----------------------------------------------------------------

def test_coherence_perfect_when_phase_matches() -> None:
    critic = WorldCritic()
    history = [
        MockWorldStep(
            tick=i,
            crowd_state_snapshot={
                "c1": {"phase": "lynch_mode", "alignment": 0.8},
            },
        )
        for i in range(1, 6)
    ]
    report = critic.evaluate(history)
    assert report.world_coherence == 1.0


def test_coherence_detects_lynch_with_low_alignment() -> None:
    """Contradiction: phase = lynch_mode but alignment < 0.6."""
    critic = WorldCritic()
    history = [
        MockWorldStep(
            tick=i,
            crowd_state_snapshot={
                "c1": {"phase": "lynch_mode", "alignment": 0.3},
            },
        )
        for i in range(1, 6)
    ]
    report = critic.evaluate(history)
    assert report.world_coherence < 1.0


# -----------------------------------------------------------------
# Path dependence
# -----------------------------------------------------------------

def test_path_dependence_zero_when_constant() -> None:
    critic = WorldCritic()
    history = [
        MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "idle", "alignment": 0.1}},
        )
        for i in range(1, 10)
    ]
    report = critic.evaluate(history)
    assert report.path_dependence_evidence == 0.0


def test_path_dependence_nonzero_when_diverges() -> None:
    critic = WorldCritic()
    history = []
    # Early: idle
    for i in range(1, 6):
        history.append(MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "idle", "alignment": 0.1}},
        ))
    # Mid: gathered
    for i in range(6, 11):
        history.append(MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "gathered", "alignment": 0.5}},
        ))
    # Late: lynch_mode
    for i in range(11, 16):
        history.append(MockWorldStep(
            tick=i,
            crowd_state_snapshot={"c1": {"phase": "lynch_mode", "alignment": 0.9}},
        ))
    report = critic.evaluate(history)
    assert report.path_dependence_evidence > 0.0


# -----------------------------------------------------------------
# is_living_world heuristic
# -----------------------------------------------------------------

def test_is_living_world_requires_all_three() -> None:
    critic = WorldCritic()
    history = []
    phases = ["idle"] * 5 + ["gathered"] * 5 + ["aligned"] * 5
    for i, ph in enumerate(phases):
        history.append(MockWorldStep(
            tick=i + 1,
            crowd_state_snapshot={
                "c1": {"phase": ph, "alignment": 0.7,
                       "blame": {"target": 0.3}},
            },
            rumor_snapshot=[{"id": "r1", "intensity": 0.5}],
        ))
    report = critic.evaluate(history)
    # 2 phase transitions × 100 / 15 ticks = 13.3 story_density
    # cross_layer_activations = 15 (all ticks have both crowd+rumor)
    assert report.is_living_world


# -----------------------------------------------------------------
# Rule #1
# -----------------------------------------------------------------

def test_world_critic_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    src = (root / "engine" / "rubric" / "world_critic.py").read_text(
        encoding="utf-8"
    ).lower()
    for b in banned:
        if re.search(rf"\b{b}\b", src):
            raise AssertionError(f"world_critic.py contains '{b}' -- Rule #1")
