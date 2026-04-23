"""WeightFormula.compute_weight_breakdown 테스트 (Trace Schema §2.2).

Action weight의 구성 요소(base + state_multipliers)를 추적 가능하게 로그.
v2.0 render-ready trace의 필수 요소. v1.0 drive 모델 도입 시 drive contribution 추가.
"""

from engine.core.event import StateMultiplier, WeightFormula
from engine.core.state import AgentState, EmotionalState


def _state(fear: float = 5.0) -> AgentState:
    return AgentState(
        agent_id="test",
        emotions=EmotionalState(fear=fear),
    )


class TestWeightBreakdown:
    def test_no_multipliers_base_only(self):
        """State multiplier 없으면 base만 등장."""
        wf = WeightFormula(base_weight=2.0)
        br = wf.compute_weight_breakdown(_state())
        assert br["base"] == 2.0
        assert br["final"] == 2.0
        assert len(br) == 2

    def test_single_multiplier(self):
        """Single state_multiplier → breakdown 3 entries."""
        wf = WeightFormula(
            base_weight=1.0,
            state_multipliers=[
                StateMultiplier(
                    field_path="emotions.fear",
                    factor_type="linear",
                    params={"scale": 0.1},
                ),
            ],
        )
        br = wf.compute_weight_breakdown(_state(fear=5.0))
        assert "base" in br
        assert "state_mult.emotions.fear" in br
        assert "final" in br
        # final = base * contribution
        assert abs(br["final"] - br["base"] * br["state_mult.emotions.fear"]) < 1e-6

    def test_multiple_multipliers(self):
        """여러 multiplier → 각각 별도 key."""
        wf = WeightFormula(
            base_weight=1.0,
            state_multipliers=[
                StateMultiplier(
                    field_path="emotions.fear",
                    factor_type="linear",
                    params={"scale": 0.1},
                ),
                StateMultiplier(
                    field_path="emotions.hope",
                    factor_type="linear",
                    params={"scale": 0.1},
                ),
            ],
        )
        br = wf.compute_weight_breakdown(_state())
        assert "state_mult.emotions.fear" in br
        assert "state_mult.emotions.hope" in br

    def test_duplicate_field_indexed(self):
        """같은 field가 여러 번 쓰이면 인덱싱."""
        wf = WeightFormula(
            base_weight=1.0,
            state_multipliers=[
                StateMultiplier(
                    field_path="emotions.fear",
                    factor_type="linear",
                    params={"scale": 0.1},
                ),
                StateMultiplier(
                    field_path="emotions.fear",
                    factor_type="inverse",
                    params={"scale": 0.2},
                ),
            ],
        )
        br = wf.compute_weight_breakdown(_state())
        assert "state_mult.emotions.fear" in br
        assert "state_mult.emotions.fear[1]" in br

    def test_breakdown_matches_compute_weight(self):
        """breakdown의 final 값이 compute_weight와 일치."""
        wf = WeightFormula(
            base_weight=1.5,
            state_multipliers=[
                StateMultiplier(
                    field_path="emotions.fear",
                    factor_type="linear",
                    params={"scale": 0.15},
                ),
            ],
        )
        state = _state(fear=7.0)
        w = wf.compute_weight(state)
        br = wf.compute_weight_breakdown(state)
        assert abs(br["final"] - w) < 1e-9

    def test_zero_base_safety(self):
        """base=0이면 final도 최소 0.001 (기존 계약 유지)."""
        wf = WeightFormula(base_weight=0.0)
        br = wf.compute_weight_breakdown(_state())
        assert br["final"] >= 0.001
