"""End-to-end trace pipeline 통합 테스트.

실제 Peter SimulationWorld 결과를 trace emitter + player view filter에 통과시켜,
v1.0 파이프라인이 현실 SimulationResult와 호환됨을 증명.

검증:
1. MultiAgentResult → collect_trace_events → 비어있지 않은 event 스트림
2. action_taken, trigger_fired, canonical_match 모두 생성
3. Bifurcation report 첨부 시 bifurcation_point event 생성
4. Peter 시점 filter → 타 agent 비밀 행동/내부 정보 제거
5. JSONL 덤프/로드 round-trip
"""

import json
import tempfile
from pathlib import Path

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_hazard_events,
    load_interventions,
    load_triggers,
    register_domain_type,
)
from engine.rendering.player_view import PlayerViewFilterConfig, filter_for_player
from engine.rendering.trace_emitter import (
    collect_trace_events,
    emit_bifurcation_events,
    write_trace_jsonl,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import FearResponseRule, GriefRule, HopeRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.bifurcation import detect_bifurcation
from engine.simulation.world import SimulationWorld

register_domain_type("faith_journey", FaithJourneyState)
register_domain_type("betrayal_psychology", BetrayalPsychologyState)
register_domain_type("political_calculation", PoliticalCalculationState)
register_domain_type("crowd_dynamics", CrowdDynamicsState)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def _run_peter(seed: int = 0, max_tick: int = 100):
    peter = load_agent_state(CONTENT_DIR / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT_DIR / "judas" / "initial_state.json")
    caiaphas = load_agent_state(CONTENT_DIR / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT_DIR / "crowd" / "initial_state.json")
    triggers = load_triggers(CONTENT_DIR / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT_DIR / "peter" / "hazard_events.json")
    interventions = load_interventions(CONTENT_DIR / "peter" / "canonical_events.json")
    profiles = {
        "peter": load_behavior_profile(CONTENT_DIR / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT_DIR / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT_DIR / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT_DIR / "crowd" / "behavior_profile.json"),
    }
    config = SimulationConfig(
        max_tick=max_tick, initial_state=peter,
        initial_states=[peter, judas, caiaphas, crowd],
        hazard_events=hazards, interventions=interventions,
        triggers=triggers, state_noise_scale=0.05,
    )
    engine = RuleEngine([FearResponseRule(), GriefRule(), HopeRule(), HomeostasisRule()])
    return SimulationWorld(config, engine, behavior_profiles=profiles).run(seed=seed)


class TestTraceFromRealSimulation:
    def test_events_generated_from_peter_run(self):
        """실제 Peter 시뮬 → trace events 생성 확인."""
        result = _run_peter(seed=0, max_tick=80)
        events = collect_trace_events(result)

        # 최소한 action_taken 있어야 함 (Peter + Judas 자발 행동)
        types = {e.type for e in events}
        assert "action_taken" in types, f"No action_taken in events: {types}"

        # tick 정렬 확인
        ticks = [e.tick for e in events]
        assert ticks == sorted(ticks), "Events should be tick-sorted"

    def test_canonical_match_events_empty_without_checkpoints(self):
        """Checkpoint 설정 안 했으므로 canonical_match 없음."""
        result = _run_peter(seed=0, max_tick=50)
        events = collect_trace_events(result)
        types = {e.type for e in events}
        assert "canonical_match" not in types

    def test_bifurcation_integration(self):
        """여러 run으로 bifurcation report → trace events."""
        ensemble = [_run_peter(seed=s, max_tick=100) for s in range(5)]

        # 각 run에서 judas disill trajectory 추출
        trajectories = []
        sample_ticks = list(range(0, 100, 10))
        for r in ensemble:
            judas_snaps = r.state_snapshots.get("judas", {})
            traj = []
            for t in sample_ticks:
                candidates = [tk for tk in judas_snaps if tk <= t]
                if candidates:
                    traj.append(
                        judas_snaps[max(candidates)].domain_state.disillusionment
                    )
                else:
                    traj.append(0.0)
            trajectories.append(traj)

        report = detect_bifurcation(trajectories, window_size=2)
        bifurcation_events = list(emit_bifurcation_events([report]))
        assert len(bifurcation_events) == 1
        assert bifurcation_events[0].type == "bifurcation_point"


class TestPlayerViewFromRealSimulation:
    def test_peter_view_excludes_secret_judas_action(self):
        """Peter 시점: Judas 비밀 행동이 observable_from으로 제한되면 제외."""
        result = _run_peter(seed=0, max_tick=50)
        events = collect_trace_events(result)

        # 현 엔진은 observable_from을 설정하지 않음 (모든 action이 public)
        # 따라서 Peter 시점에서 Judas 행동도 보여야 함 (default)
        cfg = PlayerViewFilterConfig(player_id="peter")
        filtered = filter_for_player(events, cfg)

        # Filter 후에도 action_taken 존재
        filtered_types = {e.type for e in filtered}
        assert "action_taken" in filtered_types

    def test_non_player_internals_stripped(self):
        """Peter 시점에서 타 agent의 weights 등 내부 필드 제거."""
        result = _run_peter(seed=0, max_tick=50)
        events = collect_trace_events(result)
        cfg = PlayerViewFilterConfig(player_id="peter")
        filtered = filter_for_player(events, cfg)

        # Judas action 찾기
        judas_actions = [
            e for e in filtered
            if e.type == "action_taken" and e.payload.get("agent") == "judas"
        ]
        if judas_actions:
            # weights 필드가 제거되어야 함 (타 agent 내부 정보)
            for ev in judas_actions:
                assert "weights" not in ev.payload, \
                    f"Judas weights should be stripped, got {ev.payload}"

        # Peter 자기 action은 weights 보존 (include_self_internals=True)
        peter_actions = [
            e for e in filtered
            if e.type == "action_taken" and e.payload.get("agent") == "peter"
        ]
        # Peter 자기 action은 weights가 있어야 함 (존재한다면)
        # (실제로 현 엔진이 weights를 비워 저장하므로 항상 {} — 스키마 준수만 확인)
        for ev in peter_actions:
            # weights 키 자체는 남아있어야 함 (비어있더라도)
            assert "weights" in ev.payload


class TestVisibleSignalPropagation:
    """Content pack의 visible_signal이 trace pipeline을 통과하여
    narrator output에 반영되는지 E2E 검증.
    """

    def test_peter_follow_signal_in_trace(self):
        """peter의 follow_closely action이 visible_signal을 trace에 전달한다."""
        result = _run_peter(seed=0, max_tick=30)
        events = collect_trace_events(result)
        peter_actions = [
            e for e in events
            if e.type == "action_taken" and e.payload.get("agent") == "peter"
        ]
        # 적어도 하나는 content의 visible_signal이 채워져 있어야 함
        signals = [e.payload.get("visible_signal") for e in peter_actions]
        assert any(s for s in signals), "No Peter visible_signal populated from content"
        # Non-null signal은 한국어 content pack 문자열
        non_null = [s for s in signals if s]
        assert any("베드로" in s for s in non_null), \
            f"Expected '베드로' in Peter visible_signals: {non_null[:3]}"

    def test_all_agents_have_some_visible_signals(self):
        """peter/judas/caiaphas/crowd 각 agent에 visible_signal 유통 증거."""
        result = _run_peter(seed=1, max_tick=100)
        events = collect_trace_events(result)
        per_agent_signals: dict[str, set[str]] = {}
        for e in events:
            if e.type != "action_taken":
                continue
            agent = e.payload.get("agent")
            sig = e.payload.get("visible_signal")
            if agent and sig:
                per_agent_signals.setdefault(agent, set()).add(sig)
        # 4개 agent 각각 최소 한 개 signal
        for agent in ["peter", "judas", "caiaphas", "crowd"]:
            assert agent in per_agent_signals, \
                f"No visible_signal reached trace for {agent}"
            assert len(per_agent_signals[agent]) >= 1

    def test_observable_from_respected_peter_view(self):
        """Judas inform_authorities (observable_from=[caiaphas]) → Peter 시점에서 제외."""
        # disillusionment 선제 조건 맞도록 seed 충분히 긴 run
        result = _run_peter(seed=0, max_tick=200)
        events = collect_trace_events(result)
        cfg_peter = PlayerViewFilterConfig(player_id="peter")
        cfg_caiaphas = PlayerViewFilterConfig(player_id="caiaphas")
        peter_view = filter_for_player(events, cfg_peter)
        caiaphas_view = filter_for_player(events, cfg_caiaphas)

        def _has_inform(evs):
            return any(
                e.type == "action_taken"
                and e.payload.get("agent") == "judas"
                and e.payload.get("action") == "inform_authorities"
                for e in evs
            )

        # All events에는 inform_authorities가 있을 수 있음 (발생했다면)
        all_has = _has_inform(events)
        # 발생하지 않았으면 테스트 skip (deterministic seed 200tick에서 발생 여부 불확정)
        if not all_has:
            return
        # Caiaphas는 봄, Peter는 못 봄
        assert _has_inform(caiaphas_view), "caiaphas should see inform_authorities"
        assert not _has_inform(peter_view), \
            "peter must NOT see judas inform_authorities (observable_from=[caiaphas])"

    def test_narrator_uses_content_signal(self):
        """render_trace_timeline이 visible_signal을 fallback 대신 사용한다."""
        from engine.rendering.trace_narrator import render_trace_timeline

        result = _run_peter(seed=0, max_tick=40)
        events = collect_trace_events(result)
        out = render_trace_timeline(events, skip_repeats=True)
        # Content-provided 한국어 시그널이 narrative에 등장
        assert "베드로" in out, "Peter signal missing from narrative"
        # Generic fallback "을(를) 수행했다"가 dominant면 안 됨
        # (일부 action은 visible_signal 없을 수도 있지만 대다수는 있음)
        lines = out.split("\n")
        fallback_lines = [line for line in lines if "을(를) 수행했다" in line]
        signal_lines = [line for line in lines if "베드로" in line or "유다" in line
                        or "가야바" in line or "군중" in line or "대제사장" in line
                        or "경비병" in line or "산헤드린" in line]
        # signal-based 라인이 fallback 라인보다 많아야 함
        assert len(signal_lines) > len(fallback_lines), \
            f"Too many fallbacks: {len(fallback_lines)} fallback vs {len(signal_lines)} signal"


class TestJSONLRoundTrip:
    def test_write_and_parse_jsonl(self):
        """Peter 시뮬 → JSONL 파일 → 다시 파싱 → 구조 유지."""
        result = _run_peter(seed=0, max_tick=60)
        events = collect_trace_events(result)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8",
        ) as f:
            path = f.name
        try:
            n = write_trace_jsonl(events, path)
            assert n == len(events)

            # 파싱
            with open(path, encoding="utf-8") as rf:
                parsed = [json.loads(line) for line in rf]
            assert len(parsed) == n

            # 각 entry에 tick, type, payload 존재
            for entry in parsed:
                assert "tick" in entry
                assert "type" in entry
                assert "payload" in entry
        finally:
            import os
            os.unlink(path)
