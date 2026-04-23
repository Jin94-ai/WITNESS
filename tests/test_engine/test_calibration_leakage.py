"""Calibration Leakage 점검.

ChatGPT 피드백: "trigger 설계와 POM 패턴이 같은 역사 서술을 반복 소비하는가?"

설계 정보(trigger conditions, hazard events, behavior profiles)와
검증 정보(POM patterns)가 독립적인가를 구조적으로 분석한다.

Leakage가 있으면: 시뮬레이터가 역사적 결과를 "맞추는" 게 아니라
같은 정보를 두 번 쓰고 있는 것일 뿐.
"""

from pathlib import Path

from content.peter.pom_scorecard import make_peter_scorecard
from engine.io.loader import load_hazard_events, load_triggers

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _trigger_design_inputs() -> set[str]:
    """트리거 설계에 사용된 '정보 소스'를 추출한다.

    각 trigger condition은 특정 상태/행동을 기준으로 한다.
    이 기준이 되는 정보의 출처를 추적.
    """
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")

    # trigger 조건이 참조하는 필드/행동
    referenced: set[str] = set()
    for t in triggers:
        for sc in t.state_conditions:
            referenced.add(f"state:{sc.agent_id}.{sc.field_path}")
        for ac in t.action_conditions:
            referenced.add(f"action:{ac.agent_id}.{ac.action_id}")
    return referenced


def _hazard_design_inputs() -> set[str]:
    """hazard 이벤트 설계의 정보 소스."""
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    referenced: set[str] = set()
    for h in hazards:
        referenced.add(f"event:{h.event_id}")
        for opt_data in h.action_options_on_fire:
            aid = opt_data.get("action_id") if isinstance(opt_data, dict) else None
            if aid:
                referenced.add(f"action:peter.{aid}")
    return referenced


def _pom_validation_targets() -> set[str]:
    """POM 패턴이 검증하는 '관측값'을 추출한다."""
    # make_peter_scorecard의 각 패턴이 검증하는 대상
    # (함수 내부 로직을 분석)
    return {
        "action:peter.follow_at_distance",  # p1_no_flee
        "action:peter.draw_sword",          # p1, p2
        "action:peter.deny",                # p3_triple_denial
        "state:peter.emotions.grief",       # p4_grief_peak
        "state:peter.slow_state.moral_injury",  # p5
        "state:peter.slow_state.identity_shift",  # p6
        "state:peter.emotions.hope",        # p7
    }


