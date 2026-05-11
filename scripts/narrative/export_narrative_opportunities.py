"""Export Narrative Opportunities — Phase 4 entry point.

Per `docs/WITNESS_NARRATIVE_MINING_PLAN.md` §9.

Reads:
    data/narrative/story_threads.json    (Phase 3 output)
    data/narrative/moments.json          (Phase 1 output, for evidence rows)

Writes:
    docs/portfolio/NARRATIVE_OPPORTUNITIES.md
    data/narrative/narrative_opportunities.json

The Markdown output is the *creator-facing* artifact. The JSON output is
machine-readable so downstream tools (HTML console, etc.) can consume it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.moment import Moment  # noqa: E402
from engine.observer.thread import StoryThread  # noqa: E402
from engine.observer.narrative_opportunity import (  # noqa: E402
    from_thread,
    NarrativeOpportunity,
)


def _load_threads(path: Path) -> tuple[str, list[StoryThread]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    run_label = payload.get("run_label", "unknown")
    # StoryThread expects tuples — convert lists in dicts
    threads: list[StoryThread] = []
    for d in payload["threads"]:
        threads.append(StoryThread(
            thread_id=d["thread_id"],
            title=d["title"],
            main_agents=tuple(d.get("main_agents", [])),
            supporting_agents=tuple(d.get("supporting_agents", [])),
            groups=tuple(d.get("groups", [])),
            core_conflict=d.get("core_conflict", "unknown"),
            arc_direction=d.get("arc_direction", "unknown"),
            moment_ids=tuple(d.get("moment_ids", [])),
            start_tick=d.get("start_tick", 0),
            end_tick=d.get("end_tick", 0),
            pressure_history=tuple(d.get("pressure_history", [])),
            relationship_drift=tuple(d.get("relationship_drift", [])),
            unresolved_question=d.get("unresolved_question", ""),
            story_potential_score=d.get("story_potential_score", 0.0),
            usable_as=tuple(d.get("usable_as", [])),
            provenance=d.get("provenance", "source_inferred"),
        ))
    return run_label, threads


def _load_moments(path: Path) -> dict[str, Moment]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {d["moment_id"]: Moment.from_dict(d) for d in payload["moments"]}


def _render_evidence_table(moments: dict[str, Moment], thread: StoryThread) -> str:
    rows = ["| Tick | Moment | Type | Provenance | Summary |",
            "|---:|---|---|---|---|"]
    seen = set()
    for mid in thread.moment_ids:
        m = moments.get(mid)
        if not m or m.moment_id in seen:
            continue
        seen.add(m.moment_id)
        summary = m.summary.replace("|", "\\|")
        rows.append(
            f"| {m.tick} | `{m.moment_id}` | `{m.moment_type}` | "
            f"`{m.provenance}` | {summary} |"
        )
    if len(rows) == 2:
        rows.append("| — | _(no resolved moments)_ | | | |")
    return "\n".join(rows)


def _render_opportunity_card(
    opp: NarrativeOpportunity,
    thread: StoryThread,
    moments: dict[str, Moment],
) -> str:
    creative = ", ".join(f"`{u}`" for u in opp.creative_uses) if opp.creative_uses else "_(none)_"
    pressures = ", ".join(f"`{p}`" for p in thread.pressure_history) or "_(none)_"
    relationships = ", ".join(thread.relationship_drift) or "_(none recorded)_"
    main = ", ".join(opp.main_agents) or "_(world-level)_"
    groups = ", ".join(opp.groups) or "_(none)_"

    return f"""## {opp.thread_id} — {opp.title}

- **rank**: `{opp.rank}` (score `{opp.score:.3f}`)
- **core conflict**: `{opp.core_conflict}`
- **arc direction**: `{opp.arc_direction}`
- **main agents**: {main}
- **groups**: {groups}
- **tick span**: {opp.start_tick} → {opp.end_tick} ({opp.moment_count} moments)
- **pressure history**: {pressures}
- **relationship drift**: {relationships}
- **creative uses**: {creative}

### Logline

{opp.logline}

### Unresolved Question

{opp.unresolved_question}

### Evidence

{_render_evidence_table(moments, thread)}

### Provenance Note

