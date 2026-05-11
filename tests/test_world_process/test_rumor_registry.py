"""Tests for engine/world/information/rumor_registry.py (Phase 3)."""

from __future__ import annotations

import random
import re
from pathlib import Path

from engine.world.information import Rumor, RumorRegistry


def _small_network() -> dict[str, set[str]]:
    """5-agent star network with a central hub + 2-hop cluster."""
    return {
        "a": {"b", "c"},
        "b": {"a", "d"},
        "c": {"a", "e"},
        "d": {"b"},
        "e": {"c"},
    }


def test_registry_empty_by_default() -> None:
    r = RumorRegistry()
    assert len(r) == 0


def test_spawn_creates_rumor() -> None:
    r = RumorRegistry(_small_network())
    rumor = r.spawn(
        content_tag="accusation",
        target_role="outsider",
        origin_source="a",
        origin_tick=0,
    )
    assert rumor.content_tag == "accusation"
    assert rumor.target_role == "outsider"
    assert "a" in rumor.reach
    assert len(r) == 1


def test_get_about() -> None:
    r = RumorRegistry()
    r.spawn("prophecy", target_role="prophet_X", origin_source="a", origin_tick=0)
    r.spawn("accusation", target_role="outsider", origin_source="b", origin_tick=0)
    about_prophet = r.get_about("prophet_X")
    about_outsider = r.get_about("outsider")
    assert len(about_prophet) == 1
    assert len(about_outsider) == 1


def test_step_propagates() -> None:
    rng = random.Random(42)
    r = RumorRegistry(_small_network())
    rumor = r.spawn(
        content_tag="accusation",
        target_role="outsider",
        origin_source="a",
        origin_tick=0,
        intensity=0.9,
        credibility=0.8,
    )
    initial_reach = set(rumor.reach)
    # Step a few times to allow propagation (stochastic but p_spread high)
    for t in range(1, 8):
        r.step(t, rng=rng)

    # Reach should have grown (high propagation_rate=0.3 × intensity × cred)
    assert len(rumor.reach) > len(initial_reach)


def test_step_decays_intensity() -> None:
    r = RumorRegistry()
    rumor = r.spawn(
        content_tag="secret", origin_source="a", origin_tick=0,
        intensity=0.5,
    )
    initial = rumor.intensity
    r.step(1)
    assert rumor.intensity < initial


def test_cleanup_removes_faded_rumors() -> None:
    r = RumorRegistry(cleanup_threshold=0.1)
    r.spawn(
        content_tag="old", origin_source="a", origin_tick=0,
        intensity=0.15,  # low initial
    )
    # After several decays (0.08/tick), should drop below 0.1
    for t in range(1, 5):
        r.step(t)
    assert len(r) == 0


def test_distortion_accumulates_on_propagation() -> None:
    rng = random.Random(0)
    r = RumorRegistry(_small_network())
    rumor = r.spawn(
        content_tag="accusation",
        origin_source="a",
        origin_tick=0,
        intensity=1.0,
        credibility=1.0,
    )
    initial_distortion = rumor.distortion

    # High propagation likelihood → distortion should grow
    for t in range(1, 6):
        r.step(t, rng=rng)

    assert rumor.distortion >= initial_distortion
    # With full network spread, distortion should be > 0
    if len(rumor.reach) > 1:
        assert rumor.distortion > 0


def test_authority_suppression_reduces_spread() -> None:
    rng_a = random.Random(0)
    rng_b = random.Random(0)

    # Without suppression
    r_free = RumorRegistry(_small_network())
    rumor_free = r_free.spawn(
        "accusation", origin_source="a", origin_tick=0,
        intensity=0.8, credibility=0.7,
    )
    for t in range(1, 4):
        r_free.step(t, rng=rng_a)

    # With suppression
    r_sup = RumorRegistry(_small_network(), authority_suppression=0.9)
    rumor_sup = r_sup.spawn(
        "accusation", origin_source="a", origin_tick=0,
        intensity=0.8, credibility=0.7,
    )
    for t in range(1, 4):
        r_sup.step(t, rng=rng_b)

    # Suppression should reduce reach
    assert len(rumor_sup.reach) <= len(rumor_free.reach)


def test_reach_fraction() -> None:
    r = RumorRegistry(_small_network())
    rumor = r.spawn("accusation", origin_source="a", origin_tick=0)
    fraction = r.reach_fraction(rumor.rumor_id, population_size=10)
    assert 0.0 <= fraction <= 1.0
    assert fraction == 0.1  # 1 agent of 10


def test_add_edge_modifies_network() -> None:
    r = RumorRegistry({"a": {"b"}, "b": {"a"}})
    r.add_edge("a", "c")
    assert "c" in r._network["a"]
    assert "a" in r._network["c"]


# -----------------------------------------------------------------
# Rule #1
# -----------------------------------------------------------------

def test_information_module_no_person_hardcoding() -> None:
    banned = ["peter", "jesus", "judas", "caiaphas", "pilate"]
    root = Path(__file__).resolve().parents[2]
    for py in (root / "engine" / "world" / "information").glob("*.py"):
        src = py.read_text(encoding="utf-8").lower()
        for b in banned:
            if re.search(rf"\b{b}\b", src):
                raise AssertionError(f"{py.name} contains '{b}' -- Rule #1")
