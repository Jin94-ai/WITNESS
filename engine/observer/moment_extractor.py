"""Moment Extractor — Narrative Mining Layer Phase 1.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §4.2.

Walks an observer dump (or in-memory snapshot stream) and emits a
deterministic list of Moment objects.

Extractor families:
    A. agent_state_shift       — fear/hope/shame_self/dominant_state delta ≥ threshold
    B. group_tension_shift     — group.tension delta or mode change
    C. world_pressure_shift    — crowd_mood / authority / blame / suspicion delta
    D. conflict_marker         — co-occurring signal cross (multi-source)
    E. unresolved_thread       — sustained pressure for ≥ N ticks

ABSOLUTE Rules:
    - Rule #1: no agent_id hardcoding. All agent IDs come from data.
    - Rule #6: existing observer API is not modified.
    - Determinism: same input -> same Moment list (no rng).

Thresholds are exposed as parameters (defaults documented). Tuning lives in
the caller, not in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from engine.observer.moment import Moment

# ---------------------------------------------------------------------------
# Threshold configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MomentThresholds:
    """Thresholds for Moment extraction.

    Defaults chosen so a 200-tick / 12-agent baseline yields ~30–150
    Moments — enough material for thread mining, not so many that every
    tick generates noise.
    """
    agent_state_delta: float = 1.5            # 0–10 scale
    agent_state_field_min: float = 0.5        # ignore tiny noise
    group_tension_delta: float = 0.15         # 0–1 scale
    world_pressure_delta: float = 0.08        # 0–1 scale (mood is categorical)
    sustained_pressure_min_ticks: int = 8     # for unresolved_thread
    sustained_pressure_field: str = "fear"
    sustained_pressure_threshold: float = 7.0
    conflict_window: int = 3                  # ticks for co-occurring signals
    min_tick_gap_per_agent: int = 4           # don't flood the same agent


DEFAULT_THRESHOLDS = MomentThresholds()


# ---------------------------------------------------------------------------
# Helpers — observer dump shape (reuses the same JSON used by the brief)
# ---------------------------------------------------------------------------

def _build_tick_index(observer: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Returns tick_value → tick_dict (the observer dump stores ticks in a
    list, but list[i].tick is not always == i — this mirrors the brief's
    safe lookup convention)."""
    return {t["tick"]: t for t in observer.get("ticks", [])}


def _agent_at(tick: dict[str, Any], agent_id: str) -> dict[str, Any] | None:
    for a in tick.get("agents", []):
        if a.get("id") == agent_id:
            return a
    return None


def _group_at(tick: dict[str, Any], group_id: str) -> dict[str, Any] | None:
    for g in tick.get("groups", []):
        if g.get("id") == group_id:
            return g
    return None


def _all_agent_ids(observer: dict[str, Any]) -> list[str]:
    seen: dict[str, None] = {}
    for tick in observer.get("ticks", []):
        for a in tick.get("agents", []):
            seen.setdefault(a["id"], None)
    return list(seen.keys())


def _all_group_ids(observer: dict[str, Any]) -> list[str]:
    seen: dict[str, None] = {}
    for tick in observer.get("ticks", []):
        for g in tick.get("groups", []):
            seen.setdefault(g["id"], None)
    return list(seen.keys())


# ---------------------------------------------------------------------------
# Extractor A — Agent state shifts
# ---------------------------------------------------------------------------

_AGENT_FIELDS = ("fear", "hope", "shame_self")


def _extract_agent_state_shifts(
    observer: dict[str, Any],
    th: MomentThresholds,
) -> list[Moment]:
    moments: list[Moment] = []
    ticks_sorted = sorted(observer.get("ticks", []), key=lambda t: t["tick"])
    if len(ticks_sorted) < 2:
        return moments

    last_emit_tick: dict[str, int] = {}  # agent_id → last tick we emitted

    for prev, curr in zip(ticks_sorted, ticks_sorted[1:]):
        for a_curr in curr.get("agents", []):
            aid = a_curr["id"]
            a_prev = _agent_at(prev, aid)
            if not a_prev:
                continue

            # Find the largest field delta
            best_field = None
            best_delta = 0.0
            best_signed = 0.0
            for f in _AGENT_FIELDS:
                p = a_prev.get(f, 0.0)
                c = a_curr.get(f, 0.0)
                if abs(c) < th.agent_state_field_min and abs(p) < th.agent_state_field_min:
                    continue
                d = abs(c - p)
                if d > best_delta:
                    best_delta = d
                    best_signed = c - p
                    best_field = f

            # Also check categorical state change
            cat_change = (
                a_prev.get("dominant_state") != a_curr.get("dominant_state")
            )

            if best_delta < th.agent_state_delta and not cat_change:
                continue

            # Anti-flood: per-agent min gap
            t = curr["tick"]
            if aid in last_emit_tick and (t - last_emit_tick[aid]) < th.min_tick_gap_per_agent:
                continue
            last_emit_tick[aid] = t

            field_used = best_field or "dominant_state"
            direction = (
                "rises" if best_signed > 0 else
                "falls" if best_signed < 0 else
                "shifts"
            )
            if cat_change and best_field is None:
                summary = (
                    f"{aid} dominant_state shifts "
                    f"{a_prev.get('dominant_state')} → {a_curr.get('dominant_state')}"
                )
            else:
                summary = f"{aid} {field_used} {direction} ({best_signed:+.2f})"

            # Salience: normalize delta to [0, 1] (cap at 5.0 → 1.0)
            sal = min(1.0, best_delta / 5.0) if best_delta > 0 else 0.4

            moments.append(Moment(
                moment_id=f"M_t{t:03d}_{aid}_{field_used}",
                tick=t,
                tick_range=(prev["tick"], t),
                moment_type="agent_state_shift",
                agents=(aid,),
                groups=(a_curr.get("group_id"),) if a_curr.get("group_id") else (),
                pressures=(field_used,) if field_used in _AGENT_FIELDS else (),
                signals=("agent_state_shift",),
                summary=summary,
                salience_score=sal,
                provenance="source_derived",
            ))
    return moments


