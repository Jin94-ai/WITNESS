"""World Observer — Multi-lens Compare (Phase O5).

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` §4.6 + Phase O5.

복수 stream / 복수 lens 비교:
- same anchor, different seeds
- same scenario, different outcomes
- person view vs world view (same tick)
- same tick: world vs person vs event aggregated

ABSOLUTE Rule #1: no person hardcoding.
원칙: 비교는 *대조 표시*만. 어느 stream/seed가 "더 좋다"는 평가 안 함.

Usage:
    from engine.observer.core import Observer
    from scripts.observer.compare_views import compare_seeds, format_seed_comparison

    obs1 = Observer(snapshots_seed_0)
    obs2 = Observer(snapshots_seed_1)
    obs3 = Observer(snapshots_seed_2)
    print(format_seed_comparison({"seed_0": obs1, "seed_1": obs2, "seed_2": obs3}))
"""

from __future__ import annotations

from typing import Any

from engine.observer.core import Observer
from engine.observer.salience import top_salient_moments

# ============================================================
# Stream-level summary
# ============================================================


def stream_summary(observer: Observer) -> dict[str, Any]:
    """One stream's compact summary (for comparison row).

    Returns dict:
        tick_range: (min, max)
        n_ticks: int
        n_agents: int
        n_groups: int
        events_seen: list[str]
        peak_blame: float (max world.blame_concentration across stream)
        peak_suspicion: float
        final_crowd_mood: str
        salient_moments_count: int
    """
    ticks = observer.list_ticks()
    if not ticks:
        return {}
    snapshots = [observer._tick_index[t] for t in ticks]

    peak_blame = max(s.world.blame_concentration for s in snapshots)
    peak_suspicion = max(s.world.public_suspicion for s in snapshots)
    peak_authority = max(s.world.authority_vigilance for s in snapshots)
    peak_scarcity = max(s.world.scarcity_pressure for s in snapshots)
    final_mood = snapshots[-1].world.crowd_mood

    moments = top_salient_moments(snapshots, top_n=100)  # all salient

    return {
        "tick_range": observer.tick_range,
        "n_ticks": len(ticks),
        "n_agents": len(observer.list_agents()),
        "n_groups": len(observer.list_groups()),
        "events_seen": observer.list_events(),
        "peak_blame": peak_blame,
        "peak_suspicion": peak_suspicion,
        "peak_authority": peak_authority,
        "peak_scarcity": peak_scarcity,
        "final_crowd_mood": final_mood,
        "salient_moments_count": len(moments),
    }


# ============================================================
# Compare multiple streams (e.g., seeds of same anchor)
# ============================================================


def compare_seeds(
    streams: dict[str, Observer],
) -> dict[str, dict[str, Any]]:
    """Compare multiple Observer streams (e.g., 5 seeds of same anchor).

    Args:
        streams: {label: Observer}

    Returns:
        {label: stream_summary_dict}
    """
    return {label: stream_summary(obs) for label, obs in streams.items()}


def format_seed_comparison(streams: dict[str, Observer]) -> str:
    """Text table comparing N streams side-by-side."""
    if not streams:
        return "[Seed Comparison] no streams provided."
    summaries = compare_seeds(streams)
    labels = list(summaries.keys())

    lines = [
        f"=== Stream Comparison ({len(labels)} streams) ===",
        "",
        f"{'metric':<24}  " + "  ".join(f"{label:>14}" for label in labels),
        "-" * (26 + 16 * len(labels)),
    ]

    rows: list[tuple[str, str]] = [
        ("n_ticks", "n_ticks"),
        ("n_agents", "n_agents"),
        ("n_groups", "n_groups"),
        ("peak_blame", "peak_blame"),
        ("peak_suspicion", "peak_suspicion"),
        ("peak_authority", "peak_authority"),
        ("peak_scarcity", "peak_scarcity"),
        ("final_crowd_mood", "final_crowd_mood"),
        ("salient_moments", "salient_moments_count"),
    ]

    for display, key in rows:
        cells = []
        for label in labels:
            val = summaries[label].get(key, "-")
            if isinstance(val, float):
                cell = f"{val:.2f}"
            else:
                cell = str(val)
            cells.append(f"{cell:>14}")
        lines.append(f"{display:<24}  " + "  ".join(cells))

    lines.append("")
    lines.append("(Comparison = contrast display, not quality verdict)")
    return "\n".join(lines)


# ============================================================
# Same tick — multi-lens
# ============================================================


def multi_lens_at_tick(
    observer: Observer,
    tick: int,
    agent_ids: list[str] | None = None,
    group_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Same tick from multiple lenses simultaneously.

    Args:
        observer: stream
        tick: target tick
        agent_ids: list of agent IDs to include in person view (None = all)
        group_ids: list of group IDs to include in group view (None = all)

    Returns dict:
        tick: int
        world: WorldSnapshot
        active_events: list[str]
        salience_hints: list[str]
        agents: {agent_id: AgentSnapshot}
        groups: {group_id: GroupSnapshot}
    """
    snap = observer._tick_index[tick]
    if agent_ids is None:
        agents_view = {a.id: a for a in snap.agents}
    else:
        agents_view = {
            aid: a for a in snap.agents if (aid := a.id) in agent_ids
        }
    if group_ids is None:
        groups_view = {g.id: g for g in snap.groups}
    else:
        groups_view = {
            gid: g for g in snap.groups if (gid := g.id) in group_ids
        }
    return {
        "tick": tick,
        "world": snap.world,
        "active_events": list(snap.active_events),
        "salience_hints": list(snap.salience_hints),
        "agents": agents_view,
        "groups": groups_view,
    }


def format_multi_lens_at_tick(
    observer: Observer,
    tick: int,
    agent_ids: list[str] | None = None,
    group_ids: list[str] | None = None,
) -> str:
    """Format multi-lens snapshot at one tick."""
    data = multi_lens_at_tick(observer, tick, agent_ids, group_ids)
    lines = [f"=== Multi-lens — tick {tick} ==="]

    # World
    w = data["world"]
    lines.append("")
    lines.append("[World]")
    lines.append(
        f"  mood={w.crowd_mood}  blame={w.blame_concentration:.2f}  "
        f"suspicion={w.public_suspicion:.2f}  scarcity={w.scarcity_pressure:.2f}"
    )

    # Events / salience
    if data["active_events"]:
        lines.append(f"  active_events: {', '.join(data['active_events'])}")
    if data["salience_hints"]:
        lines.append(f"  salience: {', '.join(data['salience_hints'])}")

    # Groups
    if data["groups"]:
        lines.append("")
        lines.append(f"[Groups] ({len(data['groups'])})")
        for gid, g in data["groups"].items():
            lines.append(
                f"  {gid:<12} mode={g.dominant_mode:<12} tension={g.tension:.2f} members={g.member_count}"
            )

    # Agents
    if data["agents"]:
        lines.append("")
        lines.append(f"[Agents] ({len(data['agents'])})")
        for aid, a in data["agents"].items():
            delta_str = f" delta=[{', '.join(a.delta)}]" if a.delta else ""
            lines.append(
                f"  {aid:<12} role={a.role:<12} fear={a.fear:.1f} hope={a.hope:.1f} shame={a.shame_self:.1f}{delta_str}"
            )

    return "\n".join(lines)
