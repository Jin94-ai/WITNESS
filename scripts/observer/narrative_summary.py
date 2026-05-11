"""World Observer — Narrative Summary (Phase O7).

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §5.3 + Lee spec §11.3
("Lee의 판독 효율 향상").

Observer가 가진 multi-tick snapshot stream을 *짧은 한국어 prose*로 변환.
관찰기 ≠ 평가기 원칙 보존 — *현황 묘사*만, *quality verdict 아님*.

기존 Story Output Layer (probe-shaped, single-tick final outcome) 우회 +
Observer 강점인 multi-tick stream에 최적화한 새 narrator.

ABSOLUTE Rule #1: no person hardcoding. agent_id는 그대로 노출.

Functions:
    narrate_world_arc(observer)         — world view trajectory prose
    narrate_person_arc(observer, agent_id) — agent arc prose
    narrate_event_ripple(observer, event_id) — event 영향 prose
    narrate_seed_comparison(streams)    — multi-stream contrast prose
"""

from __future__ import annotations

from engine.observer.core import Observer
from engine.observer.salience import top_salient_moments

# ============================================================
# Korean tag mapping (관측 태그만, 평가 단어 회피)
# ============================================================

_MOOD_KO: dict[str, str] = {
    "calm": "고요한",
    "tense": "긴장된",
    "agitated": "동요한",
    "fragmenting": "분열된",
}

_MOOD_NOUN_KO: dict[str, str] = {
    "calm": "고요",
    "tense": "긴장",
    "agitated": "동요",
    "fragmenting": "분열",
}

_MODE_KO: dict[str, str] = {
    "saturation": "고착",
    "recovery": "회복",
    "mixed": "분기",
    "low_activity": "정적",
    "partial": "부분적",
}


# ============================================================
# Helpers
# ============================================================


def _intensity_word(value: float) -> str:
    """0.0-1.0 값을 한국어 강도 단어로. 평가 아님, *값 묘사*."""
    if value < 0.1:
        return "거의 없는"
    if value < 0.3:
        return "옅은"
    if value < 0.5:
        return "중간"
    if value < 0.7:
        return "짙은"
    if value < 0.9:
        return "강한"
    return "극심한"


def _delta_word(diff: float) -> str:
    """tick-over-tick 차이를 한국어 동사. 평가 아님, *변화 방향*."""
    if diff > 0.3:
        return "급격히 올랐다"
    if diff > 0.1:
        return "오르고 있다"
    if diff > -0.1:
        return "거의 변화 없다"
    if diff > -0.3:
        return "내리고 있다"
    return "급격히 내렸다"


# ============================================================
# 1. World Arc Narrator
# ============================================================


