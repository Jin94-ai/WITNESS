"""반 고흐 POM scorecard.

content/에 있어야 하지만, POM 프레임워크 자체는 engine/에 있으므로
여기서 반 고흐용 패턴을 정의한다.
NOTE: 이건 content/vangogh/에 옮길 수 있지만, 지금은 빠른 검증을 위해 여기에.
"""

from __future__ import annotations

from engine.simulation.pom import PatternCriterion
from engine.simulation.runner import SimulationResult


def make_vangogh_scorecard() -> list[PatternCriterion]:
    """반 고흐 아르 시기 POM scorecard: 5개 패턴."""

    def p1_creative_output(r: SimulationResult) -> bool:
        """패턴 1: 창작 폭발 -- creative_burst 이벤트가 발동."""
        return any(fe["event_id"] == "creative_burst" for fe in r.fired_events)

    def p2_gauguin_conflict(r: SimulationResult) -> bool:
        """패턴 2: 고갱과의 갈등 -- artistic_disagreement가 2회 이상."""
        return sum(1 for fe in r.fired_events if fe["event_id"] == "artistic_disagreement") >= 2

    def p3_grief_peak(r: SimulationResult) -> bool:
        """패턴 3: 극한 슬픔 경험."""
        return any(s.emotions.grief >= 7.0 for s in r.state_snapshots.values())

    def p4_self_harm_or_crisis(r: SimulationResult) -> bool:
        """패턴 4: 자해 또는 위기 상태."""
        return any(a.chosen_action == "self_harm" for a in r.action_history)

    def p5_moral_injury(r: SimulationResult) -> bool:
        """패턴 5: 도덕적/정체성 상처 누적."""
        return r.final_state.slow_state.moral_injury >= 1.0 or r.final_state.slow_state.identity_shift < -0.5

    return [
        PatternCriterion("creative_output", "창작 폭발 경험", p1_creative_output),
        PatternCriterion("gauguin_conflict", "고갱 갈등 2회+", p2_gauguin_conflict),
        PatternCriterion("grief_peak", "극한 슬픔", p3_grief_peak),
        PatternCriterion("self_harm", "자해/위기", p4_self_harm_or_crisis),
        PatternCriterion("identity_damage", "정체성 손상", p5_moral_injury),
    ]
