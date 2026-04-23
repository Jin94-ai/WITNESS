"""Talleyrand POM scorecard — Type A (Negotiation/Diplomatic) 패턴 (Iter 56).

Peter/VG의 accumulation→threshold→rare-action bottleneck 구조와 **대비**되는
Type A 협상형 패턴 7개. 각 시뮬레이션 run이 이 패턴을 동시에 만족해야
"canonical-compatible Talleyrand 궤적"으로 인정.

Peter/VG는 `SimulationRunner`의 단일 agent `SimulationResult` 기반이지만,
Talleyrand는 multi-agent 지원 `SimulationWorld`의 `MultiAgentResult` 기반
(미래 외교 파트너 agent 추가 대비). 두 result 타입 모두에서 동작하도록
`getattr` 기반 duck typing으로 작성.
"""

from __future__ import annotations

from typing import Any

from engine.simulation.pom import PatternCriterion


def _get_talleyrand_final(result: Any) -> Any:
    """SimulationResult / MultiAgentResult 공통으로 Talleyrand 최종 state 추출.

    talleyrand agent가 없는 scenario에서는 None 반환 (pattern이 False로 귀결).
    """
    if hasattr(result, "final_states"):
        states = result.final_states
        if "talleyrand" in states:
            return states["talleyrand"]
        return None
    if hasattr(result, "final_state"):
        s = result.final_state
        # single-agent SimulationResult의 agent_id가 talleyrand인지 확인
        if getattr(s, "agent_id", None) == "talleyrand":
            return s
        return None
    return None


def _get_fired_events(result: Any) -> list:
    return getattr(result, "fired_events", [])


def _get_action_history(result: Any, agent_id: str = "talleyrand") -> list:
    if hasattr(result, "action_histories"):
        return result.action_histories.get(agent_id, [])
    if hasattr(result, "action_history"):
        return result.action_history
    return []


def make_talleyrand_scorecard() -> list[PatternCriterion]:
    """Talleyrand Type A POM scorecard: 7 patterns."""

    def p1_multi_regime_survival(r: Any) -> bool:
        """1. 5개 이상 regime transition 경험. Peter/VG에는 없는 구조."""
        regime_events = [
            e for e in _get_fired_events(r)
            if str(e.get("event_id", "")).startswith("regime_")
        ]
        return len(regime_events) >= 5

    def p2_network_regime_span_grown(r: Any) -> bool:
        """2. 다체제 인맥망 확장: network_regime_span >= 4 (초기 1에서 +3 이상)."""
        final = _get_talleyrand_final(r)
        if final is None:
            return False
        return getattr(final.domain_state, "network_regime_span", 0) >= 4

    def p3_reputation_ambiguity_emergent(r: Any) -> bool:
        """3. 평판 ambiguity 축적 (협상가의 자원): >= 6.0 (초기 4.0)."""
        final = _get_talleyrand_final(r)
        if final is None:
            return False
        return getattr(final.domain_state, "reputation_ambiguity", 0.0) >= 6.0

    def p4_compromise_accumulation(r: Any) -> bool:
        """4. 타협 3회 이상 — 원칙 협상가는 이 숫자가 낮고 실용가는 높음."""
        final = _get_talleyrand_final(r)
        if final is None:
            return False
        return getattr(final.domain_state, "compromise_count", 0) >= 3

    def p5_no_emotional_collapse(r: Any) -> bool:
        """5. 감정 붕괴 없음: fear 극한(>=9.5)이나 grief 극한 도달 안 함.

        Peter sword_drawn / VG self_harm 같은 rare-action bottleneck과 대비.
        협상가는 **극단 감정 상태로 결단하지 않는다** — 점진적 재조정으로 대응.
        """
        final = _get_talleyrand_final(r)
        if final is None:
            return False
        snapshots = getattr(r, "state_snapshots", {})
        if isinstance(snapshots, dict) and "talleyrand" in snapshots:
            agent_snaps = snapshots["talleyrand"]
            if isinstance(agent_snaps, dict):
                for s in agent_snaps.values():
                    if s.emotions.fear >= 9.5 or s.emotions.grief >= 9.5:
                        return False
        return final.emotions.fear < 9.5 and final.emotions.grief < 9.5

    def p6_career_continuity(r: Any) -> bool:
        """6. career 완주: 최종 tick이 시나리오 종료 지점에 도달 (붕괴로 조기 종료 없음).

        Peter arrest/VG breakdown 같은 early termination 없음.
        """
        final = _get_talleyrand_final(r)
        if final is None:
            return False
        return final.tick >= 400

    def p7_legitimacy_below_anchor_threshold(r: Any) -> bool:
        """7. 실용주의 유지: legitimacy_anchor <= 5.0."""
        final = _get_talleyrand_final(r)
        if final is None:
            return False
        return getattr(final.domain_state, "legitimacy_anchor", 10.0) <= 5.0

    return [
        PatternCriterion(
            "multi_regime_survival",
            "5개 이상 regime transition 거침",
            p1_multi_regime_survival,
        ),
        PatternCriterion(
            "network_regime_span_grown",
            "다체제 인맥망 span >= 4",
            p2_network_regime_span_grown,
        ),
        PatternCriterion(
            "reputation_ambiguity_emergent",
            "평판 ambiguity >= 6.0 (협상가 자원)",
            p3_reputation_ambiguity_emergent,
        ),
        PatternCriterion(
            "compromise_accumulation",
            "타협 3회 이상 누적",
            p4_compromise_accumulation,
        ),
        PatternCriterion(
            "no_emotional_collapse",
            "fear/grief 9.5 미만 유지 (붕괴 없음)",
            p5_no_emotional_collapse,
        ),
        PatternCriterion(
            "career_continuity",
            "career 80% 이상 완주",
            p6_career_continuity,
        ),
        PatternCriterion(
            "legitimacy_below_anchor",
            "legitimacy_anchor <= 5.0 (실용주의)",
            p7_legitimacy_below_anchor_threshold,
        ),
    ]