# ---------------------------------------------------------------------------
# Extractor B — Group tension shifts
# ---------------------------------------------------------------------------

def _extract_group_tension_shifts(
    observer: dict[str, Any],
    th: MomentThresholds,
) -> list[Moment]:
    moments: list[Moment] = []
    ticks_sorted = sorted(observer.get("ticks", []), key=lambda t: t["tick"])

    last_emit: dict[str, int] = {}

    for prev, curr in zip(ticks_sorted, ticks_sorted[1:]):
        for g_curr in curr.get("groups", []):
            gid = g_curr["id"]
            g_prev = _group_at(prev, gid)
            if not g_prev:
                continue

            tension_delta = g_curr.get("tension", 0.0) - g_prev.get("tension", 0.0)
            mode_changed = (
                g_curr.get("dominant_mode") != g_prev.get("dominant_mode")
            )

            if abs(tension_delta) < th.group_tension_delta and not mode_changed:
                continue

            t = curr["tick"]
            if gid in last_emit and (t - last_emit[gid]) < th.min_tick_gap_per_agent:
                continue
            last_emit[gid] = t

            if mode_changed:
                summary = (
                    f"group {gid} mode {g_prev.get('dominant_mode')} → "
                    f"{g_curr.get('dominant_mode')} (tension {tension_delta:+.3f})"
                )
            else:
                direction = "rises" if tension_delta > 0 else "falls"
                summary = f"group {gid} tension {direction} ({tension_delta:+.3f})"

            sal = min(1.0, abs(tension_delta) * 3) if abs(tension_delta) > 0 else 0.5
            moments.append(Moment(
                moment_id=f"M_t{t:03d}_{gid}_tension",
                tick=t,
                tick_range=(prev["tick"], t),
                moment_type="group_tension_shift",
                groups=(gid,),
                pressures=("group_tension",),
                signals=("group_tension_shift",),
                summary=summary,
                salience_score=sal,
                provenance="source_derived",
            ))
    return moments


# ---------------------------------------------------------------------------
# Extractor C — World pressure shifts
# ---------------------------------------------------------------------------

_WORLD_FIELDS = ("blame_concentration", "public_suspicion", "authority_vigilance")


def _extract_world_pressure_shifts(
    observer: dict[str, Any],
    th: MomentThresholds,
) -> list[Moment]:
    moments: list[Moment] = []
    ticks_sorted = sorted(observer.get("ticks", []), key=lambda t: t["tick"])

    last_emit_field: dict[str, int] = {}

    for prev, curr in zip(ticks_sorted, ticks_sorted[1:]):
        wp = prev.get("world", {})
        wc = curr.get("world", {})
        t = curr["tick"]

        # Categorical mood shift
        if wp.get("crowd_mood") != wc.get("crowd_mood"):
            moments.append(Moment(
                moment_id=f"M_t{t:03d}_world_mood",
                tick=t,
                tick_range=(prev["tick"], t),
                moment_type="world_pressure_shift",
                pressures=("crowd_mood",),
                signals=("world_pressure_shift", "mood_shift"),
                summary=f"crowd_mood {wp.get('crowd_mood')} → {wc.get('crowd_mood')}",
                salience_score=0.7,
                provenance="source_derived",
            ))

        # Scalar pressure deltas
        for f in _WORLD_FIELDS:
            d = wc.get(f, 0.0) - wp.get(f, 0.0)
            if abs(d) < th.world_pressure_delta:
                continue
            if f in last_emit_field and (t - last_emit_field[f]) < th.min_tick_gap_per_agent:
                continue
            last_emit_field[f] = t
            direction = "rises" if d > 0 else "falls"
            sal = min(1.0, abs(d) * 4)
            moments.append(Moment(
                moment_id=f"M_t{t:03d}_world_{f}",
                tick=t,
                tick_range=(prev["tick"], t),
                moment_type="world_pressure_shift",
                pressures=(f,),
                signals=("world_pressure_shift",),
                summary=f"world.{f} {direction} ({d:+.3f})",
                salience_score=sal,
                provenance="source_derived",
            ))
    return moments


