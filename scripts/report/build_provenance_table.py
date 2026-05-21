"""Build per-field Provenance Table (Phase 12).

Difference from Phase 11's Observer Brief:
  - The brief reports candidates with one short Provenance block per card.
  - This table is *one row per field per candidate*: a flat ledger that lets
    the reader verify every single value's provenance class.

Class assignment (field-level, not value-level):

  source_derived: field is a direct readout of an observer tick — no rule
                  applied. (tick, tick_range, agents_involved,
                  events_involved, world snapshot fields, group fields,
                  agent fields)

  source_inferred: field is produced by a bounded rule operating over
                  source signals. The output is reproducible from the same
                  observer dump but represents system-level interpretation.
                  (rationale, signals, strongest_lens, candidate_type,
                  salience_score, dominant_pressure, use_mode,
                  related_candidate_ids)

  not_used:      field would have come from the visual staging layer
                 (synthetic guard movement, tile-grid coords, walking
                 frames, speech-bubble timing). Explicitly excluded from
                 the text-first brief.

Confidence (qualitative): high / medium / low.
  - high   = directly read from a single source field, no aggregation.
  - medium = aggregation over a small window (tick range / focal agents).
  - low    = single classifier output with policy threshold.

Outputs:
  - docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md
  - data/report/provenance_table.json (machine-readable, optional)

CLI:
  python scripts/report/build_provenance_table.py
  python scripts/report/build_provenance_table.py --include-holds \
      --json data/report/provenance_table.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_brief_module() -> Any:
    """Reuse the brief module's tick lookup + filter helpers."""
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "build_observer_brief", here / "build_observer_brief.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("build_observer_brief", mod)
    spec.loader.exec_module(mod)
    return mod


bob = _load_brief_module()


# ---------------------------------------------------------------------------
# Field schema (locked manually — adapter changes require re-validation)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldSpec:
    name: str
    cls: str            # source_derived | source_inferred | not_used
    confidence: str     # high | medium | low
    source: str         # human-readable source path
    note: str = ""


CANDIDATE_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("candidate_id", "source_derived", "high",
              "observer.candidates[i].candidate_id",
              "stable identifier; not interpreted"),
    FieldSpec("tick", "source_derived", "high",
              "observer.candidates[i].tick",
              "anchor tick of the candidate"),
    FieldSpec("tick_range", "source_derived", "high",
              "observer.candidates[i].tick_range",
              "[lo, hi] window the candidate spans"),
    FieldSpec("agents_involved", "source_derived", "high",
              "observer.candidates[i].agents_involved",
              "stable agent IDs; ordering is observer-imposed"),
    FieldSpec("events_involved", "source_derived", "high",
              "observer.candidates[i].events_involved",
              "active_events seen across the tick range"),
    FieldSpec("rationale", "source_inferred", "medium",
              "observer scoring rules over signals",
              "free-text label of which signals fired"),
    FieldSpec("signals", "source_inferred", "high",
              "observer signal detector outputs",
              "set of signal names that crossed thresholds"),
    FieldSpec("candidate_type", "source_inferred", "medium",
              "observer lens scorer",
              "person | group | event | world (matches strongest_lens)"),
    FieldSpec("strongest_lens", "source_inferred", "medium",
              "observer lens scorer",
              "lens with maximum signal weight at this tick range"),
    FieldSpec("salience_score", "source_inferred", "medium",
              "observer salience aggregator",
              "integer score from signal weights"),
    FieldSpec("dominant_pressure", "source_inferred", "low",
              "observer pressure classifier",
              "may be 'none_clear' if no single pressure dominates"),
    FieldSpec("use_mode", "source_inferred", "medium",
              "curation policy thresholds",
              "story_ready | observation_only | low_activity_hold"),
    FieldSpec("related_candidate_ids", "source_inferred", "high",
              "observer relation linker",
              "IDs of other candidates linked by shared signal"),
)

WORLD_TICK_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("world.crowd_mood", "source_derived", "high",
              "observer.ticks[t].world.crowd_mood",
              "categorical mood at the candidate tick"),
    FieldSpec("world.blame_concentration", "source_derived", "high",
              "observer.ticks[t].world.blame_concentration"),
    FieldSpec("world.public_suspicion", "source_derived", "high",
              "observer.ticks[t].world.public_suspicion"),
    FieldSpec("world.authority_vigilance", "source_derived", "high",
              "observer.ticks[t].world.authority_vigilance"),
)

GROUP_TICK_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("groups[].dominant_mode", "source_derived", "high",
              "observer.ticks[t].groups[i].dominant_mode"),
    FieldSpec("groups[].tension", "source_derived", "high",
              "observer.ticks[t].groups[i].tension"),
    FieldSpec("groups[].member_count", "source_derived", "high",
              "observer.ticks[t].groups[i].member_count"),
)

