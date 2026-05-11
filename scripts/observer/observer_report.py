"""World Observer — Text Report Generator (Phase O3).

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §6.

관찰자 출력은 *텍스트 기반*. 4 lens 각각의 상태를 사람이 빠르게 훑을 수
있는 형태로 변환.

ABSOLUTE Rule #1: no person hardcoding. report는 generic schema 그대로 출력.
원칙: 관찰기 ≠ 평가기. "이게 좋다/나쁘다" 같은 평가 단어 금지.

Usage:
    from engine.observer.core import Observer
    from scripts.observer.observer_report import (
        format_world_view, format_person_view, format_salience_summary
    )
    obs = Observer(snapshots)
    print(format_world_view(obs, tick=10))
    print(format_salience_summary(obs))
"""

from __future__ import annotations

from engine.observer.core import Observer
from engine.observer.salience import (
    top_salient_moments,
    top_unstable_agents,
)

# ============================================================
# Categorical → Korean tag (관측 태그만, 평가 아님)
# ============================================================

_CROWD_MOOD_KO: dict[str, str] = {
    "calm": "고요",
    "tense": "긴장",
    "agitated": "동요",
    "fragmenting": "분열",
}

_DOMINANT_MODE_KO: dict[str, str] = {
    "saturation": "고착",
    "recovery": "회복",
    "mixed": "분기",
    "low_activity": "정적",
    "partial": "부분",
}


# ============================================================
# Helpers
# ============================================================


def _intensity_bar(value: float, width: int = 10) -> str:
    """0.0-1.0 값을 막대로 시각화. 평가 아님, *값 표시*."""
    if value < 0.0:
        value = 0.0
    if value > 1.0:
        value = 1.0
    filled = int(round(value * width))
    return "█" * filled + "·" * (width - filled)


def _intensity_bar_10(value: float, width: int = 10) -> str:
    """0.0-10.0 값 (agent state)을 막대로 시각화."""
    return _intensity_bar(value / 10.0, width)


# ============================================================
# Lens 1 — World View
# ============================================================


def format_world_view(observer: Observer, tick: int) -> str:
    """Format world-level state at one tick.

    Returns multi-line text report.
    """
    try:
        ws = observer.get_world_view(tick)
    except KeyError:
        return f"[World View] tick {tick} not in snapshot stream."
    snap = observer._tick_index[tick]  # internal access OK for report
    mood_ko = _CROWD_MOOD_KO.get(ws.crowd_mood, ws.crowd_mood)
    lines = [
        f"=== World View — tick {tick} ===",
        f"Crowd mood:          {mood_ko} ({ws.crowd_mood})",
        f"Blame concentration: {_intensity_bar(ws.blame_concentration)} {ws.blame_concentration:.2f}",
        f"Public suspicion:    {_intensity_bar(ws.public_suspicion)} {ws.public_suspicion:.2f}",
        f"Authority vigilance: {_intensity_bar(ws.authority_vigilance)} {ws.authority_vigilance:.2f}",
        f"Scarcity pressure:   {_intensity_bar(ws.scarcity_pressure)} {ws.scarcity_pressure:.2f}",
    ]
    if snap.active_events:
        lines.append(f"Active events:       {', '.join(snap.active_events)}")
    else:
        lines.append("Active events:       (none)")
    if snap.salience_hints:
        lines.append(f"Salience hints:      {', '.join(snap.salience_hints)}")
    return "\n".join(lines)


def format_world_trace(
    observer: Observer,
    tick_from: int | None = None,
    tick_to: int | None = None,
) -> str:
    """Compact world trace across window — one line per tick."""
    trace = observer.get_world_trace(tick_from, tick_to)
    if not trace:
        return "[World Trace] no ticks in window."
    lines = [f"=== World Trace — ticks {trace[0][0]} → {trace[-1][0]} ==="]
    lines.append(
        f"{'tick':>5}  mood       blame  susp   vigil  scarc"
    )
    for t, ws in trace:
        mood_short = ws.crowd_mood[:8].ljust(10)
        lines.append(
            f"{t:>5}  {mood_short} "
            f"{ws.blame_concentration:.2f}   "
            f"{ws.public_suspicion:.2f}   "
            f"{ws.authority_vigilance:.2f}   "
            f"{ws.scarcity_pressure:.2f}"
        )
    return "\n".join(lines)


# ============================================================
# Lens 2 — Person View
# ============================================================


def format_person_view(
    observer: Observer, agent_id: str, tick: int
) -> str:
    """Format one agent's state at one tick."""
    a = observer.get_person_view(agent_id, tick)
    if a is None:
        return f"[Person View] agent '{agent_id}' not present at tick {tick}."
    lines = [
        f"=== Person View — {agent_id} (role: {a.role}) — tick {tick} ===",
        f"Fear:       {_intensity_bar_10(a.fear)} {a.fear:.1f}/10",
        f"Hope:       {_intensity_bar_10(a.hope)} {a.hope:.1f}/10",
        f"Shame_self: {_intensity_bar_10(a.shame_self)} {a.shame_self:.1f}/10",
    ]
    if a.delta:
        lines.append(f"Delta tags: {', '.join(a.delta)}")
    else:
        lines.append("Delta tags: (no tick-over-tick shift)")
    return "\n".join(lines)


