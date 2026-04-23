"""Small simulation-module edge branches for 100% coverage."""

from types import SimpleNamespace

from engine.core.state import AgentState, EmotionalState
from engine.simulation.bifurcation import (
    _find_non_overlapping_peaks,
    detect_bifurcation,
)
from engine.simulation.checkpoint import ActionRecord
from engine.simulation.drive_training import train_and_validate
from engine.simulation.explanation import generate_explanation
from engine.simulation.resolution import ResolutionConfig, ResolutionEngine


class TestBifurcationHelpers:
    def test_find_non_overlapping_peaks_empty(self):
        """empty series → empty list (line 71)."""
        assert _find_non_overlapping_peaks([], top_k=3, min_gap=2) == []

    def test_detect_bifurcation_single_trajectory(self):
        """run이 1개면 cross-run std = 0 (lines 125, 134)."""
        rep = detect_bifurcation([[float(i) for i in range(50)]], window_size=10)
        assert all(s == 0.0 for s in rep.state_std_series)
        assert rep.max_growth_std_value == 0.0


class TestExplanationEdges:
    def test_empty_action_history(self):
        """action_histories가 비어있는 agent는 skip (line 99)."""
        result = SimpleNamespace(
            seed=0,
            action_histories={"peter": [], "judas": [
                ActionRecord(tick=1, event_id="v", chosen_action="x"),
                ActionRecord(tick=2, event_id="v", chosen_action="y"),
            ]},
            fired_triggers=[], fired_events=[],
            final_states={}, state_snapshots={},
            canonical_match_rates={},
        )
        card = generate_explanation(result)
        # no crash
        assert "causal_chain" in card

    def test_single_action_type_skipped(self):
        """action_counts가 1개면 rare 판정 skip (line 102)."""
        result = SimpleNamespace(
            seed=0,
            action_histories={"peter": [
                ActionRecord(tick=i, event_id="v", chosen_action="follow")
                for i in range(10)
            ]},
            fired_triggers=[], fired_events=[],
            final_states={}, state_snapshots={},
            canonical_match_rates={},
        )
        card = generate_explanation(result)
        # 단일 action이면 rare chain 없음, 하지만 crash 없이 card 반환
        assert "outcome_summary" in card

    def test_outcome_no_triggers(self):
        """fired_triggers가 비어있으면 'completed without trigger' (line 128)."""
        result = SimpleNamespace(
            seed=0,
            action_histories={"peter": [
                ActionRecord(tick=1, event_id="v", chosen_action="pray"),
            ]},
            fired_triggers=[], fired_events=[],
            final_states={}, state_snapshots={},
            canonical_match_rates={},
        )
        card = generate_explanation(result)
        assert "without trigger" in card["outcome_summary"]


class TestResolutionEngineConfigProperty:
    def test_config_property_returns_original(self):
        """config property 접근 (line 118)."""
        cfg = ResolutionConfig()
        mgr = ResolutionEngine(cfg)
        assert mgr.config is cfg


class TestDriveTrainingDefaultConfig:
    def test_train_and_validate_without_config_uses_default(self):
        """config=None → TrainingConfig() default (line 193)."""
        def run_fn(seed: int):
            return SimpleNamespace(
                state_snapshots={"a": {
                    0: AgentState(agent_id="a", emotions=EmotionalState()),
                    5: AgentState(agent_id="a", emotions=EmotionalState()),
                }},
                action_histories={"a": [
                    ActionRecord(tick=0, event_id="v", chosen_action="x"),
                ]},
                fired_events=[], fired_triggers=[],
            )
        model, report = train_and_validate(run_fn, config=None)
        assert model.is_active()  # identity fallback
        assert report.n_samples >= 0