AGENT_TICK_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("agents[].dominant_state", "source_derived", "high",
              "observer.ticks[t].agents[i].dominant_state"),
    FieldSpec("agents[].fear", "source_derived", "high",
              "observer.ticks[t].agents[i].fear"),
    FieldSpec("agents[].hope", "source_derived", "high",
              "observer.ticks[t].agents[i].hope"),
    FieldSpec("agents[].shame_self", "source_derived", "high",
              "observer.ticks[t].agents[i].shame_self"),
    FieldSpec("agents[].salient", "source_derived", "high",
              "observer.ticks[t].agents[i].salient"),
    FieldSpec("agents[].x", "source_derived", "high",
              "observer.ticks[t].agents[i].x",
              "engine canvas-space coordinate; not a tile"),
    FieldSpec("agents[].y", "source_derived", "high",
              "observer.ticks[t].agents[i].y"),
)

NOT_USED_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("synthetic_guard_movement", "not_used", "low",
              "(visual staging — frozen)",
              "would require Engine Event Log Adapter"),
    FieldSpec("walking_frame_timeline", "not_used", "low",
              "(visual staging — frozen)"),
    FieldSpec("speech_bubble_staging", "not_used", "low",
              "(visual staging — frozen)"),
    FieldSpec("tile_grid_position", "not_used", "low",
              "(visual staging — frozen)",
              "viewer maps to canvas coords, not tiles"),
    FieldSpec("hand_authored_cutscene_cues", "not_used", "low",
              "(visual staging — frozen)"),
)


# ---------------------------------------------------------------------------
# Build per-candidate ledger (one row per field-spec, with concrete value)
# ---------------------------------------------------------------------------

def _format_value(v: Any) -> str:
    if isinstance(v, list):
        if len(v) == 0:
            return "[]"
        if all(isinstance(x, (int, float, str, bool)) for x in v):
            return ", ".join(str(x) for x in v[:8]) + (f" (+{len(v)-8})" if len(v) > 8 else "")
        return f"[{len(v)} items]"
    if isinstance(v, float):
        return f"{v:.3f}"
    return str(v)


def _candidate_field_value(cand: dict[str, Any], spec: FieldSpec) -> str:
    if spec.name in cand:
        return _format_value(cand[spec.name])
    return "-"


def _world_field_value(world: dict[str, Any], spec: FieldSpec) -> str:
    key = spec.name.split(".", 1)[1]
    return _format_value(world.get(key, "-"))


def _group_summary_value(groups: list[dict[str, Any]], spec: FieldSpec) -> str:
    key = spec.name.split(".", 1)[1].replace("[]", "")
    if key.startswith("groups"):
        key = key[len("groups"):]
    # spec name like "groups[].dominant_mode" → key 'dominant_mode' after suffix split
    field = spec.name.split(".")[-1]
    parts = []
    for g in groups:
        v = g.get(field, "-")
        parts.append(f"{g.get('id','?')}={_format_value(v)}")
    return "; ".join(parts)


def _agent_summary_value(agents: list[dict[str, Any]], spec: FieldSpec) -> str:
    field = spec.name.split(".")[-1]
    if not agents:
        return "(no focal agents)"
    sample = agents[: min(3, len(agents))]
    parts = []
    for a in sample:
        v = a.get(field, "-")
        parts.append(f"{a.get('id','?')}={_format_value(v)}")
    if len(agents) > 3:
        parts.append(f"…(+{len(agents)-3})")
    return "; ".join(parts)


def build_candidate_ledger(observer: dict[str, Any],
                           cand: dict[str, Any]) -> list[dict[str, str]]:
    snap = bob.collect_snapshot(observer, cand)
    rows: list[dict[str, str]] = []

    def _row(spec: FieldSpec, value: str) -> dict[str, str]:
        return {
            "field": spec.name,
            "class": spec.cls,
            "confidence": spec.confidence,
            "source": spec.source,
            "value": value,
            "note": spec.note,
        }

    for spec in CANDIDATE_FIELDS:
        rows.append(_row(spec, _candidate_field_value(cand, spec)))
    for spec in WORLD_TICK_FIELDS:
        rows.append(_row(spec, _world_field_value(snap.world_at_tick, spec)))
    for spec in GROUP_TICK_FIELDS:
        rows.append(_row(spec, _group_summary_value(snap.groups_at_tick, spec)))
    for spec in AGENT_TICK_FIELDS:
        rows.append(_row(spec, _agent_summary_value(snap.focal_agents, spec)))
    for spec in NOT_USED_FIELDS:
        rows.append(_row(spec, "(excluded)"))

    return rows


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _render_ledger_table(rows: list[dict[str, str]]) -> str:
    head = "| field | class | confidence | source | value | note |\n" \
           "|---|---|---|---|---|---|"
    lines = [head]
    for r in rows:
        # escape pipes inside values
        val = r["value"].replace("|", "\\|")
        note = r["note"].replace("|", "\\|")
        lines.append(
            f"| `{r['field']}` | `{r['class']}` | {r['confidence']} | "
            f"{r['source']} | {val} | {note} |"
        )
    return "\n".join(lines)


