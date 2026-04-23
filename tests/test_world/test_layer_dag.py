"""DAG integrity tests — A-3: no same-tick cyclic feedback.

Each layer declares its causal_dependencies in describe_dynamics(). This
file asserts that the dependency graph across all world layers is a DAG
when the tick order is applied: every layer only depends on layers that
were updated *earlier in the same tick* OR on layers from the previous
tick. This is the automated guardrail for ABSOLUTE RULE #9 (see
WORLD_DESIGN.md §8).

If Spike 3 introduces a cycle (e.g. faction ↔ crowd), the cycle MUST be
broken by inserting a 1-tick delay (i.e. reading last-tick's value
instead of this-tick's value). Such reads should be marked in the
causal_dependencies list with the suffix ``@prev_tick``.
"""

from __future__ import annotations

import pytest

from world.economy.economy import EconomyLayer
from world.environment.calendar import CalendarLayer
from world.factions.factions import FactionLayer
from world.politics.politics import PoliticsLayer
from world.social.crowd import CrowdLayer
from world.social.rumors import RumorLayer

# The canonical Spike 1-3 tick order used by WorldTick. Each layer may
# only read from layers scheduled earlier in this list (same-tick) or
# from @prev_tick values of any layer.
TICK_ORDER = [
    ("calendar", CalendarLayer()),
    ("crowd",    CrowdLayer()),
    ("economy",  EconomyLayer()),
    ("politics", PoliticsLayer()),
    ("rumors",   RumorLayer()),
    ("factions", FactionLayer()),
]


def _layer_dependencies(layer_obj) -> list[str]:
    """Return declared same-tick dependencies (excluding @prev_tick reads)."""
    deps = layer_obj.describe_dynamics().get("causal_dependencies", [])
    return [d for d in deps if "@prev_tick" not in d]


def _dep_to_layer_id(dep: str) -> str:
    """'calendar.pilgrim_influx_target' -> 'calendar'."""
    return dep.split(".", 1)[0]


@pytest.mark.parametrize("layer_id,layer_obj", TICK_ORDER)
def test_layer_declares_describe_dynamics(layer_id: str, layer_obj) -> None:
    desc = layer_obj.describe_dynamics()
    assert desc["layer_id"] == layer_id
    assert "causal_dependencies" in desc or "deterministic" in desc


def test_tick_order_is_a_dag() -> None:
    """Every same-tick dependency must point to a layer scheduled earlier.

    If this test fails, either reorder the layers in WorldTick or introduce
    a 1-tick delay (documented via @prev_tick on the dependency string).

    ``aggregated_effects.*`` is a whitelisted pseudo-source — the Sync
    Layer fills it from the PREVIOUS world day, so reading it mid-tick
    is not a cycle.
    """
    # aggregated_effects is fed from the prior world day, not this tick's
    # layers, so we pre-seed it as "already scheduled" for DAG purposes.
    scheduled_so_far: set[str] = {"aggregated_effects"}
    for layer_id, layer_obj in TICK_ORDER:
        deps = _layer_dependencies(layer_obj)
        for dep in deps:
            dep_layer = _dep_to_layer_id(dep)
            assert dep_layer in scheduled_so_far, (
                f"layer '{layer_id}' reads same-tick from '{dep_layer}' "
                f"which is not yet scheduled. Either (a) reorder layers, "
                f"or (b) read from previous tick: annotate the dependency "
                f"in describe_dynamics() as '{dep}@prev_tick'."
            )
        scheduled_so_far.add(layer_id)


def test_no_self_loop_in_same_tick() -> None:
    """A layer may NOT reference itself in same-tick causal_dependencies."""
    for layer_id, layer_obj in TICK_ORDER:
        deps = _layer_dependencies(layer_obj)
        for dep in deps:
            assert _dep_to_layer_id(dep) != layer_id, (
                f"layer '{layer_id}' declares a same-tick self-dependency "
                f"on '{dep}'. Self-dependencies must always be @prev_tick "
                f"(the previous tick's value) to avoid an implicit cycle."
            )


def test_politics_reads_crowd_same_tick() -> None:
    """Sanity — the politics layer SHOULD read the crowd layer in the same
    tick (the threshold boost depends on freshly-updated density). This
    asserts the expected cross-layer edge is present."""
    politics = PoliticsLayer()
    deps = politics.describe_dynamics()["causal_dependencies"]
    assert any(d.startswith("crowd.") for d in deps)


def test_economy_reads_calendar_same_tick() -> None:
    """Sanity — economy reads today's pilgrim_influx_target (from the
    just-advanced calendar)."""
    econ = EconomyLayer()
    deps = econ.describe_dynamics()["causal_dependencies"]
    assert any(d.startswith("calendar.") for d in deps)
