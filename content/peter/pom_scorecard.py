"""베드로 POM scorecard.

7개 관측 패턴을 동시에 맞춰야 유효한 시뮬레이션으로 판정.
engine/이 아니라 content/peter/에 위치 (인물 특정).
"""

from __future__ import annotations

from engine.simulation.pom import PatternCriterion
from engine.simulation.runner import SimulationResult


def make_peter_scorecard() -> list[PatternCriterion]:
    """베드로 POM scorecard."""

    def p1_no_flee(r: SimulationResult) -> bool:
        aa = next((a.chosen_action for a in r.action_history if a.event_id == "arrest"), None)
        return aa in ("follow_at_distance", "draw_sword")

    def p2_sword_drawn(r: SimulationResult) -> bool:
        return any(a.chosen_action == "draw_sword" and a.event_id == "arrest" for a in r.action_history)

    def p3_triple_denial(r: SimulationResult) -> bool:
        return sum(1 for a in r.action_history if a.chosen_action == "deny") >= 3

    def p4_grief_peak(r: SimulationResult) -> bool:
        return any(s.emotions.grief >= 8.0 for s in r.state_snapshots.values())

    def p5_moral_injury(r: SimulationResult) -> bool:
        return r.final_state.slow_state.moral_injury >= 3.0

    def p6_identity_damage(r: SimulationResult) -> bool:
        return r.final_state.slow_state.identity_shift < -1.0

    def p7_eventual_hope(r: SimulationResult) -> bool:
        return r.final_state.emotions.hope >= 3.0

    return [
        PatternCriterion("no_flee", "체포 시 도주 안 함", p1_no_flee),
        PatternCriterion("sword_drawn", "칼을 뽑음", p2_sword_drawn),
        PatternCriterion("triple_denial", "3회 부인", p3_triple_denial),
        PatternCriterion("grief_peak", "극한 슬픔 경험", p4_grief_peak),
        PatternCriterion("moral_injury", "도덕적 상처 누적", p5_moral_injury),
        PatternCriterion("identity_damage", "정체성 손상", p6_identity_damage),
        PatternCriterion("eventual_hope", "희망 회복", p7_eventual_hope),
    ]