def render(observer: dict[str, Any], run_label: str,
           include_holds: bool) -> tuple[str, dict[str, Any]]:
    modes = ("story_ready", "low_activity_hold") if include_holds else ("story_ready",)
    cands = bob.filter_candidates(observer, modes)

    sections = []
    json_payload = {
        "run_label": run_label,
        "schema_version": "provenance_table_v1",
        "modes": list(modes),
        "candidates": [],
    }

    # aggregate counts across all candidates
    agg = {"source_derived": 0, "source_inferred": 0, "not_used": 0}
    for cand in cands:
        rows = build_candidate_ledger(observer, cand)
        for r in rows:
            agg[r["class"]] += 1
        json_payload["candidates"].append({
            "candidate_id": cand["candidate_id"],
            "tick": cand["tick"],
            "use_mode": cand["use_mode"],
            "rows": rows,
        })
        sections.append(
            f"## {cand['candidate_id']} — tick {cand['tick']} "
            f"(`{cand['use_mode']}`)\n\n" + _render_ledger_table(rows)
        )

    total = sum(agg.values())
    pct = lambda n: (100.0 * n / total) if total else 0.0
    summary = (
        "## Field-class aggregate (all candidates included)\n\n"
        f"- Total field rows: **{total}**\n"
        f"- `source_derived`: **{agg['source_derived']}** ({pct(agg['source_derived']):.1f}%)\n"
        f"- `source_inferred`: **{agg['source_inferred']}** ({pct(agg['source_inferred']):.1f}%)\n"
        f"- `not_used`: **{agg['not_used']}** ({pct(agg['not_used']):.1f}%)\n"
    )

    head = f"""# WITNESS Provenance Table — {run_label}

> **Companion to**: [WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
> **Phase**: 12 — per-field provenance ledger.
> **Schema**: `provenance_table_v1`.

This document is a **flat field-level ledger**: every field reported on a
candidate (or actively excluded from this brief) gets a row stating its
provenance class and confidence. The brief itself is structured for
readability; this table is structured for verification.

## How to read

- **class** is one of:
  - `source_derived` — a direct readout from observer state.
  - `source_inferred` — a bounded rule applied over source signals.
  - `not_used` — a field that *would* have come from the visual layer
    and is intentionally excluded from this text-first brief.
- **confidence** is qualitative:
  - `high` — direct field readout, no aggregation.
  - `medium` — aggregation over a window or small set.
  - `low` — single classifier output gated by a policy threshold.
- **source** points to the ledger's origin. `observer.ticks[t].…` indexes
  by tick value via the safe lookup in `build_observer_brief.get_tick`.

The aggregate at the bottom counts field rows across all candidates in
this run. `source_derived` should dominate; `not_used` is a positive
signal that the brief is honestly excluding visual-only fields rather
than silently omitting them.

---

{summary}

---

"""

    md = head + "\n\n---\n\n".join(sections) + "\n\n---\n\n" + summary
    json_payload["aggregate"] = {
        "total_rows": total,
        "by_class": agg,
        "by_class_pct": {k: round(pct(v), 2) for k, v in agg.items()},
    }
    return md, json_payload


def main(in_path: str, out_md: str, run_label: str,
         include_holds: bool = False, out_json: str | None = None) -> None:
    observer = bob.load_observer(Path(in_path))
    md, payload = render(observer, run_label=run_label, include_holds=include_holds)
    out = Path(out_md)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"Wrote {out_md} ({len(md)} bytes, "
          f"{payload['aggregate']['total_rows']} field rows)")
    if out_json:
        outj = Path(out_json)
        outj.parent.mkdir(parents=True, exist_ok=True)
        outj.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                        encoding="utf-8")
        print(f"Wrote {out_json}")


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--in", dest="in_path",
                    default="data/visual/dot_observer_data.json")
    ap.add_argument("--out", dest="out_md",
                    default="docs/demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md")
    ap.add_argument("--json", dest="out_json", default=None)
    ap.add_argument("--run-label", default="peter_scarcity_baseline")
    ap.add_argument("--include-holds", action="store_true")
    ns = ap.parse_args()
    main(ns.in_path, ns.out_md, ns.run_label, ns.include_holds, ns.out_json)


if __name__ == "__main__":
    cli()
