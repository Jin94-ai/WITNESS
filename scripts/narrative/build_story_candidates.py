"""Build StoryCandidate cards — Stage 6 entry point.

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §6, §7.

Reads:
    data/narrative/story_threads.json     (Phase 3 output)
    data/narrative/moments.json           (Phase 1 output)
    data/visual/dot_observer_data.json    (anchor + agent metadata for IdentityResolver)
    content/{anchor_id}/identity_map.json (optional — Phase A enrichment)

Writes:
    data/narrative/story_candidates.json     (machine-readable ledger)
    docs/portfolio/STORY_CANDIDATES.md       (creator-facing cards)

Usage:
    python scripts/narrative/build_story_candidates.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.identity_resolver import IdentityResolver  # noqa: E402
from engine.observer.moment import Moment  # noqa: E402
from engine.observer.story_candidate import StoryCandidate  # noqa: E402
from engine.observer.story_candidate_builder import (  # noqa: E402
    build_story_candidates,
    serialize_candidates,
)
from engine.observer.thread import StoryThread  # noqa: E402


def _load_threads(p: Path) -> tuple[str, list[StoryThread]]:
    payload = json.loads(p.read_text(encoding="utf-8"))
    run_label = payload.get("run_label", "unknown")
    threads = []
    for d in payload.get("threads", []):
        threads.append(StoryThread(
            thread_id=d["thread_id"], title=d["title"],
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


def _load_moments(p: Path) -> list[Moment]:
    payload = json.loads(p.read_text(encoding="utf-8"))
    return [Moment.from_dict(d) for d in payload.get("moments", [])]


def _render_candidate_card(c: StoryCandidate) -> str:
    main_chars = ", ".join(c.main_characters) or "_(world-level)_"
    supporting = ", ".join(c.supporting_characters_or_groups) or "_(none)_"
    formats = ", ".join(f"`{f}`" for f in c.usable_formats) or "_(none)_"
    pressure_ctx = "; ".join(c.world_pressure_context) or "_(none)_"
    relationship = "\n".join(f"- {r}" for r in c.relationship_dynamics) or "_(none recorded)_"

    if c.key_turning_points:
        tp_rows = ["| Tick | Label | Provenance | Summary |",
                   "|---:|---|---|---|"]
        for tp in c.key_turning_points:
            summary = tp.summary.replace("|", "\\|")
            tp_rows.append(
                f"| {tp.tick} | {tp.label} | `{tp.provenance}` | {summary} |"
            )
        tp_block = "\n".join(tp_rows)
    else:
        tp_block = "_(no turning points selected)_"

    hooks_block = ""
    if c.adaptation_hooks:
        hook_lines = []
        for fmt, hook in c.adaptation_hooks.items():
            hook_lines.append(f"- **{fmt}**: {hook}")
        hooks_block = "\n".join(hook_lines)
    else:
        hooks_block = "_(no creative-use hooks for this conflict)_"

    risk_block = "\n".join(f"- {r}" for r in c.risk_notes)

    return f"""## {c.story_candidate_id} — {c.title}

> **source thread**: `{c.source_thread_id}` · **conflict**: `{c.core_conflict}`
> **main**: {main_chars} · **supporting / context**: {supporting}

### One-line premise

{c.one_line_premise}

### Arc summary

{c.arc_summary}

### Key turning points

{tp_block}

### Relationship dynamics

{relationship}

### World pressure context

{pressure_ctx}

### Unresolved question

> {c.unresolved_question}

### Adaptation hooks

{hooks_block}

### Evidence

{c.evidence_summary}
- provenance: source_derived={c.provenance_summary.get('source_derived',0)}, source_inferred={c.provenance_summary.get('source_inferred',0)}, not_used={c.provenance_summary.get('not_used',0)}

### Risk notes

{risk_block}
"""


def _render_brief(
    candidates: list[StoryCandidate],
    run_label: str,
) -> str:
    head = f"""# WITNESS Story Candidates — {run_label}

> *Stage 6 / Stage 7 output*. Each card below is a *creator-facing*
> abstraction over a `StoryThread`, built deterministically (no LLM)
> from source-derived moments, an IdentityResolver, and conflict-typed
> templates.
>
> **What this is**: a set of *story seeds* you can take into film, novel,
> game, or drama work. Each card states what the simulation produced
> — agent identity, pressure pattern, turning points, unresolved
> question — without writing the story itself.
>
> **What this is not**: completed prose, dialogue, screenplay, or any
> emotion-narrated content. See each card's *Risk notes* for explicit
> disclosures.

## Run summary

- candidates total: **{len(candidates)}**
- format coverage: { ', '.join(sorted({f for c in candidates for f in c.usable_formats})) or '(none)' }

---

"""
    body = "\n\n---\n\n".join(_render_candidate_card(c) for c in candidates) \
        if candidates else "_(no story candidates exceeded the threshold)_"

    tail = """

---

## Cross-reference

- Source threads: [data/narrative/story_threads.json](../../data/narrative/story_threads.json)
- Underlying moments: [data/narrative/moments.json](../../data/narrative/moments.json)
- Plan: [WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md](../WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md)
- Provenance ledger (per-field): [WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md](../demo/WITNESS_PROVENANCE_TABLE_PETER_SCARCITY.md)

*Generated by* `scripts/narrative/build_story_candidates.py`.
"""
    return head + body + tail


def main(in_threads: str, in_moments: str, in_observer: str,
         out_md: str, out_json: str) -> None:
    run_label, threads = _load_threads(Path(in_threads))
    moments = _load_moments(Path(in_moments))
    observer = json.loads(Path(in_observer).read_text(encoding="utf-8"))

    identity = IdentityResolver.from_observer(observer)
    candidates = build_story_candidates(threads, moments, identity)

    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text(_render_brief(candidates, run_label),
                            encoding="utf-8")

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    payload = serialize_candidates(candidates, run_label=run_label)
    Path(out_json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(
        f"Wrote {out_md} ({Path(out_md).stat().st_size} bytes)\n"
        f"Wrote {out_json}  total={len(candidates)}"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--threads", default="data/narrative/story_threads.json")
    ap.add_argument("--moments", default="data/narrative/moments.json")
    ap.add_argument("--observer", default="data/visual/dot_observer_data.json")
    ap.add_argument("--out-md", default="docs/portfolio/STORY_CANDIDATES.md")
    ap.add_argument("--out-json", default="data/narrative/story_candidates.json")
    ns = ap.parse_args()
    main(ns.threads, ns.moments, ns.observer, ns.out_md, ns.out_json)


if __name__ == "__main__":
    cli()