# ---------------------------------------------------------------------------
# Extractor D — Conflict markers (co-occurring signals)
# ---------------------------------------------------------------------------

def _extract_conflict_markers(
    observer: dict[str, Any],
    th: MomentThresholds,
    base_moments: list[Moment],
) -> list[Moment]:
    """Scans windows for co-occurring multi-source signals.

    Pattern A: agent fear-rise + world.authority_vigilance rise (within W ticks)
    Pattern B: group tension rise + world.public_suspicion rise (within W ticks)
    Pattern C: agent fear-rise + agent hope-fall on same agent (within W ticks)
    """
    moments: list[Moment] = []

    by_tick: dict[int, list[Moment]] = {}
    for m in base_moments:
        by_tick.setdefault(m.tick, []).append(m)

    last_emit_pattern: dict[str, int] = {}

    for t in sorted(by_tick.keys()):
        window_moments: list[Moment] = []
        for ti in range(t, t + th.conflict_window):
            window_moments.extend(by_tick.get(ti, []))

        # Pattern A: fear-up + authority_vigilance up
        fear_ups = [m for m in window_moments if "fear" in m.pressures and "rises" in m.summary]
        auth_ups = [
            m for m in window_moments
            if "authority_vigilance" in m.pressures and "rises" in m.summary
        ]
        if fear_ups and auth_ups:
            key = f"A_{t}"
            if "A" in last_emit_pattern and (t - last_emit_pattern["A"]) < th.conflict_window:
                pass
            else:
                last_emit_pattern["A"] = t
                agents = tuple(sorted({a for m in fear_ups for a in m.agents}))
                moments.append(Moment(
                    moment_id=f"M_t{t:03d}_conflict_authority_fear",
                    tick=t,
                    tick_range=(t, t + th.conflict_window - 1),
                    moment_type="conflict_marker",
                    agents=agents,
                    pressures=("fear", "authority_vigilance"),
                    signals=("conflict_marker", "agent_state_shift", "world_pressure_shift"),
                    summary=(
                        f"agents fear rises while authority_vigilance rises "
                        f"(co-occurrence at t={t})"
                    ),
                    salience_score=0.85,
                    provenance="source_inferred",
                ))

        # Pattern B: group tension up + public_suspicion up
        ten_ups = [
            m for m in window_moments
            if m.moment_type == "group_tension_shift" and "rises" in m.summary
        ]
        sus_ups = [
            m for m in window_moments
            if "public_suspicion" in m.pressures and "rises" in m.summary
        ]
        if ten_ups and sus_ups:
            if "B" in last_emit_pattern and (t - last_emit_pattern["B"]) < th.conflict_window:
                pass
            else:
                last_emit_pattern["B"] = t
                groups = tuple(sorted({g for m in ten_ups for g in m.groups}))
                moments.append(Moment(
                    moment_id=f"M_t{t:03d}_conflict_suspicion_tension",
                    tick=t,
                    tick_range=(t, t + th.conflict_window - 1),
                    moment_type="conflict_marker",
                    groups=groups,
                    pressures=("group_tension", "public_suspicion"),
                    signals=("conflict_marker", "group_tension_shift", "world_pressure_shift"),
                    summary=(
                        f"group tension rises with public_suspicion at t={t}"
                    ),
                    salience_score=0.80,
                    provenance="source_inferred",
                ))

        # Pattern C: per-agent fear-up + hope-down
        agents_with_fear_up: dict[str, Moment] = {}
        agents_with_hope_down: dict[str, Moment] = {}
        for m in window_moments:
            if m.moment_type != "agent_state_shift" or len(m.agents) != 1:
                continue
            aid = m.agents[0]
            if "fear" in m.pressures and "rises" in m.summary:
                agents_with_fear_up[aid] = m
            elif "hope" in m.pressures and "falls" in m.summary:
                agents_with_hope_down[aid] = m
        for aid in agents_with_fear_up.keys() & agents_with_hope_down.keys():
            key = f"C_{aid}"
            if key in last_emit_pattern and (t - last_emit_pattern[key]) < th.conflict_window:
                continue
            last_emit_pattern[key] = t
            moments.append(Moment(
                moment_id=f"M_t{t:03d}_conflict_internal_{aid}",
                tick=t,
                tick_range=(t, t + th.conflict_window - 1),
                moment_type="conflict_marker",
                agents=(aid,),
                pressures=("fear", "hope"),
                signals=("conflict_marker", "agent_state_shift"),
                summary=f"{aid} fear rises while hope falls (internal collapse window)",
                salience_score=0.82,
                provenance="source_inferred",
            ))

    return moments


