"""Training sample extractor 테스트.

v1.0 학습 데이터 준비 계층 검증.
"""

from types import SimpleNamespace

from engine.core.state import AgentState, EmotionalState, SlowState
from engine.simulation.checkpoint import ActionRecord
from engine.simulation.training_samples import (
    SampleStatistics,
    extract_samples,
    samples_to_feature_matrix,
    state_to_feature_vector,
    summarize_samples,
)


def _state(fear: float = 0.0, tick: int = 0, aid: str = "peter") -> AgentState:
    return AgentState(
        agent_id=aid,
        tick=tick,
        emotions=EmotionalState(fear=fear),
    )


class TestStateToFeatureVector:
    def test_vector_length_12(self):
        state = _state()
        vec = state_to_feature_vector(state)
        assert len(vec) == 12

    def test_vector_reflects_fields(self):
        state = AgentState(
            agent_id="x",
            emotions=EmotionalState(fear=3.0, hope=7.0),
            slow_state=SlowState(moral_injury=2.0),
        )
        vec = state_to_feature_vector(state)
        assert vec[0] == 3.0  # fear
        assert vec[1] == 7.0  # hope
        assert vec[8] == 2.0  # moral_injury


class TestExtractSamples:
    def test_empty_result_no_samples(self):
        result = SimpleNamespace(
            state_snapshots={}, action_histories={},
            fired_events=[], fired_triggers=[],
        )
        assert extract_samples(result) == []

    def test_single_agent_pairs(self):
        """3 snapshots → 2 samples (t0→t1, t1→t2)."""
        snaps = {
            "peter": {
                0: _state(fear=0.0, tick=0),
                10: _state(fear=2.0, tick=10),
                20: _state(fear=5.0, tick=20),
            }
        }
        actions = {
            "peter": [
                ActionRecord(tick=0, event_id="v", chosen_action="follow"),
                ActionRecord(tick=10, event_id="v", chosen_action="pray"),
            ]
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories=actions,
            fired_events=[{"event_id": "storm", "tick": 10}],
            fired_triggers=[],
        )
        samples = extract_samples(result)
        assert len(samples) == 2
        s0 = samples[0]
        assert s0.tick == 0
        assert s0.next_tick == 10
        assert s0.action == "follow"
        assert s0.agent_id == "peter"

        s1 = samples[1]
        assert s1.tick == 10
        assert s1.action == "pray"
        assert "storm" in s1.event_ids

    def test_multi_agent(self):
        snaps = {
            "peter": {0: _state(tick=0, aid="peter"), 5: _state(tick=5, aid="peter")},
            "judas": {0: _state(tick=0, aid="judas"), 5: _state(tick=5, aid="judas")},
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories={},
            fired_events=[], fired_triggers=[],
        )
        samples = extract_samples(result)
        assert len(samples) == 2
        ids = {s.agent_id for s in samples}
        assert ids == {"peter", "judas"}

    def test_trigger_events_captured(self):
        snaps = {
            "peter": {0: _state(tick=0), 10: _state(tick=10)},
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories={},
            fired_events=[],
            fired_triggers=[{"trigger_id": "arrest_trigger", "tick": 0}],
        )
        samples = extract_samples(result)
        assert len(samples) == 1
        assert "trigger:arrest_trigger" in samples[0].event_ids

    def test_tick_delta_property(self):
        snaps = {
            "peter": {5: _state(tick=5), 25: _state(tick=25)},
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories={},
            fired_events=[], fired_triggers=[],
        )
        [sample] = extract_samples(result)
        assert sample.tick_delta == 20


class TestFeatureMatrix:
    def test_matrix_shape(self):
        snaps = {
            "peter": {
                0: _state(tick=0),
                5: _state(fear=1.0, tick=5),
                10: _state(fear=2.0, tick=10),
            }
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories={},
            fired_events=[], fired_triggers=[],
        )
        samples = extract_samples(result)
        X, Y, actions = samples_to_feature_matrix(samples)
        assert len(X) == 2
        assert len(Y) == 2
        assert len(actions) == 2
        assert len(X[0]) == 12  # state feature dim

    def test_actions_preserved(self):
        snaps = {"peter": {0: _state(tick=0), 5: _state(tick=5)}}
        act = [ActionRecord(tick=0, event_id="v", chosen_action="flee")]
        result = SimpleNamespace(
            state_snapshots=snaps,
            action_histories={"peter": act},
            fired_events=[], fired_triggers=[],
        )
        samples = extract_samples(result)
        X, Y, actions = samples_to_feature_matrix(samples)
        assert actions == ["flee"]


class TestSampleStatistics:
    def test_empty_stats(self):
        stats = summarize_samples([])
        assert stats.n_samples == 0
        assert stats.n_agents == 0
        assert stats.action_counts == {}
        assert stats.event_rate == 0.0
        assert stats.most_common_action is None
        assert stats.action_imbalance_ratio == 0.0

    def test_counts_and_event_rate(self):
        snaps = {
            "peter": {
                0: _state(tick=0, aid="peter"),
                5: _state(tick=5, aid="peter"),
                10: _state(tick=10, aid="peter"),
            },
            "judas": {
                0: _state(tick=0, aid="judas"),
                5: _state(tick=5, aid="judas"),
            },
        }
        actions = {
            "peter": [
                ActionRecord(tick=0, event_id="v", chosen_action="follow"),
                ActionRecord(tick=5, event_id="v", chosen_action="pray"),
            ],
            "judas": [ActionRecord(tick=0, event_id="v", chosen_action="withdraw")],
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories=actions,
            fired_events=[{"event_id": "X", "tick": 5}],
            fired_triggers=[],
        )
        samples = extract_samples(result)
        stats = summarize_samples(samples)
        assert isinstance(stats, SampleStatistics)
        # peter: 2 samples (t0, t5), judas: 1 sample (t0)
        assert stats.n_samples == 3
        assert stats.n_agents == 2
        assert stats.agent_counts == {"peter": 2, "judas": 1}
        # 1 sample has events (peter tick=5 → 'X')
        assert stats.event_rate == 1 / 3
        # actions: follow, pray, withdraw
        assert stats.action_counts == {"follow": 1, "pray": 1, "withdraw": 1}
        assert stats.action_imbalance_ratio == 1.0
        assert stats.avg_tick_delta == 5.0

    def test_imbalance_ratio(self):
        # 2 peter samples, one with common action, one rare
        snaps = {
            "peter": {
                0: _state(tick=0),
                5: _state(tick=5),
                10: _state(tick=10),
                15: _state(tick=15),
            }
        }
        actions = {
            "peter": [
                ActionRecord(tick=0, event_id="v", chosen_action="follow"),
                ActionRecord(tick=5, event_id="v", chosen_action="follow"),
                ActionRecord(tick=10, event_id="v", chosen_action="follow"),
                ActionRecord(tick=15, event_id="v", chosen_action="deny"),
            ]
        }
        result = SimpleNamespace(
            state_snapshots=snaps, action_histories=actions,
            fired_events=[], fired_triggers=[],
        )
        samples = extract_samples(result)
        stats = summarize_samples(samples)
        # follow:3 deny:1 (only 3 samples since we need pairs)
        # action for last sample (tick=10) is "follow", sample at tick=15 omitted
        # so follow:3 from ticks 0,5,10 — no deny in samples
        common = stats.most_common_action
        assert common is not None
        assert common[0] == "follow"
