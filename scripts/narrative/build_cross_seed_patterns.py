"""Build Cross-seed Story Patterns — Phase E.

Per `docs/WITNESS_STORY_EMERGENCE_IMPLEMENTATION_PLAN.md` §12 Phase E.

Pipeline:
  For each seed N in [0..K]:
      observer dump (data/visual/dot_observer_data_seed{N}.json, must exist)
        → moments
        → links
        → threads
        → story candidates (Phase A-C)
  Aggregate across seeds:
      → conflict frequency
      → main_character recurrence
      → robustness classification (robust / moderate / anomaly)

Outputs:
  data/narrative/cross_seed_story_patterns.json
  docs/portfolio/CROSS_SEED_STORY_PATTERNS.md

Usage:
  python scripts/narrative/build_cross_seed_patterns.py
  python scripts/narrative/build_cross_seed_patterns.py --seeds 0,1,2,3,4
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.cross_seed_pattern import (  # noqa: E402
    SeedRecord,
    build_cross_seed_report,
)
from engine.observer.identity_resolver import IdentityResolver  # noqa: E402
from engine.observer.moment_extractor import extract_moments  # noqa: E402
from engine.observer.story_candidate_builder import (  # noqa: E402
    build_story_candidates,
)
from engine.observer.thread_builder import (  # noqa: E402
    build_story_threads,
    link_moments,
)


def _run_pipeline_for_seed(observer_path: Path, seed: int) -> SeedRecord:
    observer = json.loads(observer_path.read_text(encoding="utf-8"))
    anchor_id = observer.get("meta", {}).get("anchor_id", "unknown")
    moments = extract_moments(observer)
    links = link_moments(moments)
    threads = build_story_threads(moments, links)
    identity = IdentityResolver.from_observer(observer)
    candidates = build_story_candidates(threads, moments, identity)
    return SeedRecord(
        seed=seed,
        run_label=f"{anchor_id}_seed{seed}",
        candidates=[c.to_dict() for c in candidates],
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _render_pattern_table(patterns) -> str:
    if not patterns:
        return "_(no patterns aggregated)_"
    rows = ["| Pattern | Seeds | Frequency | Robustness | Sample candidates |",
            "|---|---:|---:|---|---|"]
    for p in patterns:
        seeds = ", ".join(str(s) for s in p.seeds_present)
        cand_sample = ", ".join(p.candidate_ids[:3])
        if len(p.candidate_ids) > 3:
            cand_sample += f" (+{len(p.candidate_ids)-3})"
        rows.append(
            f"| `{p.pattern_value}` | {p.seed_count}/{p.total_seeds} ({seeds}) | "
            f"{p.seed_count / p.total_seeds:.2f} | "
            f"`{p.robustness}` | {cand_sample} |"
        )
    return "\n".join(rows)


def _render_brief(report) -> str:
    head = f"""# WITNESS Cross-seed Story Patterns — {report.anchor_id}

> *Phase E output*. Aggregates StoryCandidate sets across **{len(report.seeds)} seeds**
> ({', '.join(str(s) for s in report.seeds)}) of the same anchor.
>
> **What this answers**:
> - Which conflict families are *robust* vs *seed-specific*?
> - Which main characters recur across runs?
> - What does the simulation *consistently* surface vs surface only once?
>
> **What this is not**: an outcome distribution (REC/PARTIAL/SAT lives in
> the engine's outcome label). This is a *narrative pattern* aggregator —
> what kinds of stories emerge, not whether the run "succeeds".

## Run summary

- Anchor: `{report.anchor_id}`
- Seeds aggregated: **{len(report.seeds)}**
- Candidates per seed: { ', '.join(f'seed {s}={c}' for s, c in sorted(report.candidate_counts.items())) }
- Total patterns surfaced: **{len(report.conflict_patterns) + len(report.character_patterns)}**
- Robust patterns (≥80% of seeds): **{report.robust_count}**
- Anomaly patterns (one seed only): **{report.anomaly_count}**

---

## Conflict patterns (frequency by core_conflict)

{_render_pattern_table(report.conflict_patterns)}

**Reading**: a conflict labeled `robust` means the world's pressure
configuration produces this kind of story regardless of seed. An `anomaly`
means it surfaced only under one specific seed — interesting, but not
something to claim as a stable property of the simulation.

---

## Main character recurrence

{_render_pattern_table(report.character_patterns)}

**Reading**: a character flagged `robust` is named main in most seeds —
the simulation consistently surfaces them. Note: with the identity
map applied, the same agent_id maps to the same character across seeds,
so frequency here measures *which agent_id keeps becoming the main*,
not which character "should" be main.

---

## Honesty disclosures

- This aggregator does *not* re-run the simulation. It reads existing
  observer dumps `data/visual/dot_observer_data_seed*.json`. If those
  dumps are stale (e.g. seed source changed), the report is stale.
- Robustness thresholds (≥80% robust, ≥40% moderate, else anomaly) are
  configurable in `engine/observer/cross_seed_pattern.py`. Different
  thresholds yield different classifications.
- This report aggregates a *single anchor* across seeds. Cross-anchor
  comparison (peter vs vangogh vs talleyrand) is a separate question.

---

*Generated by* `scripts/narrative/build_cross_seed_patterns.py`.
"""
    return head


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(seeds: list[int], out_md: str, out_json: str,
         observer_template: str) -> None:
    seed_records: list[SeedRecord] = []
    anchor_id = "unknown"
    for s in seeds:
        path = Path(observer_template.format(seed=s))
        if not path.exists():
            print(f"WARN: {path} missing, skipping seed {s}", file=sys.stderr)
            continue
        rec = _run_pipeline_for_seed(path, s)
        seed_records.append(rec)
        # capture anchor from any record
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
            anchor_id = d.get("meta", {}).get("anchor_id", anchor_id)
        except Exception:
            pass

    if not seed_records:
        print("ERROR: no seeds processed — generate dumps first via "
              "scripts/visual/export_dot_observer_data.py --seed N", file=sys.stderr)
        sys.exit(1)

    report = build_cross_seed_report(seed_records, anchor_id=anchor_id)

    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text(_render_brief(report), encoding="utf-8")

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    s = report.to_dict()["summary"]
    print(
        f"Wrote {out_md}\n"
        f"Wrote {out_json}  patterns={s['total_patterns']} "
        f"(robust={s['robust']}, anomaly={s['anomaly']})"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--seeds", default="0,1,2,3,4",
                    help="Comma-separated seeds (default: 0,1,2,3,4)")
    ap.add_argument("--observer-template",
                    default="data/visual/dot_observer_data_seed{seed}.json",
                    help="Path template (use {seed} for seed substitution)")
    ap.add_argument("--out-md",
                    default="docs/portfolio/CROSS_SEED_STORY_PATTERNS.md")
    ap.add_argument("--out-json",
                    default="data/narrative/cross_seed_story_patterns.json")
    ns = ap.parse_args()
    seeds = [int(s) for s in ns.seeds.split(",") if s.strip()]
    main(seeds, ns.out_md, ns.out_json, ns.observer_template)


if __name__ == "__main__":
    cli()