This opportunity is `source_inferred` — assembled by linking source-derived
moments through deterministic rules (no LLM). Each evidence row above
carries its own per-moment provenance class.
"""


def _render_brief(
    opps: list[NarrativeOpportunity],
    threads: list[StoryThread],
    moments: dict[str, Moment],
    run_label: str,
) -> str:
    by_id = {t.thread_id: t for t in threads}
    counts: dict[str, int] = {"strong": 0, "usable": 0, "weak": 0, "hold": 0}
    for o in opps:
        counts[o.rank] = counts.get(o.rank, 0) + 1

    head = f"""# WITNESS Narrative Opportunities — {run_label}

> *Companion artifacts*:
> - Brief: [WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md](../demo/WITNESS_OBSERVER_BRIEF_PETER_SCARCITY.md)
> - Per-field provenance: [WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)
> - Plan: [WITNESS_NARRATIVE_MINING_PLAN.md](../WITNESS_NARRATIVE_MINING_PLAN.md)

## Run Context

- **Run label**: `{run_label}`
- **Threads found**: **{len(opps)}**
- **Strong opportunities** (score ≥ 0.80): **{counts['strong']}**
- **Usable threads** (0.60 ≤ score < 0.80): {counts['usable']}
- **Weak threads** (0.40 ≤ score < 0.60): {counts['weak']}
- **Hold** (score < 0.40): {counts['hold']}

## How to read this document

Each card below is a *narrative opportunity* — a sequence of source-derived
moments connected by deterministic rules into a candidate story. The card
states:

- **What it is** (logline + arc + core conflict).
- **Why it qualifies** (score factors + evidence rows).
- **What it could become** (creative_uses tags).
- **What is not resolved** (unresolved_question).

This document does *not* write the story. It surfaces the seed and the
evidence so a creator can choose which thread to develop.

---

"""

    cards = "\n\n---\n\n".join(
        _render_opportunity_card(o, by_id[o.thread_id], moments) for o in opps
    ) if opps else "_(no opportunities exceeded the inclusion threshold)_"

    tail = """

---

## Honesty disclosures

- Each thread's data layer (StoryThread) carries technical evidence; this
  layer adds a creator-facing logline and rank.
- Conflict labels and arc labels are `source_inferred` — they apply
  deterministic rules to source-derived moment data. Different rule sets
  could produce different labels.
- `creative_uses` tags are *suggestions*, not commitments. The thread does
  not become a film/novel/game by itself; it is a seed.
- `score` is a relative ranking within this run. Cross-run comparison is
  only meaningful with the same threshold configuration.

*Generated by* `scripts/narrative/export_narrative_opportunities.py`.
"""
    return head + cards + tail


def main(in_threads: str, in_moments: str,
         out_md: str, out_json: str) -> None:
    run_label, threads = _load_threads(Path(in_threads))
    moments = _load_moments(Path(in_moments))
    opps = [from_thread(t) for t in threads]

    # Sort by descending score for the markdown output
    opps_sorted = sorted(opps, key=lambda o: -o.score)

    md = _render_brief(opps_sorted, threads, moments, run_label)
    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text(md, encoding="utf-8")

    payload: dict[str, Any] = {
        "run_label": run_label,
        "schema_version": "narrative_opportunities_v1",
        "summary": {
            "threads_total": len(opps),
            "strong_opportunities": sum(1 for o in opps if o.rank == "strong"),
            "usable_threads": sum(1 for o in opps if o.rank == "usable"),
            "weak_threads": sum(1 for o in opps if o.rank == "weak"),
            "hold_threads": sum(1 for o in opps if o.rank == "hold"),
        },
        "opportunities": [o.to_dict() for o in opps_sorted],
    }
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    s = payload["summary"]
    print(
        f"Wrote {out_md} ({len(md)} bytes)\n"
        f"Wrote {out_json}  total={s['threads_total']} "
        f"(strong={s['strong_opportunities']}, usable={s['usable_threads']}, "
        f"weak={s['weak_threads']}, hold={s['hold_threads']})"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--threads", default="data/narrative/story_threads.json")
    ap.add_argument("--moments", default="data/narrative/moments.json")
    ap.add_argument("--out-md",
                    default="docs/portfolio/NARRATIVE_OPPORTUNITIES.md")
    ap.add_argument("--out-json",
                    default="data/narrative/narrative_opportunities.json")
    ns = ap.parse_args()
    main(ns.threads, ns.moments, ns.out_md, ns.out_json)


if __name__ == "__main__":
    cli()
