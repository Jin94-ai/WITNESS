"""Spike 6 Phase D — decide_action dual-path regression.

Covers:
- Rule #11 fallback: a policy returning all zeros triggers rule-based weights
- Backward compat: ``policy=None`` produces bit-identical output to a call
  without the new argument, for a fixed seed
- Neural policy plumbs through: a NeuralDecisionPolicy instance on a trivial
  model does not crash and selects a legal action
"""

from __future__ import annotations

import random

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from engine.core.event import ActionOption, WeightFormula  # noqa: E402
from engine.core.state import AgentState  # noqa: E402
from engine.policies.neural.inference import (  # noqa: E402
    NeuralDecisionPolicy,
    always_abstain_weights,
    uniform_random_weights,
)
from engine.policies.neural.model import BehaviorCloningMLP  # noqa: E402
from engine.simulation.decision import decide_action  # noqa: E402


class _StubPolicy:
    """Implements the DecisionPolicy Protocol with a fixed weight list."""

    def __init__(self, fixed_weights: list[float]) -> None:
        self._weights = fixed_weights

    def weights(self, state, options, environment=None):  # type: ignore[no-untyped-def]
        return self._weights[: len(options)]


def _simple_options() -> list[ActionOption]:
    return [
        ActionOption(
            action_id="a",
            weight_formula=WeightFormula(base_weight=1.0, state_multipliers=[]),
        ),
        ActionOption(
            action_id="b",
            weight_formula=WeightFormula(base_weight=3.0, state_multipliers=[]),
        ),
        ActionOption(
            action_id="c",
            weight_formula=WeightFormula(base_weight=1.0, state_multipliers=[]),
        ),
    ]


def test_policy_none_is_bit_identical_to_legacy_call() -> None:
    """Adding ``policy=None`` must not change the legacy sampling path."""
    state = AgentState(agent_id="probe")
    options = _simple_options()

    rng1 = random.Random(42)
    rng2 = random.Random(42)

    results_no_arg = [decide_action(state, options, rng1) for _ in range(50)]
    results_none_arg = [
        decide_action(state, options, rng2, policy=None) for _ in range(50)
    ]

    assert [r.action_id for r in results_no_arg] == [
        r.action_id for r in results_none_arg
    ]


def test_policy_all_zero_falls_back_to_rule_based() -> None:
    """Rule #11 — a policy returning all zeros must not abstain into a crash.

    It must fall through to rule-based weights, producing the same
    distribution as ``policy=None``.
    """
    state = AgentState(agent_id="probe")
    options = _simple_options()

    rng1 = random.Random(7)
    rng2 = random.Random(7)
    rng3 = random.Random(7)

    ref = [decide_action(state, options, rng1) for _ in range(80)]
    abstain = [
        decide_action(state, options, rng2, policy=_StubPolicy([0.0, 0.0, 0.0]))
        for _ in range(80)
    ]
    # `always_abstain_weights` bare function style — wrap in class.
    class _Abstain:
        def weights(self, s, o, e=None):  # type: ignore[no-untyped-def]
            return always_abstain_weights(s, o, e)

    abstain_helper = [
        decide_action(state, options, rng3, policy=_Abstain()) for _ in range(80)
    ]

    assert [r.action_id for r in ref] == [r.action_id for r in abstain]
    assert [r.action_id for r in ref] == [r.action_id for r in abstain_helper]


def test_policy_forces_single_action_when_one_weight_nonzero() -> None:
    """Policy returning [0, 100, 0] forces option 'b' every time."""
    state = AgentState(agent_id="probe")
    options = _simple_options()

    rng = random.Random(0)
    picks = [
        decide_action(state, options, rng, policy=_StubPolicy([0.0, 100.0, 0.0]))
        for _ in range(30)
    ]
    assert all(r.action_id == "b" for r in picks)


def test_uniform_random_weights_helper_rejects_nothing() -> None:
    """Uniform policy — every option should be reachable across many samples."""
    state = AgentState(agent_id="probe")
    options = _simple_options()
    rng = random.Random(1)

    class _Uniform:
        def weights(self, s, o, e=None):  # type: ignore[no-untyped-def]
            return uniform_random_weights(s, o, e)

    chosen = {
        decide_action(state, options, rng, policy=_Uniform()).action_id
        for _ in range(200)
    }
    assert chosen == {"a", "b", "c"}


def test_neural_policy_plumbs_through_decide_action() -> None:
    """Smoke: a small MLP wrapped in NeuralDecisionPolicy selects a legal
    action via decide_action. No training — just forward pass.
    """
    model = BehaviorCloningMLP(in_dim=12, n_actions=3, hidden=(8,))
    vocab = ["a", "b", "c"]
    policy = NeuralDecisionPolicy(model=model, action_vocab=vocab, device="cpu")
    state = AgentState(agent_id="probe")
    options = _simple_options()
    rng = random.Random(0)
    result = decide_action(state, options, rng, policy=policy)
    assert result is not None
    assert result.action_id in {"a", "b", "c"}


def test_neural_policy_unknown_action_yields_zero_weight() -> None:
    """If a policy's vocab doesn't cover an option, that option gets zero.

    With ALL options unknown to the policy, weights sum to zero → fallback
    to rule-based (Rule #11).
    """
    model = BehaviorCloningMLP(in_dim=12, n_actions=3, hidden=(8,))
    # Vocab that doesn't intersect the real options.
    vocab = ["foo", "bar", "baz"]
    policy = NeuralDecisionPolicy(model=model, action_vocab=vocab, device="cpu")
    state = AgentState(agent_id="probe")
    options = _simple_options()

    # Direct weight call returns all zeros.
    w = policy.weights(state, options)
    assert w == [0.0, 0.0, 0.0]

    # decide_action still returns a valid option (rule-based fallback).
    rng = random.Random(3)
    result = decide_action(state, options, rng, policy=policy)
    assert result is not None
    assert result.action_id in {"a", "b", "c"}


def test_neural_policy_describe_reports_architecture() -> None:
    model = BehaviorCloningMLP(in_dim=12, n_actions=4, hidden=(32, 16))
    policy = NeuralDecisionPolicy(
        model=model, action_vocab=["w", "x", "y", "z"], device="cpu",
    )
    info = policy.describe()
    assert info["kind"] == "neural_mlp"
    assert info["n_actions"] == 4
    assert info["in_dim"] == 12
    assert info["hidden"] == [32, 16]
    assert info["action_vocab"] == ["w", "x", "y", "z"]


def test_neural_policy_consistent_across_calls() -> None:
    """Same state → same weight distribution (deterministic eval)."""
    model = BehaviorCloningMLP(in_dim=12, n_actions=3, hidden=(8,))
    policy = NeuralDecisionPolicy(
        model=model, action_vocab=["a", "b", "c"], device="cpu",
    )
    state = AgentState(agent_id="probe")
    options = _simple_options()
    w1 = policy.weights(state, options)
    w2 = policy.weights(state, options)
    assert np.allclose(np.array(w1), np.array(w2))
