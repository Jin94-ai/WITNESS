"""Demo: World Observer Layer — single entry point.

Per `docs/observer/WORLD_OBSERVER_LAYER_SPEC.md` MVP.

Usage:
    python examples/demo_observer.py                # 기본 (full demo + report)
    python examples/demo_observer.py --status       # Observer Layer 진행 상태
    python examples/demo_observer.py --views        # 4 lens demo only
    python examples/demo_observer.py --replay       # ReplayCursor + bookmark demo
    python examples/demo_observer.py --compare      # multi-stream comparison demo
    python examples/demo_observer.py --narrate      # Narrative summaries (prose)
    python examples/demo_observer.py --real         # Real run validation (Peter scarcity baseline canonical)

Synthetic snapshot stream (built in this demo) — 14 ticks × 3 agents × 2 groups
+ 1 event ripple. 관찰기 ≠ 평가기 원칙 보존.

Real run mode (--real) — Lee directive `WITNESS_NEXT_STEP_OBSERVER_REAL_RUN_VALIDATION.md`:
peter_scarcity_baseline anchor (J-Beta selector) → MicroWorld 200 ticks →
WorldStep history → Snapshot stream → Observer 4 lens + salience + replay + compare.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Force UTF-8 stdout (Windows cp949 fallback breaks Korean + em-dash)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass

from engine.observer.core import Observer  # noqa: E402
from engine.observer.recorder import SnapshotStream  # noqa: E402
from engine.observer.replay import ReplayCursor, auto_bookmark_turning_points  # noqa: E402
from scripts.observer.compare_views import (  # noqa: E402
    format_multi_lens_at_tick,
    format_seed_comparison,
)
from scripts.observer.narrative_summary import (  # noqa: E402
    narrate_event_ripple,
    narrate_person_arc,
    narrate_seed_comparison,
    narrate_world_arc,
)
from scripts.observer.observer_report import (  # noqa: E402
    format_event_view,
    format_full_report,
    format_group_arc,
    format_person_arc,
    format_salience_summary,
    format_world_trace,
    format_world_view,
)

# ============================================================
# Synthetic stream builders
# ============================================================


def build_synthetic_stream(seed_label: str = "seed_0") -> Observer:
    """Build a 14-tick synthetic stream representing accusation arc.

    Story arc:
    - Tick 0-2: calm baseline
    - Tick 3: public_accusation event fires
    - Tick 4-7: blame concentration spikes, group L1 saturates, L2 mixes
    - Tick 8: turning point (L1 starts recovery)
    - Tick 9-13: gradual recovery, blame fades

    seed_label affects peak intensity (different seeds yield different streams).
    """
    if seed_label == "seed_0":
        peak_blame = 0.85
        l1_recover_tick = 8
    elif seed_label == "seed_1":
        peak_blame = 0.65
        l1_recover_tick = 10  # slower recovery
    elif seed_label == "seed_2":
        peak_blame = 0.95
        l1_recover_tick = None  # no recovery (saturation lock)
    else:
        peak_blame = 0.7
        l1_recover_tick = 9

    stream = SnapshotStream()

    for t in range(14):
        # World state evolves
        if t < 3:
            mood = "calm"
            blame = 0.0
            suspicion = 0.0
        elif t == 3:
            mood = "tense"
            blame = peak_blame * 0.5
            suspicion = 0.3
        elif t < 8:
            mood = "agitated"
            blame = peak_blame
            suspicion = 0.6
        elif l1_recover_tick is not None and t >= l1_recover_tick:
            # Recovery phase
            mood = "tense" if t < 11 else "calm"
            blame = max(0.0, peak_blame - 0.15 * (t - l1_recover_tick + 1))
            suspicion = max(0.0, 0.6 - 0.1 * (t - l1_recover_tick + 1))
        else:
            # Continued saturation
            mood = "agitated"
            blame = peak_blame
            suspicion = 0.6

        # L1 group dominant mode
        if t < 4:
            l1_mode = "low_activity"
            l1_tension = 0.1
        elif l1_recover_tick is not None and t >= l1_recover_tick:
            l1_mode = "recovery"
            l1_tension = max(0.1, 0.8 - 0.15 * (t - l1_recover_tick + 1))
        else:
            l1_mode = "saturation"
            l1_tension = min(0.95, 0.5 + 0.05 * (t - 3))

        # L2 group always more mixed
        if t < 3:
            l2_mode = "low_activity"
            l2_tension = 0.1
        elif t < 9:
            l2_mode = "mixed"
            l2_tension = 0.5
        else:
            l2_mode = "recovery"
            l2_tension = max(0.0, 0.5 - 0.1 * (t - 8))

        # Agent states
        a1_fear = min(9.0, 2.0 + 0.8 * max(0, t - 2))
        if l1_recover_tick is not None and t >= l1_recover_tick:
            a1_fear = max(2.0, a1_fear - 1.0 * (t - l1_recover_tick + 1))
        a2_fear = 3.0 + (1.5 if 3 <= t <= 7 else 0.0)
        a3_fear = 2.0 + (0.5 if 4 <= t <= 8 else 0.0)

        active_events = ["public_accusation"] if 3 <= t <= 7 else []

        stream.append_from_stats(
            tick=t,
            active_events=active_events,
            world_stats={
                "crowd_mood": mood,
                "blame_concentration": blame,
                "public_suspicion": suspicion,
                "authority_vigilance": 0.3 if 4 <= t <= 9 else 0.1,
                "scarcity_pressure": 0.0,
            },
            group_stats_list=[
                {
                    "id": "L1",
                    "dominant_mode": l1_mode,
                    "tension": l1_tension,
                    "member_count": 4,
                },
                {
                    "id": "L2",
                    "dominant_mode": l2_mode,
                    "tension": l2_tension,
                    "member_count": 3,
                },
            ],
            agent_stats_list=[
                {"id": "agent_001", "role": "follower", "fear": a1_fear, "hope": 5.0, "shame_self": 2.0},
                {"id": "agent_002", "role": "crowd", "fear": a2_fear, "hope": 4.0, "shame_self": 1.0},
                {"id": "agent_003", "role": "authority", "fear": a3_fear, "hope": 6.0, "shame_self": 0.5},
            ],
        )

    return Observer(stream.snapshots)


# ============================================================
# Commands
# ============================================================


def cmd_status() -> int:
    print("=" * 70)
    print("WITNESS World Observer Layer — Status (2026-04-30)")
    print("=" * 70)
    print()
    print("Phase O1-O5 MVP: complete (Lee directive 2026-04-30)")
    print()
    print("Components:")
    print("  engine/observer/")
    print("    snapshot_schema.py   — 4 Pydantic models (Snapshot/World/Group/Agent)")
    print("    recorder.py          — record_snapshot + SnapshotStream")
    print("    core.py              — Observer class (4 lens API + listing)")
    print("    salience.py          — 8 tag types + top-N moments/agents")
    print("    replay.py            — ReplayCursor + auto_bookmark + window helpers")
    print("  scripts/observer/")
    print("    observer_report.py   — 11 text format functions")
    print("    compare_views.py     — stream_summary + compare_seeds + multi_lens")
    print()
    print("Tests: 179 PASS (test_observer — 130 base + 35 Pipeline + 14 adapter)")
    print("Engine integrity: observer code violations 0")
    print()
    print("Principles (Lee directive §6):")
    print("  - 관찰기 != 평가기 (no quality verdict)")
    print("  - 여러 렌즈 제공, 하나를 정답으로 고정 안 함")
    print("  - 해석보다 *탐색 가능성*")
    print()
    print("Demo modes: --views / --replay / --compare / (default = full)")
    return 0


def cmd_views() -> int:
    """4 lens demo on synthetic stream."""
    obs = build_synthetic_stream()
    print("=" * 70)
    print("DEMO — 4 Lens Views on synthetic 14-tick stream")
    print("=" * 70)
    print()

    # Lens 1 — World View at peak
    print(format_world_view(obs, tick=5))
    print()

    # Lens 1b — World trace (compact)
    print(format_world_trace(obs, tick_from=2, tick_to=10))
    print()

    # Lens 2 — Person arc
    print(format_person_arc(obs, "agent_001"))
    print()

    # Lens 3 — Group arc
    print(format_group_arc(obs, "L1"))
    print()

    # Lens 4 — Event view
    print(format_event_view(obs, "public_accusation"))
    print()

    return 0


def cmd_replay() -> int:
    """ReplayCursor + bookmark demo."""
    obs = build_synthetic_stream()
    print("=" * 70)
    print("DEMO — ReplayCursor + auto_bookmark on synthetic stream")
    print("=" * 70)
    print()

    cursor = ReplayCursor(obs)
    print(f"Initial cursor position: tick {cursor.current_tick}")

    # Jump to event start
    cursor.jump_to_event_start("public_accusation")
    print(f"Jump to event start ('public_accusation'): tick {cursor.current_tick}")

    # Auto-bookmark turning points
    bookmarks = auto_bookmark_turning_points(cursor)
    print(f"\nAuto-bookmarked turning points: {len(bookmarks)} markers")
    for name, tick in bookmarks.items():
        print(f"  {name:<40} tick {tick}")

    # Demonstrate jump to bookmark
    if "first_recovery_turning_point" in bookmarks:
        cursor.jump_to_bookmark("first_recovery_turning_point")
        print(f"\nJump to recovery turning point: tick {cursor.current_tick}")
        snap = cursor.current()
        print(
            f"  World: mood={snap.world.crowd_mood} blame={snap.world.blame_concentration:.2f}"
        )

    # Advance / before-after
    print(f"\nAdvance 3 ticks: {cursor.advance(3)}")
    print(f"Backward 5 ticks: {cursor.advance(-5)}")

    return 0


def cmd_compare() -> int:
    """Multi-stream comparison demo."""
    print("=" * 70)
    print("DEMO — Multi-stream Comparison (3 seeds)")
    print("=" * 70)
    print()

    obs_seeds = {
        "seed_0_recover": build_synthetic_stream("seed_0"),
        "seed_1_slow": build_synthetic_stream("seed_1"),
        "seed_2_locked": build_synthetic_stream("seed_2"),
    }

    print(format_seed_comparison(obs_seeds))
    print()

    print("=" * 70)
    print("DEMO — Multi-lens at single tick (seed_0, tick 5)")
    print("=" * 70)
    print()
    print(format_multi_lens_at_tick(obs_seeds["seed_0_recover"], tick=5))
    print()

    return 0


# ============================================================
# Real run mode — peter_scarcity_baseline canonical
# ============================================================


def _classify_arc(peak: float, final_mean: float) -> str:
    """Cohort arc classification — same as generate_scarcity_depth_variations.py."""
    if peak < 1.5:
        return "low_activity"
    if final_mean < 4 and peak >= 5:
        return "recovery"
    if final_mean >= 7:
        return "saturation"
    return "partial"


def _classify_crowd_mood(blame_sum: float) -> str:
    """Map blame_concentration sum → categorical crowd_mood."""
    if blame_sum < 0.1:
        return "calm"
    if blame_sum < 0.5:
        return "tense"
    if blame_sum < 1.5:
        return "agitated"
    return "fragmenting"


def build_real_stream_from_anchor(
    anchor_id: str = "peter_scarcity_baseline",
    seed: int = 0,
    n_ticks: int = 200,
) -> Observer:
    """Build Observer from real MicroWorld run (J-Beta selector anchor).

    Per Lee directive `WITNESS_NEXT_STEP_OBSERVER_REAL_RUN_VALIDATION.md` §4.2:
    canonical run = peter_scarcity_baseline (scarcity, single accusation, baseline density).

    Maps WorldStep history → Snapshot stream:
    - WorldSnapshot: crowd blame_sum / public_suspicion / authority_vigilance / scarcity_pressure (=0, not modeled)
    - GroupSnapshot per crowd: id / dominant_mode (cohort arc) / tension / member_count
    - AgentSnapshot per agent: fear / hope / shame_self (+ delta vs prev tick)
    - active_events: from spawned_events
    """
    # Lazy import to avoid heavy module load at top
    from collections import defaultdict

    from scripts.story.selector import get_anchor_by_id

    anchor = get_anchor_by_id(anchor_id)
    if anchor is None:
        raise ValueError(f"Unknown anchor_id: {anchor_id}")

    world = anchor.builder(seed)

    # Track per-tick agent shame for cohort arc post-hoc classification
    per_agent_shame: dict[str, list[float]] = defaultdict(list)
    # Cohort = location grouping
    cohort_groups: dict[str, list[str]] = defaultdict(list)
    for aid in world._agents:
        loc = world._spatial.where(aid)
        if loc is not None:
            cohort_groups[loc].append(aid)
    location_anon = {
        loc_id: f"L{i+1}"
        for i, loc_id in enumerate(world._spatial._locations.keys())
    }

    stream = SnapshotStream()

    for tick_offset in range(n_ticks):
        result = world.step()
        tick = world._tick  # 1-indexed in MicroWorld

        # Agent shame trace for cohort classification (running)
        for aid, agent in world._agents.items():
            shame_pg = agent.state.get("shame", {}).get("public_group", 0.0)
            per_agent_shame[aid].append(shame_pg)

        # World stats
        crowd_blame_sum = sum(
            sum(c.blame_concentration.values()) for c in world._crowds.values()
        )
        public_suspicion = sum(c.public_suspicion for c in world._crowds.values())
        authority_vigilance = sum(
            c.authority_vigilance for c in world._crowds.values()
        )
        # Normalize to 0-1 (heuristic — divide by 3.0 cap for blame, 1.0 for others)
        world_stats = {
            "crowd_mood": _classify_crowd_mood(crowd_blame_sum),
            "blame_concentration": min(1.0, crowd_blame_sum / 3.0),
            "public_suspicion": min(1.0, public_suspicion),
            "authority_vigilance": min(1.0, authority_vigilance),
            "scarcity_pressure": 0.0,  # not modeled in MicroWorld layer
        }

        # Group stats per crowd
        group_stats_list: list[dict] = []
        for loc_id, members in cohort_groups.items():
            # Cohort arc — running classification based on shame so far
            shames_so_far = [per_agent_shame[a] for a in members if per_agent_shame[a]]
            peaks = [max(s) for s in shames_so_far if s]
            finals = [s[-1] for s in shames_so_far if s]
            if peaks and finals:
                peak = max(peaks)
                final_mean = sum(finals) / len(finals)
                arc = _classify_arc(peak, final_mean)
            else:
                arc = "low_activity"
            # Tension = final_mean / 10.0 (normalized 0-1)
            tension = (sum(finals) / len(finals) / 10.0) if finals else 0.0
            group_stats_list.append({
                "id": location_anon.get(loc_id, loc_id),
                "dominant_mode": arc,
                "tension": min(1.0, tension),
                "member_count": len(members),
            })

        # Agent stats (use anonymized ID + role)
        agent_stats_list: list[dict] = []
        for aid, agent in world._agents.items():
            agent_stats_list.append({
                "id": aid,
                "role": agent.role_id,
                "fear": agent.state.get("fear", 0.0),
                "hope": agent.state.get("hope", 5.0),
                "shame_self": agent.state.get("shame", {}).get("public_group", 0.0),
            })

        # Active events
        active_events = [ev.get("event_id", "unknown") for ev in result.spawned_events]

        stream.append_from_stats(
            tick=tick,
            active_events=active_events,
            world_stats=world_stats,
            group_stats_list=group_stats_list,
            agent_stats_list=agent_stats_list,
        )

    return Observer(stream.snapshots)


def cmd_real() -> int:
    """Real run validation: peter_scarcity_baseline canonical → 4 view + salience + replay + compare."""
    print("=" * 70)
    print("DEMO — Real Run Validation: peter_scarcity_baseline (canonical)")
    print("=" * 70)
    print()
    print("Building real stream (200 ticks, seed=0)...")
    obs = build_real_stream_from_anchor(seed=0)
    print(f"Stream built: {len(obs.list_ticks())} ticks, "
          f"{len(obs.list_agents())} agents, "
          f"{len(obs.list_groups())} groups, "
          f"{len(obs.list_events())} unique events")
    print()

    # Salience first — find interesting ticks
    print("[Salience top 5]")
    print(format_salience_summary(obs, top_n=5))
    print()

    # World view at peak salient tick (or middle)
    moments = top_salient_moments_for(obs, top_n=1)
    peak_tick = moments[0]["tick"] if moments else obs.list_ticks()[len(obs.list_ticks()) // 2]
    print(f"[World View — peak salient tick {peak_tick}]")
    print(format_world_view(obs, tick=peak_tick))
    print()

    # World trace (compact, last 30 ticks)
    last_tick = obs.list_ticks()[-1]
    print("[World Trace — last 30 ticks]")
    print(format_world_trace(obs, tick_from=max(1, last_tick - 30), tick_to=last_tick))
    print()

    # Person view — pick first agent
    sample_agent = obs.list_agents()[0]
    print(f"[Person Arc — {sample_agent}]")
    print(format_person_arc(obs, sample_agent))
    print()

    # Group arc
    sample_group = obs.list_groups()[0] if obs.list_groups() else None
    if sample_group:
        print(f"[Group Arc — {sample_group}]")
        print(format_group_arc(obs, sample_group))
        print()

    # Event view — pick first event
    events = obs.list_events()
    if events:
        print(f"[Event View — {events[0]}]")
        print(format_event_view(obs, events[0]))
        print()

    # Narrative summaries
    print("[Narrative — World Arc]")
    print(narrate_world_arc(obs))
    print()
    print(f"[Narrative — Person Arc {sample_agent}]")
    print(narrate_person_arc(obs, sample_agent))
    print()

    # Replay/jump demo
    print("[Replay/Jump]")
    cursor = ReplayCursor(obs)
    bookmarks = auto_bookmark_turning_points(cursor)
    print(f"Auto-bookmarked turning points: {len(bookmarks)} markers")
    for name, tick in list(bookmarks.items())[:5]:
        print(f"  {name:<40} tick {tick}")
    print()

    # Compare 3 seeds
    print("[Compare — 3 seeds of peter_scarcity_baseline]")
    streams = {
        "seed_0": obs,
        "seed_1": build_real_stream_from_anchor(seed=1),
        "seed_2": build_real_stream_from_anchor(seed=2),
    }
    print(format_seed_comparison(streams))
    print()
    print(narrate_seed_comparison(streams))
    print()

    return 0


def top_salient_moments_for(observer: Observer, top_n: int = 5) -> list[dict]:
    """Helper: top salient moments via internal snapshots."""
    from engine.observer.salience import top_salient_moments

    snapshots = [observer._tick_index[t] for t in observer.list_ticks()]
    return top_salient_moments(snapshots, top_n=top_n)


def cmd_narrate() -> int:
    """Narrative summary demo (Phase O7 prose narrators)."""
    obs = build_synthetic_stream()
    print("=" * 70)
    print("DEMO — Narrative Summaries (한국어 prose)")
    print("=" * 70)
    print()

    # World arc
    print("[World Arc]")
    print(narrate_world_arc(obs))
    print()

    # Person arc
    print("[Person Arc — agent_001]")
    print(narrate_person_arc(obs, "agent_001"))
    print()

    # Event ripple
    print("[Event Ripple — public_accusation]")
    print(narrate_event_ripple(obs, "public_accusation"))
    print()

    # Seed comparison
    streams = {
        "seed_0_recover": build_synthetic_stream("seed_0"),
        "seed_2_locked": build_synthetic_stream("seed_2"),
    }
    print("[Seed Comparison — recover vs locked]")
    print(narrate_seed_comparison(streams))
    print()

    return 0


def cmd_full() -> int:
    """Default: full demo (status + views + replay + compare + narrate + full report)."""
    cmd_status()
    print()
    print()
    cmd_views()
    print()
    cmd_replay()
    print()
    cmd_compare()
    print()
    cmd_narrate()
    print()

    obs = build_synthetic_stream()
    print("=" * 70)
    print("DEMO — Full report (composite at middle tick)")
    print("=" * 70)
    print()
    print(format_full_report(obs))

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        return cmd_full()

    arg = sys.argv[1]
    if arg == "--status":
        return cmd_status()
    if arg == "--views":
        return cmd_views()
    if arg == "--replay":
        return cmd_replay()
    if arg == "--compare":
        return cmd_compare()
    if arg == "--narrate":
        return cmd_narrate()
    if arg == "--real":
        return cmd_real()

    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