# ---------------------------------------------------------------------------
# Extractor E — Unresolved threads (sustained pressure)
# ---------------------------------------------------------------------------

def _extract_unresolved_threads(
    observer: dict[str, Any],
    th: MomentThresholds,
) -> list[Moment]:
    """Detects sustained-pressure runs.

    For each agent, finds maximal runs of ticks where the chosen pressure
    field stays above threshold. Emits one Moment per run if the run length
    is ≥ sustained_pressure_min_ticks.
    """
    moments: list[Moment] = []
    ticks_sorted = sorted(observer.get("ticks", []), key=lambda t: t["tick"])
    field = th.sustained_pressure_field
    threshold = th.sustained_pressure_threshold

    for aid in _all_agent_ids(observer):
        run_start: int | None = None
        run_peak: float = 0.0
        for tick in ticks_sorted:
            a = _agent_at(tick, aid)
            v = a.get(field, 0.0) if a else 0.0
            t = tick["tick"]
            if v >= threshold:
                if run_start is None:
                    run_start = t
                    run_peak = v
                else:
                    run_peak = max(run_peak, v)
            else:
                if run_start is not None and (t - run_start) >= th.sustained_pressure_min_ticks:
                    moments.append(Moment(
                        moment_id=f"M_t{run_start:03d}_unresolved_{aid}_{field}",
                        tick=run_start,
                        tick_range=(run_start, t - 1),
                        moment_type="unresolved_thread",
                        agents=(aid,),
                        pressures=(field,),
                        signals=("unresolved_thread", "sustained_pressure"),
                        summary=(
                            f"{aid} {field} stays above {threshold:.1f} for "
                            f"{t - run_start} ticks (peak {run_peak:.2f})"
                        ),
                        salience_score=min(1.0, (t - run_start) / 30.0),
                        provenance="source_derived",
                    ))
                run_start = None
                run_peak = 0.0
        # Run continues to end?
        if run_start is not None and ticks_sorted:
            t_end = ticks_sorted[-1]["tick"]
            if (t_end - run_start + 1) >= th.sustained_pressure_min_ticks:
                moments.append(Moment(
                    moment_id=f"M_t{run_start:03d}_unresolved_{aid}_{field}",
                    tick=run_start,
                    tick_range=(run_start, t_end),
                    moment_type="unresolved_thread",
                    agents=(aid,),
                    pressures=(field,),
                    signals=("unresolved_thread", "sustained_pressure"),
                    summary=(
                        f"{aid} {field} stays above {threshold:.1f} for "
                        f"{t_end - run_start + 1} ticks until end of run "
                        f"(peak {run_peak:.2f})"
                    ),
                    salience_score=min(1.0, (t_end - run_start) / 30.0),
                    provenance="source_derived",
                ))
    return moments


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def extract_moments(
    observer: dict[str, Any],
    thresholds: MomentThresholds | None = None,
) -> list[Moment]:
    """Extract a deterministic, sorted list of Moments from an observer dump.

    Sort key: (tick, moment_id) for stable test fixtures.
    """
    th = thresholds or DEFAULT_THRESHOLDS

    a_moments = _extract_agent_state_shifts(observer, th)
    b_moments = _extract_group_tension_shifts(observer, th)
    c_moments = _extract_world_pressure_shifts(observer, th)
    base = a_moments + b_moments + c_moments
    d_moments = _extract_conflict_markers(observer, th, base_moments=base)
    e_moments = _extract_unresolved_threads(observer, th)

    all_moments = base + d_moments + e_moments
    all_moments.sort(key=lambda m: (m.tick, m.moment_id))
    return all_moments


def serialize_moments(
    moments: Iterable[Moment],
    *,
    run_label: str,
    schema_version: str = "moments_v1",
) -> dict[str, Any]:
    moment_list = list(moments)
    return {
        "run_label": run_label,
        "schema_version": schema_version,
        "moments": [m.to_dict() for m in moment_list],
        "summary": {
            "total": len(moment_list),
            "by_type": _count_by(moment_list, lambda m: m.moment_type),
            "by_provenance": _count_by(moment_list, lambda m: m.provenance),
        },
    }


def _count_by(moments: list[Moment], key) -> dict[str, int]:
    out: dict[str, int] = {}
    for m in moments:
        k = key(m)
        out[k] = out.get(k, 0) + 1
    return out
