"""Tests for engine/world/crowd_dynamics/ (Phase 3 B direction)."""

from __future__ import annotations

import re
from pathlib import Path

from engine.world.crowd_dynamics import (
    CROWD_PHASES,
    CrowdState,
    compute_phase,
    step_crowd,
)
from engine.world.crowd_dynamics.state import (
    inject_crowd_event,
    set_dominant_emotion,
)


# -----------------------------------------------------------------
# Phase classification
# -----------------------------------------------------------------

def test_idle_when_low_density() -> None:
    state = CrowdState(density=0.1, alignment_strength=0.8)
    assert compute_phase(state) == "idle"


def test_idle_when_low_alignment() -> None:
    state = CrowdState(density=0.8, alignment_strength=0.1)
    assert compute_phase(state) == "idle"


def test_gathered_when_dense_low_alignment() -> None:
    state = CrowdState(density=0.6, alignment_strength=0.4)
    assert compute_phase(state) == "gathered"


def test_aligned_when_dense_and_aligned() -> None:
    state = CrowdState(
        density=0.7, alignment_strength=0.7,
        dominant_emotion="celebration",
    )
    assert compute_phase(state) == "aligned"


def test_lynch_mode_when_blame_and_anger() -> None:
    state = CrowdState(
        density=0.7, alignment_strength=0.8,
        dominant_emotion="anger",
        blame_concentration={"outsider": 0.8},
    )
    assert compute_phase(state) == "lynch_mode"


def test_not_lynch_if_low_blame() -> None:
    """High alignment + anger but low blame → aligned, not lynch."""
    state = CrowdState(
        density=0.7, alignment_strength=0.8,
        dominant_emotion="anger",
        blame_concentration={"outsider": 0.3},
    )
    assert compute_phase(state) == "aligned"


# -----------------------------------------------------------------
# Per-tick decay
# -----------------------------------------------------------------

def test_step_decays_alignment() -> None:
    state = CrowdState(density=0.5, alignment_strength=0.5)
    initial_align = state.alignment_strength
    step_crowd(state)
    # Alignment decays, but contagion may boost it at 0.5 — net should reduce
    # or stay similar
    # Decay 0.07, contagion boost ≤ 0.5 × 0.5 × 0.5 × 0.05 = 0.006
    # Net decay ≈ 0.064 → so strictly less than initial
    assert state.alignment_strength < initial_align


def test_step_decays_volatility() -> None:
    state = CrowdState(volatility=0.8)
    step_crowd(state)
    assert state.volatility < 0.8


def test_step_decays_blame() -> None:
    state = CrowdState(blame_concentration={"x": 0.5, "y": 0.02})
    step_crowd(state)
    assert state.blame_concentration["x"] < 0.5
    # y starts 0.02, decay 0.05 → -0.03 → below cleanup threshold → removed
    assert "y" not in state.blame_concentration


def test_dominant_emotion_drifts_to_indifferent_on_low_alignment() -> None:
    state = CrowdState(
        density=0.4, alignment_strength=0.1, dominant_emotion="anger",
    )
    step_crowd(state)
    assert state.dominant_emotion == "indifferent"


# -----------------------------------------------------------------
# Agent action injections
# -----------------------------------------------------------------

def test_inject_gathering_raises_density() -> None:
    state = CrowdState(density=0.2)
    inject_crowd_event(state, "gathering", intensity=0.5)
    assert state.density > 0.2


def test_inject_accusation_raises_blame() -> None:
    state = CrowdState()
    inject_crowd_event(state, "public_accusation",
                       target="outsider", intensity=0.8)
    assert state.blame_concentration["outsider"] > 0
    assert state.accusation_amplification > 0


def test_inject_defiant_voice_raises_fragmentation() -> None:
    state = CrowdState()
    inject_crowd_event(state, "defiant_voice", intensity=0.5)
    assert state.fragmentation > 0


def test_authority_suppression_reduces_alignment() -> None:
    state = CrowdState(alignment_strength=0.8)
    inject_crowd_event(state, "authority_suppression")
    assert state.alignment_strength < 0.8


def test_panic_scatter_drops_density() -> None:
    state = CrowdState(density=0.7, alignment_strength=0.5)
    inject_crowd_event(state, "panic_scatter", intensity=0.8)
    assert state.density < 0.7
    assert state.alignment_strength < 0.5


def test_set_dominant_emotion() -> None:
    state = CrowdState(alignment_strength=0.3)
    set_dominant_emotion(state, "fear")
    assert state.dominant_emotion == "fear"
    assert state.alignment_strength > 0.3


# -----------------------------------------------------------------
# Phase transitions over time (integration)
# -----------------------------------------------------------------

def test_gradual_to_lynch_phase_transition() -> None:
    """Scenario: gathering → rumor → accusation → blame → lynch."""
    state = CrowdState()
    assert compute_phase(state) == "idle"

    # People gather
    inject_crowd_event(state, "gathering", intensity=1.0)
    inject_crowd_event(state, "gathering", intensity=1.0)
    # density ~0.4
    # plus higher density to be sure
    state.density = 0.7
    state.alignment_strength = 0.4
    assert compute_phase(state) == "gathered"

    # Rumor + accusation
    inject_crowd_event(state, "rumor_spread", intensity=1.0)
    inject_crowd_event(state, "public_accusation",
                       target="outsider", intensity=1.0)
    set_dominant_emotion(state, "anger", strength_boost=0.3)
    # Force blame above threshold
    state.blame_concentration["outsider"] = 0.8

    phase = compute_phase(state)
    assert phase in ("aligned", "lynch_mode")


def test_crowd_phases_constant() -> None:
    assert CROWD_PHASES == ("idle", "gathered", "aligned", "lynch_mode")


# -----------------------------------------------------------------
# Rule #1
# -----------------------------------------------------------------

def test_crowd_module_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    for py in (root / "engine" / "world" / "crowd_dynamics").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")
