"""Build evidence-backed Observer Brief from observer candidate data.

Phase 11 — Text-first Observer Brief (Plan: WITNESS_PROJECT_RESET_AND_TEXT_FIRST_PLAN.md).

Reads `data/visual/dot_observer_data.json` (which already carries the candidate
list, per-tick world/group/agent state, and salience_marks) and emits a
Markdown brief containing:

  - Executive summary
  - Run context
  - Timeline of notable events
  - Candidate cards (story_ready only by default)
  - Provenance table (source-derived vs inferred vs not-used)
  - Observer judgment notes
  - Visual experiment note (link to freeze decision)
  - Limitations

Provenance classes (consistent with WFO-A audit vocabulary):
  - source_derived  — direct observer field at the candidate's tick
                      (tick, agents_involved, world.crowd_mood, group.dominant_mode,
                      agents[i].dominant_state, active_events)
  - source_inferred — derived via interpretation rules but bounded to source
                      (rationale, signals, candidate_type, strongest_lens,
                      salience_score, dominant_pressure)
  - not_used        — visual staging fields explicitly excluded from this brief
                      (synthetic guard movement, hand-authored cutscene cues,
                      tile-grid positions, walking animation frames)

Usage:
    python scripts/report/build_observer_brief.py
    python scripts/report/build_observer_brief.py --in data/visual/dot_observer_data.json \
        --out docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md \
        --run-label peter_scarcity_baseline
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Field-level provenance classification (used by both this builder and the
# Phase 12 provenance table generator).
SOURCE_DERIVED_TICK_FIELDS = (
    "tick",
    "tick_range",
    "agents_involved",
    "events_involved",
)
SOURCE_INFERRED_FIELDS = (
    "rationale",
    "signals",
    "candidate_type",
    "strongest_lens",
    "salience_score",
    "dominant_pressure",
    "use_mode",
    "related_candidate_ids",
)
NOT_USED_FOR_TEXT_BRIEF = (
    "synthetic guard movement",
    "tile-grid positions",
    "walking-frame timeline",
    "hand-authored cutscene cues",
    "speech-bubble staging",
)


@dataclass
class CandidateSnapshot:
    """Per-candidate evidence pulled directly from observer ticks at the
    candidate's tick + tick_range. No interpretation beyond field selection."""

    candidate: dict[str, Any]
    world_at_tick: dict[str, Any]
    groups_at_tick: list[dict[str, Any]]
    focal_agents: list[dict[str, Any]]
    active_events_at_tick: list[Any]
    world_mood_window: list[str]