def narrate_world_arc(
    observer: Observer,
    tick_from: int | None = None,
    tick_to: int | None = None,
) -> str:
    """World view trajectory를 짧은 prose로 묘사.

    구조:
    - 시작 mood + 끝 mood (변화 묘사)
    - 가장 큰 metric 변화 1-2개
    - active events 등장 시 명시
    - salient moments 카운트

    *현황 묘사만*, *quality verdict 아님*.
    """
    trace = observer.get_world_trace(tick_from, tick_to)
    if not trace:
        return "관찰 가능한 tick이 없다."

    first_tick, first_ws = trace[0]
    last_tick, last_ws = trace[-1]

    first_mood = _MOOD_NOUN_KO.get(first_ws.crowd_mood, first_ws.crowd_mood)
    last_mood = _MOOD_NOUN_KO.get(last_ws.crowd_mood, last_ws.crowd_mood)

    lines: list[str] = []

    # Opening
    lines.append(
        f"tick {first_tick}부터 {last_tick}까지의 흐름이다. "
        f"세계는 {first_mood} 상태로 시작해 {last_mood} 상태로 끝났다."
    )

    # Metric changes (find biggest delta across trace)
    metric_changes: list[tuple[str, float, float]] = []
    for metric_name, getter in [
        ("비난", lambda ws: ws.blame_concentration),
        ("의심", lambda ws: ws.public_suspicion),
        ("권위 시선", lambda ws: ws.authority_vigilance),
        ("자원 압력", lambda ws: ws.scarcity_pressure),
    ]:
        first_val = getter(first_ws)
        last_val = getter(last_ws)
        peak_val = max(getter(ws) for _, ws in trace)
        metric_changes.append((metric_name, last_val - first_val, peak_val))

    # 가장 큰 absolute delta 또는 peak
    biggest = max(metric_changes, key=lambda mc: max(abs(mc[1]), mc[2]))
    name, delta, peak = biggest
    if peak > 0.3:
        lines.append(
            f"{name}은(는) 최고 {peak:.2f}까지 올랐고, 이 구간에서 {_delta_word(delta)}."
        )

    # Active events
    snapshots = [observer._tick_index[t] for t, _ in trace]
    all_events: set[str] = set()
    for s in snapshots:
        all_events.update(s.active_events)
    if all_events:
        ev_list = ", ".join(sorted(all_events))
        lines.append(f"이 구간에 {ev_list} 이벤트가 활성이었다.")

    # Salience count
    moments = top_salient_moments(snapshots, top_n=100)
    if moments:
        lines.append(f"주목할 만한 순간이 {len(moments)}개 감지되었다.")
    else:
        lines.append("주목할 만한 변동은 감지되지 않았다.")

    return " ".join(lines)


# ============================================================
# 2. Person Arc Narrator
# ============================================================


def narrate_person_arc(
    observer: Observer,
    agent_id: str,
    tick_from: int | None = None,
    tick_to: int | None = None,
) -> str:
    """One agent's state arc를 prose로 묘사."""
    arc = observer.get_person_arc(agent_id, tick_from, tick_to)
    if not arc:
        return f"{agent_id}는 이 구간에 등장하지 않는다."

    first_tick, first_a = arc[0]
    last_tick, last_a = arc[-1]

    lines: list[str] = []
    lines.append(
        f"{agent_id} ({first_a.role})의 흐름은 tick {first_tick}부터 {last_tick}까지다."
    )

    # Fear / Hope / Shame_self trajectory
    metric_changes: list[tuple[str, float, float]] = []
    for name, get_first, get_last, get_peak in [
        (
            "두려움",
            first_a.fear,
            last_a.fear,
            max(a.fear for _, a in arc),
        ),
        (
            "희망",
            first_a.hope,
            last_a.hope,
            max(a.hope for _, a in arc),
        ),
        (
            "자기 수치",
            first_a.shame_self,
            last_a.shame_self,
            max(a.shame_self for _, a in arc),
        ),
    ]:
        metric_changes.append((name, get_last - get_first, get_peak))

    # 가장 큰 변화 1개 묘사
    biggest = max(metric_changes, key=lambda mc: abs(mc[1]))
    name, delta, peak = biggest
    if abs(delta) > 1.0:
        direction = "올랐다" if delta > 0 else "내렸다"
        lines.append(
            f"{name}은(는) {first_tick} 시점 대비 {abs(delta):.1f} 단위 {direction}. "
            f"최고치는 {peak:.1f}/10이었다."
        )
    else:
        lines.append(
            f"세 감정 모두 큰 변화 없이 안정적으로 흘렀다. "
            f"두려움 최고 {first_a.fear:.1f}~{max(a.fear for _, a in arc):.1f}/10."
        )

    # Delta tags 카운트
    shift_ticks = [t for t, a in arc if a.delta]
    if shift_ticks:
        if len(shift_ticks) == 1:
            lines.append(f"tick {shift_ticks[0]}에 상태 변화가 한 번 감지되었다.")
        else:
            lines.append(
                f"상태 변화가 감지된 tick은 {len(shift_ticks)}개 ({shift_ticks[0]}~{shift_ticks[-1]} 범위)다."
            )

    return " ".join(lines)


# ============================================================
# 3. Event Ripple Narrator
# ============================================================