def format_person_arc(
    observer: Observer,
    agent_id: str,
    tick_from: int | None = None,
    tick_to: int | None = None,
) -> str:
    """Format agent's arc across window — compact line per present tick."""
    arc = observer.get_person_arc(agent_id, tick_from, tick_to)
    if not arc:
        return f"[Person Arc] '{agent_id}' not present in window."
    lines = [
        f"=== Person Arc — {agent_id} ===",
        f"{'tick':>5}  fear  hope  shame_self  delta",
    ]
    for t, a in arc:
        delta_short = ", ".join(a.delta) if a.delta else "(stable)"
        lines.append(
            f"{t:>5}  {a.fear:.1f}   {a.hope:.1f}   "
            f"{a.shame_self:.1f}         {delta_short}"
        )
    return "\n".join(lines)


# ============================================================
# Lens 3 — Group View
# ============================================================


def format_group_view(
    observer: Observer, group_id: str, tick: int
) -> str:
    """Format one group's state at one tick."""
    g = observer.get_group_view(group_id, tick)
    if g is None:
        return f"[Group View] group '{group_id}' not present at tick {tick}."
    mode_ko = _DOMINANT_MODE_KO.get(g.dominant_mode, g.dominant_mode)
    lines = [
        f"=== Group View — {group_id} — tick {tick} ===",
        f"Dominant mode: {mode_ko} ({g.dominant_mode})",
        f"Tension:       {_intensity_bar(g.tension)} {g.tension:.2f}",
        f"Member count:  {g.member_count}",
    ]
    return "\n".join(lines)


def format_group_arc(
    observer: Observer,
    group_id: str,
    tick_from: int | None = None,
    tick_to: int | None = None,
) -> str:
    """Format group's arc across window."""
    arc = observer.get_group_arc(group_id, tick_from, tick_to)
    if not arc:
        return f"[Group Arc] '{group_id}' not present in window."
    lines = [
        f"=== Group Arc — {group_id} ===",
        f"{'tick':>5}  mode         tension  members",
    ]
    for t, g in arc:
        mode_short = g.dominant_mode[:12].ljust(12)
        lines.append(
            f"{t:>5}  {mode_short} {g.tension:.2f}     {g.member_count}"
        )
    return "\n".join(lines)


# ============================================================
# Lens 4 — Event View
# ============================================================


def format_event_view(observer: Observer, event_id: str) -> str:
    """Format event ripple."""
    ev = observer.get_event_view(event_id)
    if not ev["active_ticks"]:
        return f"[Event View] '{event_id}' not active in any tick."
    lines = [
        f"=== Event View — {event_id} ===",
        f"First tick: {ev['first_tick']}",
        f"Last tick:  {ev['last_tick']}",
        f"Span:       {len(ev['active_ticks'])} ticks",
        f"Agents present during span: {len(ev['agent_ids_present'])}",
    ]
    if ev["agent_ids_present"]:
        agent_list = ", ".join(ev["agent_ids_present"][:10])
        if len(ev["agent_ids_present"]) > 10:
            agent_list += f", ... (+{len(ev['agent_ids_present']) - 10} more)"
        lines.append(f"  → {agent_list}")
    return "\n".join(lines)


# ============================================================
# Salience summaries
# ============================================================


def format_salience_summary(
    observer: Observer,
    tick_from: int | None = None,
    tick_to: int | None = None,
    top_n: int = 5,
) -> str:
    """Top-N salient moments summary.

    Salience = *attention pointer*, NOT quality verdict.
    """
    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    moments = top_salient_moments(snapshots, tick_from, tick_to, top_n=top_n)
    if not moments:
        return "[Salience Summary] no salient moments in window."
    lines = [f"=== Top {len(moments)} Salient Moments ==="]
    for i, m in enumerate(moments, 1):
        tags_str = ", ".join(m["tags"])
        lines.append(f"  {i}. tick {m['tick']:>4}  (score={m['score']})  [{tags_str}]")
    lines.append("")
    lines.append("(Salience = attention pointer, not quality verdict)")
    return "\n".join(lines)


def format_unstable_agents_summary(
    observer: Observer,
    tick_from: int | None = None,
    tick_to: int | None = None,
    top_n: int = 3,
) -> str:
    """Top-N agents with most state-shift moments."""
    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    ranked = top_unstable_agents(snapshots, tick_from, tick_to, top_n=top_n)
    if not ranked:
        return "[Unstable Agents] no agents with state shifts in window."
    lines = [f"=== Top {len(ranked)} Unstable Agents ==="]
    for i, r in enumerate(ranked, 1):
        ticks_str = ", ".join(str(t) for t in r["ticks_with_shift"][:5])
        if len(r["ticks_with_shift"]) > 5:
            ticks_str += f", ... (+{len(r['ticks_with_shift']) - 5} more)"
        lines.append(
            f"  {i}. {r['agent_id']:>12}  shifts={r['score']}  [ticks: {ticks_str}]"
        )
    return "\n".join(lines)


# ============================================================
# Composite report
# ============================================================


def format_full_report(
    observer: Observer,
    tick: int | None = None,
) -> str:
    """One-shot full report at given tick (default: middle tick).

    Includes World view + Salience summary + Unstable agents.
    """
    if tick is None:
        ticks = observer.list_ticks()
        tick = ticks[len(ticks) // 2]
    sections = [
        format_world_view(observer, tick),
        "",
        format_salience_summary(observer),
        "",
        format_unstable_agents_summary(observer),
    ]
    return "\n".join(sections)