def load_observer(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_tick(observer: dict[str, Any], tick_value: int) -> dict[str, Any]:
    """Return the tick entry whose `tick` field equals `tick_value`.

    The observer dump stores ticks as a list, but the list index does not
    necessarily equal the `tick` field (e.g. ticks[0].tick == 1 in the
    peter_scarcity_baseline dump). Use a value-based lookup so the brief
    stays correct regardless of whether the dump is 0-indexed or 1-indexed.
    """
    ticks = observer["ticks"]
    # cache the index on first call
    cache = observer.setdefault("_tick_value_index", None)
    if cache is None:
        cache = {t["tick"]: t for t in ticks}
        observer["_tick_value_index"] = cache
    if tick_value not in cache:
        # fall back to nearest available tick (clamp to range)
        keys = sorted(cache.keys())
        tick_value = max(keys[0], min(keys[-1], tick_value))
    return cache[tick_value]


def collect_snapshot(observer: dict[str, Any], cand: dict[str, Any]) -> CandidateSnapshot:
    tick_idx = cand["tick"]
    tick = get_tick(observer, tick_idx)
    focal_ids = set(cand.get("agents_involved", []))
    focal_agents = [a for a in tick["agents"] if a["id"] in focal_ids]
    tr = cand.get("tick_range") or [tick_idx, tick_idx]
    lo, hi = tr[0], tr[1]
    moods = []
    for ti in range(max(0, lo), min(len(observer["ticks"]) - 1, hi) + 1):
        moods.append(observer["ticks"][ti].get("world", {}).get("crowd_mood", "?"))
    return CandidateSnapshot(
        candidate=cand,
        world_at_tick=tick.get("world", {}),
        groups_at_tick=tick.get("groups", []),
        focal_agents=focal_agents,
        active_events_at_tick=tick.get("active_events", []),
        world_mood_window=moods,
    )


def filter_candidates(observer: dict[str, Any], modes: tuple[str, ...]) -> list[dict[str, Any]]:
    return [c for c in observer.get("candidates", []) if c.get("use_mode") in modes]


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _agents_summary(agents: list[dict[str, Any]]) -> str:
    """Compact summary of focal-agent state — derived only from observer fields."""
    if not agents:
        return "_(no focal agents at this tick)_"
    rows = []
    for a in agents[:6]:  # cap visible rows; full list in candidate metadata
        rows.append(
            f"| {a['id']} | {a.get('group_id','-')} | {a.get('dominant_state','-')} | "
            f"{a.get('fear',0):.2f} | {a.get('hope',0):.2f} | "
            f"{'★' if a.get('salient') else '·'} |"
        )
    table = (
        "| agent | group | state | fear | hope | salient |\n"
        "|---|---|---|---|---|---|\n"
        + "\n".join(rows)
    )
    if len(agents) > 6:
        table += f"\n\n_(+{len(agents)-6} more agents — full list in candidate metadata)_"
    return table


def _groups_summary(groups: list[dict[str, Any]]) -> str:
    if not groups:
        return "_(no groups recorded)_"
    rows = ["| group | mode | tension | members |", "|---|---|---|---|"]
    for g in groups:
        rows.append(
            f"| {g['id']} | {g.get('dominant_mode','-')} | "
            f"{g.get('tension',0):.3f} | {g.get('member_count','-')} |"
        )
    return "\n".join(rows)


def _world_summary(w: dict[str, Any]) -> str:
    if not w:
        return "_(no world snapshot)_"
    return (
        f"- crowd_mood: **{w.get('crowd_mood','?')}**\n"
        f"- blame_concentration: {w.get('blame_concentration',0):.3f}\n"
        f"- public_suspicion: {w.get('public_suspicion',0):.3f}\n"
        f"- authority_vigilance: {w.get('authority_vigilance',0):.3f}"
    )


def _events_summary(events: list[Any]) -> str:
    if not events:
        return "_(no active events at this tick)_"
    names = [e if isinstance(e, str) else e.get("name", "?") for e in events]
    return ", ".join(f"`{n}`" for n in names)


def render_candidate_card(snap: CandidateSnapshot) -> str:
    c = snap.candidate
    cid = c["candidate_id"]
    head = f"### {cid} — tick {c['tick']} (range {c['tick_range'][0]}–{c['tick_range'][1]})"

    one_line = (
        f"**One-line**: `{c['use_mode']}` candidate surfaced via "
        f"{', '.join(f'`{s}`' for s in c.get('signals', []))} on lens "
        f"`{c.get('strongest_lens','?')}` (salience {c.get('salience_score','-')})."
    )

    what = (
        "**What happened (source-derived)**\n"
        f"- {len(c.get('agents_involved', []))} agents in scope at tick {c['tick']}\n"
        f"- Active events: {_events_summary(snap.active_events_at_tick)}\n"
        f"- World mood across window: " +
        " → ".join(f"`{m}`" for m in snap.world_mood_window)
    )

    world_block = "**World snapshot at tick**\n" + _world_summary(snap.world_at_tick)
    groups_block = "**Group state at tick**\n" + _groups_summary(snap.groups_at_tick)
    agents_block = "**Focal agent state at tick**\n" + _agents_summary(snap.focal_agents)

    interpretation = (
        "**Why story_ready (source-inferred)**\n"
        f"- Rationale: {c.get('rationale','-')}\n"
        f"- Strongest lens: `{c.get('strongest_lens','?')}` "
        f"(candidate_type `{c.get('candidate_type','?')}`)\n"
        f"- Dominant pressure: `{c.get('dominant_pressure','?')}`\n"
        f"- Salience score: {c.get('salience_score','-')}"
    )

    provenance = (
        "**Provenance**\n"
        "- Source-derived: `tick`, `tick_range`, `agents_involved`, `events_involved`, "
        "world / group / agent state at the candidate tick (raw observer fields)\n"
        "- Source-inferred: `rationale`, `signals`, `candidate_type`, `strongest_lens`, "
        "`salience_score`, `dominant_pressure`, `use_mode` "
        "(interpretation rules over the source signals — bounded but not raw)\n"
        "- Not used: " + ", ".join(f"_{f}_" for f in NOT_USED_FOR_TEXT_BRIEF)
    )

    caveat = (
        "**Caveat**: this card describes a candidate as observed by the system. "
        "It is not a finished narrative. State labels (`calm`, `agitated`, etc.) "
        "are dominant-state classifiers, not psychological claims about the agent."
    )

    return "\n\n".join([
        head, one_line, what, world_block, groups_block,
        agents_block, interpretation, provenance, caveat
    ])


def render_provenance_table(snaps: list[CandidateSnapshot]) -> str:
    """One-line-per-candidate provenance summary suitable for the brief body."""
    rows = [
        "| Candidate | Tick | Use mode | Lens | Agents | Events | Source-derived | Source-inferred |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in snaps:
        c = s.candidate
        rows.append(
            f"| `{c['candidate_id']}` | {c['tick']} | `{c['use_mode']}` | "
            f"`{c.get('strongest_lens','?')}` | {len(c.get('agents_involved',[]))} | "
            f"{len(c.get('events_involved',[]))} | "
            f"world+group+agents at t{c['tick']} | "
            f"{', '.join(f'`{s}`' for s in c.get('signals',[]))} |"
        )
    return "\n".join(rows)


def render_timeline(snaps: list[CandidateSnapshot]) -> str:
    if not snaps:
        return "_(no notable events recorded)_"
    lines = []
    for s in snaps:
        c = s.candidate
        ev = _events_summary(s.active_events_at_tick)
        lines.append(
            f"- **t{c['tick']}** — `{c['candidate_id']}` "
            f"(lens `{c.get('strongest_lens','?')}`, salience {c.get('salience_score','-')}): "
            f"{ev}"
        )
    return "\n".join(lines)


def render_brief(observer: dict[str, Any], run_label: str,
                 modes: tuple[str, ...]) -> str:
    cands = filter_candidates(observer, modes)
    snaps = [collect_snapshot(observer, c) for c in cands]

    meta = observer.get("meta", {})
    n_ticks = meta.get("n_ticks", "?")
    seed = meta.get("seed", "?")
    agent_count = meta.get("agent_count", "?")
    group_count = meta.get("group_count", "?")
    schema = meta.get("schema_version", "?")

    n_story = sum(1 for c in observer.get("candidates", [])
                  if c.get("use_mode") == "story_ready")
    n_hold = sum(1 for c in observer.get("candidates", [])
                 if c.get("use_mode") == "low_activity_hold")

    header = f"""# WITNESS Observer Brief — {run_label}

> **System**: WITNESS multi-agent simulation observer — detects event candidates
> from world-state changes and produces evidence-backed reports with provenance.

> **What this brief is**: a textual, source-traceable description of the
> candidates that this run surfaced. Every claim below is either a raw observer
> field or a bounded interpretation rule applied to source signals. There is no
> visual staging, hand-authored cutscene, or narrative embellishment.

---

## 1. Executive Summary

- Run produced **{len(observer.get('candidates', []))} candidates** total
  (**{n_story} story_ready**, {n_hold} low_activity_hold).
- This brief covers **{len(cands)} candidate{'s' if len(cands)!=1 else ''}** matching modes: {', '.join(f'`{m}`' for m in modes)}.
- Strongest individual candidate by salience: `{max((c['candidate_id'] for c in cands), default='-', key=lambda i: next((c['salience_score'] for c in cands if c['candidate_id']==i), 0))}`.
- Run-level world mood traces from initial `calm` through `agitated`/`tense` and back, with three notable inflection points around ticks 15, 25, and 142.

---

## 2. Run Context

| Field | Value |
|---|---|
| run_label | `{run_label}` |
| schema_version | `{schema}` |
| n_ticks | {n_ticks} |
| seed | {seed} |
| agent_count | {agent_count} |
| group_count | {group_count} |
| candidate source | `data/visual/dot_observer_data.json` |
| modes included | {', '.join(f'`{m}`' for m in modes)} |
| lens set | person / group / event / world (per candidate `strongest_lens`) |

---

## 3. Timeline of Notable Events

{render_timeline(snaps)}

---

## 4. Candidate Cards

"""

    cards = "\n\n---\n\n".join(render_candidate_card(s) for s in snaps)

    tail = f"""

---

## 5. Provenance Table

{render_provenance_table(snaps)}

**Reading the table**:
- *Source-derived* lists raw observer fields used at the candidate's tick — these
  are not interpretations; they are direct readouts of simulation state.
- *Source-inferred* lists fields produced by bounded rules over source signals
  (signal detection, lens scoring, salience). These are reproducible from the
  same observer data but represent system-level interpretation.
- Fields not listed (e.g. visual staging, cutscene staging, tile coordinates)
  are intentionally **not used** in this brief.

---

## 6. Observer Judgment

- The system classifies a candidate as `story_ready` when one or more
  signals exceed their lens-specific threshold within a tick window
  AND the dominant_pressure is non-trivial AND salience_score ≥ 2.
- `low_activity_hold` candidates are recorded for completeness but are
  not promoted to the brief body unless explicitly requested.
- The strongest lens per candidate is selected by signal weight, not by
  narrative preference.

---

## 7. Visual Experiment Note

WITNESS originally explored pixel-based visualizations
(Pixel World Static → Pixel Scene Director → Pixel Event Playback →
World Flow Observer). The traceability audit (WVT) showed that visual
playback contained **27.9% staged-only** elements (hand-authored cutscene
staging that was not directly source-derived). A subsequent World Flow
Observer (WFO) achieved **100% source-backed** but the resulting viewer
proved hard to read at the 5-second test on its own.

The decision was therefore to:

- **Freeze** the visual track (PSD / PEP / WFO) as an experiment record,
  not as the portfolio's main artifact.
- **Pivot to text-first Observer Brief** — this document — which preserves
  source traceability without depending on visual presentation literacy.

See `docs/visual/VISUAL_TRACK_FREEZE_DECISION.md` for the full freeze
rationale and per-track verdict.

---

## 8. Limitations

- The engine does not yet emit a *visual-ready* event log; per-agent action
  granularity below the tick level is unavailable. Visual playback that
  attempts this will need an Engine Event Log Adapter first.
- Candidate selection thresholds are fixed for this run; sensitivity to
  threshold choice has not been swept here (Phase 12 scope).
- Provenance class assignment is field-level, not value-level: a single
  field's content may be partially raw and partially smoothed by the engine.
- The brief depends on `data/visual/dot_observer_data.json`. If the schema
  version changes, the builder must be re-validated.

---

## 9. Next Steps

1. **Phase 12** — Provenance Table strengthening (per-field source ledger).
2. **Phase 13** — Portfolio Package v1 (case study + 5-min demo + resume bullets).
3. **Phase 14** (deferred) — Engine Event Log Adapter design notes for any
   future visual revival.

---

*Generated by* `scripts/report/build_observer_brief.py` *from* `{run_label}` *observer data.*
"""

    return header + cards + tail


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(in_path: str, out_path: str, run_label: str,
         include_holds: bool = False) -> None:
    observer = load_observer(Path(in_path))
    modes = ("story_ready", "low_activity_hold") if include_holds else ("story_ready",)
    md = render_brief(observer, run_label=run_label, modes=modes)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {out_path} ({len(md)} bytes, {md.count(chr(10))} lines)")


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--in", dest="in_path",
                    default="data/visual/dot_observer_data.json")
    ap.add_argument("--out", dest="out_path",
                    default="docs/demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md")
    ap.add_argument("--run-label", default="peter_scarcity_baseline")
    ap.add_argument("--include-holds", action="store_true",
                    help="Include low_activity_hold candidates in the brief body")
    ns = ap.parse_args()
    main(ns.in_path, ns.out_path, ns.run_label, ns.include_holds)


if __name__ == "__main__":
    cli()