def narrate_event_ripple(observer: Observer, event_id: str) -> str:
    """Event ripple을 prose로 묘사."""
    ev = observer.get_event_view(event_id)

    if not ev["active_ticks"]:
        return f"{event_id} 이벤트는 어떤 tick에서도 활성화되지 않았다."

    first_tick = ev["first_tick"]
    last_tick = ev["last_tick"]
    span = len(ev["active_ticks"])
    n_agents = len(ev["agent_ids_present"])

    lines: list[str] = []
    if first_tick == last_tick:
        lines.append(f"{event_id} 이벤트는 tick {first_tick}에서 단발적으로 활성되었다.")
    else:
        lines.append(
            f"{event_id} 이벤트는 tick {first_tick}부터 {last_tick}까지 "
            f"총 {span}개 tick 동안 활성이었다."
        )

    if n_agents > 0:
        if n_agents <= 3:
            agent_list = ", ".join(ev["agent_ids_present"])
            lines.append(f"활성 동안 {n_agents}명 ({agent_list})이 등장했다.")
        else:
            lines.append(f"활성 동안 {n_agents}명이 등장했다.")

    return " ".join(lines)


# ============================================================
# 4. Seed Comparison Narrator
# ============================================================


def narrate_seed_comparison(streams: dict[str, Observer]) -> str:
    """Multi-stream comparison을 prose로 묘사.

    *대조 표시*만, *어느 stream이 더 좋다는 평가 안 함*.
    """
    if not streams:
        return "비교할 stream이 제공되지 않았다."
    if len(streams) == 1:
        only_label = next(iter(streams))
        return f"{only_label} 단일 stream만 제공되어 비교가 의미 없다."

    # peak_blame ranges
    peak_blames: dict[str, float] = {}
    final_moods: dict[str, str] = {}
    salient_counts: dict[str, int] = {}

    for label, obs in streams.items():
        ticks = obs.list_ticks()
        snaps = [obs._tick_index[t] for t in ticks]
        peak_blames[label] = max(s.world.blame_concentration for s in snaps)
        final_moods[label] = snaps[-1].world.crowd_mood
        salient_counts[label] = len(top_salient_moments(snaps, top_n=100))

    # Find max/min by peak_blame
    max_label = max(peak_blames, key=lambda k: peak_blames[k])
    min_label = min(peak_blames, key=lambda k: peak_blames[k])

    lines: list[str] = []
    lines.append(f"{len(streams)}개 stream을 비교한다.")

    if max_label != min_label:
        lines.append(
            f"비난 집중도는 {min_label}({peak_blames[min_label]:.2f})에서 "
            f"{max_label}({peak_blames[max_label]:.2f})까지 분포한다."
        )

    # Final mood diversity
    unique_moods = set(final_moods.values())
    if len(unique_moods) == 1:
        only = next(iter(unique_moods))
        only_ko = _MOOD_NOUN_KO.get(only, only)
        lines.append(f"최종 군중 분위기는 모든 stream에서 {only_ko}으로 동일하다.")
    else:
        mood_groups: dict[str, list[str]] = {}
        for label, mood in final_moods.items():
            mood_groups.setdefault(mood, []).append(label)
        parts = [
            f"{', '.join(labels)}: {_MOOD_NOUN_KO.get(mood, mood)}"
            for mood, labels in mood_groups.items()
        ]
        lines.append(f"최종 군중 분위기는 stream별로 갈렸다 — {' / '.join(parts)}.")

    # Salient count range
    max_salient = max(salient_counts.values())
    min_salient = min(salient_counts.values())
    if max_salient != min_salient:
        max_s_label = max(salient_counts, key=lambda k: salient_counts[k])
        lines.append(
            f"주목할 만한 순간 수는 {min_salient}~{max_salient} 범위 "
            f"({max_s_label}이 가장 많음)."
        )

    lines.append("(비교는 대조 표시일 뿐, 어느 stream이 더 낫다는 평가 아님.)")

    return " ".join(lines)