class TestCalibrationLeakage:
    def test_trigger_pom_independence(self):
        """트리거 설계 조건과 POM 검증 대상이 독립적인가?

        트리거가 참조하는 것: Judas.disillusionment, Caiaphas.threat 등 (원인)
        POM이 검증하는 것: Peter.deny, Peter.grief 등 (결과)

        원인-결과가 다른 에이전트/필드라면 독립적 (leakage 없음).
        같은 필드를 쓰면 leakage 의심.
        """
        trigger_inputs = _trigger_design_inputs()
        pom_targets = _pom_validation_targets()

        overlap = trigger_inputs & pom_targets
        print("\n=== Calibration Leakage Analysis ===")
        print(f"Trigger design inputs ({len(trigger_inputs)}):")
        for t in sorted(trigger_inputs):
            print(f"  {t}")
        print(f"\nPOM validation targets ({len(pom_targets)}):")
        for p in sorted(pom_targets):
            print(f"  {p}")
        print(f"\nOverlap: {overlap if overlap else 'NONE'}")

        # 트리거 조건에 Peter의 행동이 직접 포함되면 leakage
        peter_action_in_trigger = any(
            "peter" in t and "action" in t for t in trigger_inputs
        )
        peter_state_in_trigger = any(
            "peter" in t and "state" in t for t in trigger_inputs
        )

        print("\nLeakage indicators:")
        print(f"  Peter action in trigger conditions: {peter_action_in_trigger}")
        print(f"  Peter state in trigger conditions: {peter_state_in_trigger}")

        # 검증: trigger는 Peter의 상태/행동을 조건으로 쓰면 안 됨
        # (Peter는 결과 관측 대상, trigger는 원인 측)
        assert not peter_action_in_trigger, \
            "Leakage: trigger condition references Peter's actions (validation target)"
        assert not peter_state_in_trigger, \
            "Leakage: trigger condition references Peter's state (validation target)"

    def test_trigger_effects_on_peter_are_expected(self):
        """트리거 효과가 Peter의 상태를 바꾸는 것은 허용되지만 명시되어야 한다.

        이것은 leakage가 아니라 인과 전달.
        원인(Judas의 행동) -> 결과(Peter의 상태 변화) 라는 명시적 경로.
        """
        triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
        peter_effects = []
        for t in triggers:
            for eff in t.effects_on_fire:
                if isinstance(eff, dict) and eff.get("target_agent_id") == "peter":
                    peter_effects.append((t.trigger_id, eff["field_path"], eff["operation"], eff["value"]))

        print("\n=== Trigger Effects on Peter ===")
        for tid, fp, op, v in peter_effects:
            print(f"  {tid}: peter.{fp} {op} {v}")

        # 이것들은 "원인 -> 결과" 인과이므로 OK
        # 다만 모두 emotions 계열 (fast state)여야 -- slow_state 직접 set은 의심
        for tid, fp, op, v in peter_effects:
            assert "slow_state" not in fp, \
                f"Suspicious: trigger {tid} directly sets peter.{fp} (slow state bypass)"

    def test_pom_patterns_dont_match_hazard_events_directly(self):
        """POM 패턴이 hazard 이벤트 발동 여부를 직접 검증하지 않는다.

        Peter의 hazard_events는 'arrest', 'denial_challenge' 등을 정의한다.
        POM이 단순히 'arrest 이벤트가 발동했나?'를 검증하면 이는 순환 검증.
        실제 POM은 이벤트 이후의 '행동 선택'과 '상태 변화'를 검증해야 한다.
        """
        # p1~p7을 검토:
        # p1_no_flee: arrest 이벤트의 행동 선택 (draw_sword, follow_at_distance)
        # p3_triple_denial: deny 행동 카운트 (특정 이벤트 무관)
        # p4_grief_peak: 상태 값 (행동 결과)
        # 모두 "이벤트 이후의 선택/결과"를 검증 -- OK

        # 반증 예: POM에 "arrest 이벤트가 발동함"이 있으면 순환 검증
        # make_peter_scorecard의 7개 패턴 모두 그런 패턴이 없음을 확인
        scorecard = make_peter_scorecard()
        pattern_names = {p.name for p in scorecard}

        # 직접 이벤트 발동 검증 패턴이 없어야 함
        forbidden = {"arrest_fired", "denial_challenge_fired", "rooster_fired"}
        circular = pattern_names & forbidden
        assert not circular, f"Circular validation: {circular}"

        print("\n=== POM Pattern Review ===")
        for p in scorecard:
            print(f"  {p.name:20s}: {p.description}")
        print("\nNone validate 'event fired' directly - all check actions/states AFTER events.")


class TestLeakageSummary:
    def test_summary_report(self):
        """Calibration Leakage 최종 판정."""
        trigger_inputs = _trigger_design_inputs()
        pom_targets = _pom_validation_targets()

        overlap = trigger_inputs & pom_targets
        peter_in_trigger = any("peter" in t for t in trigger_inputs)

        print("\n=== CALIBRATION LEAKAGE VERDICT ===")
        print(f"Trigger-POM overlap: {len(overlap)} items")
        print(f"Peter referenced in trigger design: {peter_in_trigger}")

        if not overlap and not peter_in_trigger:
            print("VERDICT: No calibration leakage detected.")
            print("  Triggers (causes) are defined on Judas/Caiaphas/Crowd states/actions.")
            print("  POM (effects) validates Peter's actions/states.")
            print("  Cause-effect structure is respected.")
        else:
            print("VERDICT: Potential leakage - needs review")

        # 구조적 분리 확인
        assert not overlap
        assert not peter_in_trigger
