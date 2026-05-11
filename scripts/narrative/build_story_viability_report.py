"""Build complete Story Viability validation pack — Stages A-D + F + final report.

Per `docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md` §11, §14.

Single entry point that:
    Stage A: loads + normalizes StoryCandidates
    Stage B: builds Scene Briefs              → docs/portfolio/SCENE_BRIEFS.md
    Stage C: builds 1-page Treatments         → docs/portfolio/ONE_PAGE_TREATMENTS.md
    Stage D: scores viability                 → data/narrative/story_viability_scores.json
    Stage F: audits evidence discipline        → data/narrative/story_viability_audit.json
    Final:   integrated STORY_VIABILITY_REPORT.md

Stage E (Human Pick Test) is *human-driven* — guidance lives in the report
output itself.

Usage:
    python scripts/narrative/build_story_viability_report.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.observer.scene_brief import SceneBrief, build_scene_brief  # noqa: E402
from engine.observer.story_audit import (  # noqa: E402
    AuditResult, audit_pair, load_anchor_blocklist,
)
from engine.observer.story_candidate import StoryCandidate, TurningPoint  # noqa: E402
from engine.observer.story_viability import (  # noqa: E402
    ViabilityScore, score_candidate,
)
from engine.observer.treatment import Treatment, build_treatment  # noqa: E402


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _load_candidates(p: Path) -> tuple[str, list[StoryCandidate]]:
    payload = json.loads(p.read_text(encoding="utf-8"))
    run_label = payload.get("run_label", "unknown")
    out: list[StoryCandidate] = []
    for d in payload.get("candidates", []):
        tps = tuple(TurningPoint(
            tick=tp["tick"],
            moment_ids=tuple(tp.get("moment_ids", [])),
            label=tp.get("label", ""),
            summary=tp.get("summary", ""),
            provenance=tp.get("provenance", "source_inferred"),
        ) for tp in d.get("key_turning_points", []))
        out.append(StoryCandidate(
            story_candidate_id=d["story_candidate_id"],
            source_thread_id=d["source_thread_id"],
            title=d["title"],
            one_line_premise=d["one_line_premise"],
            main_characters=tuple(d.get("main_characters", [])),
            supporting_characters_or_groups=tuple(d.get("supporting_characters_or_groups", [])),
            core_conflict=d.get("core_conflict", "unknown"),
            arc_summary=d.get("arc_summary", ""),
            key_turning_points=tps,
            relationship_dynamics=tuple(d.get("relationship_dynamics", [])),
            world_pressure_context=tuple(d.get("world_pressure_context", [])),
            unresolved_question=d.get("unresolved_question", ""),
            usable_formats=tuple(d.get("usable_formats", [])),
            adaptation_hooks=dict(d.get("adaptation_hooks", {})),
            evidence_summary=d.get("evidence_summary", ""),
            provenance_summary=dict(d.get("provenance_summary", {})),
            risk_notes=tuple(d.get("risk_notes", [])),
        ))
    return run_label, out


def _load_cross_seed_freq(p: Path) -> dict[str, int]:
    """Map main_character display name → seed_count from cross-seed report."""
    if not p.exists():
        return {}
    payload = json.loads(p.read_text(encoding="utf-8"))
    out: dict[str, int] = {}
    for pat in payload.get("character_patterns", []):
        out[pat["pattern_value"]] = pat["seed_count"]
    return out


# ---------------------------------------------------------------------------
# Markdown rendering — Scene Briefs / Treatments / Final report
# ---------------------------------------------------------------------------

def _render_scene_brief(b: SceneBrief) -> str:
    ext = ", ".join(b.external_pressure) or "_(none)_"
    int_ = ", ".join(b.internal_pressure) or "_(none)_"
    sup = ", ".join(b.supporting_context) or "_(none)_"
    do_not = "\n".join(f"- {x}" for x in b.do_not_add)
    must = "\n".join(f"- {x}" for x in b.must_preserve)
    completeness_badge = (
        f"`{b.completeness}`"
        + (f" — missing: {', '.join(b.missing_fields)}" if b.missing_fields else "")
    )
    return f"""## Scene Brief — {b.candidate_id}

> completeness: {completeness_badge}
> source-derived: {b.source_derived_count} · source-inferred: {b.source_inferred_count}

### Core
- Main character: **{b.main_character}**
- Supporting / context: {sup}
- Core conflict: `{b.core_conflict}`
- Scene question: *{b.scene_question}*

### Situation
- External pressure: {ext}
- Internal pressure: {int_}
- Group / world context: {", ".join(b.group_world_context) or "_(none)_"}

### Progression
1. **Starting state** — {b.starting_state}
2. **Pressure enters** — {b.pressure_enters}
3. **Turning point** — {b.turning_point or "_(none — read end-state as pressure plateau)_"}
4. **Ending state** — {b.ending_state}

### Creative Constraint

**Do not add**:
{do_not}

**Must preserve**:
{must}
"""


def _render_treatment(t: Treatment) -> str:
    notes = "\n".join(f"- **{k}**: {v}" for k, v in t.adaptation_notes.items()) \
        or "_(no creative-use hooks for this conflict)_"
    completeness_badge = (
        f"`{t.treatment_completeness}`"
        + (f" — missing: {', '.join(t.missing_acts)}" if t.missing_acts else "")
    )
    return f"""## Treatment — {t.candidate_id}

> completeness: {completeness_badge}

### Premise

{t.premise}

### Act 1 — Setup

{t.act_1_setup}

### Act 2 — Pressure Build

{t.act_2_pressure_build}

### Act 3 — Turn / Consequence

{t.act_3_turn_consequence}

### End Hook

{t.end_hook}

### Adaptation Notes

{notes}
"""


def _render_final_report(
    run_label: str,
    pairs: list[tuple[StoryCandidate, SceneBrief, Treatment, ViabilityScore, AuditResult]],
) -> str:
    head = f"""# WITNESS Story Viability Report — {run_label}

> Stage A-F output (Story Viability Validation Plan).
>
> *What this answers*: Can each StoryCandidate be converted into a Scene
> Brief and a 1-page Treatment without inventing events / dialogue /
> locations? And does the result feel like a usable creator-facing seed?
>
> *What this does not do*: write the story. No prose, no dialogue, no
> screenplay. The forbidden surface is enforced by Stage F audit.

## 1. Summary

| Candidate | Score | Grade | Brief audit | Treatment audit | Overall |
|---|---:|---|---|---|---|
""" + "\n".join(
        f"| `{c.story_candidate_id}` `{c.title}` | {sc.score:.1f} | "
        f"`{sc.grade}` | `{ar.scene_brief_audit}` | `{ar.treatment_audit}` | `{ar.overall}` |"
        for c, _, _, sc, ar in pairs
    ) + "\n\n"

    # Strongest
    if pairs:
        strongest = max(pairs, key=lambda x: x[3].score)
        c0, b0, t0, sc0, ar0 = strongest
        head += f"""## 2. Strongest Candidate

**`{c0.story_candidate_id}` — {c0.title}** (score {sc0.score:.1f}, grade `{sc0.grade}`).

- Premise: *{c0.one_line_premise}*
- Audit: `{ar0.overall}` ({len(ar0.violations)} violations, {len(ar0.risky_phrases)} risky phrases)
- Top scoring factors: {", ".join(f"{k}={v:.2f}" for k, v in sorted(sc0.factor_breakdown.items(), key=lambda x: -x[1])[:3])}

"""
    head += "## 3. Candidate-by-Candidate Review\n\n"
    for c, b, t, sc, ar in pairs:
        violations = ", ".join(f"`{v.phrase}`" for v in ar.violations) or "(none)"
        risky = ", ".join(f"`{r.phrase}`" for r in ar.risky_phrases) or "(none)"
        notes = "\n".join(f"  - {n}" for n in sc.notes) or "  - (none)"
        head += f"""### {c.story_candidate_id} — {c.title}

- **Score**: {sc.score:.1f}  /  **Grade**: `{sc.grade}`
- **Brief completeness**: `{b.completeness}`  · missing: {', '.join(b.missing_fields) or '(none)'}
- **Treatment completeness**: `{t.treatment_completeness}`  · missing: {', '.join(t.missing_acts) or '(none)'}
- **Audit**: brief=`{ar.scene_brief_audit}`, treatment=`{ar.treatment_audit}`, overall=`{ar.overall}`
- **Violations**: {violations}
- **Risky phrases**: {risky}
- **Score notes**:
{notes}
- **Recommended use**: see scene brief at [SCENE_BRIEFS.md#{c.story_candidate_id.lower()}](SCENE_BRIEFS.md) and treatment at [ONE_PAGE_TREATMENTS.md#{c.story_candidate_id.lower()}](ONE_PAGE_TREATMENTS.md)

"""

    # Decision
    n_strong = sum(1 for _, _, _, sc, _ in pairs if sc.grade == "strong_viable")
    n_viable = sum(1 for _, _, _, sc, _ in pairs if sc.grade == "viable_with_gaps")
    n_audit_fail = sum(1 for _, _, _, _, ar in pairs if ar.overall == "audit_fail")
    n_not_viable = sum(1 for _, _, _, sc, _ in pairs if sc.grade == "not_viable")

    if (n_strong >= 1 or n_viable >= 2) and n_audit_fail == 0:
        decision = "**SHIP** — at least one strong_viable or two viable_with_gaps, zero audit_fail."
    elif n_not_viable == len(pairs):
        decision = "**DROP / REFRAME** — all candidates not_viable. Reposition as 'Simulation Pattern Mining Tool'."
    else:
        decision = "**IMPROVE** — most candidates are weak_seed; consider StoryCandidate enrichment."

    head += f"""## 4. Stage E — Human Pick Test (manual)

This stage is *not automated*. Per plan §9, ask 3+ reviewers:

1. Could you actually write a scene / episode / quest from this? (1–5)
2. Which candidate would you pick first?
3. Why that one?
4. What information is missing?
5. Which sentence reads as data, not story?
6. Where do you see forced "story-ification"?
7. Best medium for this candidate? film / novel / game / none

**Pass criteria** (per candidate):
- avg of question 1 ≥ 0.70 of 5 (i.e. ≥ 3.5/5)
- selection_rate ≥ 1/3
- no major over-inference complaint

Use the strongest candidate above as the *first* show item.

## 5. Evidence Audit Result

- Total candidates: {len(pairs)}
- audit_fail: {n_audit_fail}
- risky (no fail): {sum(1 for _, _, _, _, ar in pairs if ar.overall == 'risky')}
- pass: {sum(1 for _, _, _, _, ar in pairs if ar.overall == 'pass')}

## 6. Decision

{decision}

## 7. Honesty disclosures

- This report scores *viability* (could you write a scene?), not narrative quality.
- All sentences are deterministic templates over source-derived candidate fields.
- Stage F audit is keyword-based — it catches obvious dialogue/screenplay markers and a finite list of risky verbs. A new violation pattern requires updating `engine/observer/story_audit.py`.
- Cross-seed robustness factor only fires when `cross_seed_story_patterns.json` is present.
- Human Pick Test is *required* for the top-line claim ("yes, this is usable"). Without it, the score is system self-assessment only.

---

*Generated by* `scripts/narrative/build_story_viability_report.py`.
"""
    return head


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(in_cands: str, in_xs: str,
         out_briefs: str, out_treatments: str,
         out_scores_json: str, out_audit_json: str,
         out_report_md: str) -> None:
    run_label, candidates = _load_candidates(Path(in_cands))
    cross_seed_freq_by_name = _load_cross_seed_freq(Path(in_xs))
    # Load anchor-specific audit blocklist (optional)
    blocklist = load_anchor_blocklist(run_label)

    pairs: list[tuple[StoryCandidate, SceneBrief, Treatment, ViabilityScore, AuditResult]] = []
    for c in candidates:
        brief = build_scene_brief(c)
        treatment = build_treatment(c, brief)
        # Look up cross-seed frequency by main character name
        freq: int | None = None
        if c.main_characters:
            freq = cross_seed_freq_by_name.get(c.main_characters[0])
        sc = score_candidate(c, brief, treatment, cross_seed_frequency=freq)
        audit = audit_pair(brief, treatment, extra_blocklist=blocklist)
        pairs.append((c, brief, treatment, sc, audit))

    # Stage B output
    Path(out_briefs).parent.mkdir(parents=True, exist_ok=True)
    Path(out_briefs).write_text(
        f"# WITNESS Scene Briefs — {run_label}\n\n"
        + "\n\n---\n\n".join(_render_scene_brief(b) for _, b, _, _, _ in pairs),
        encoding="utf-8",
    )
    # Stage C output
    Path(out_treatments).write_text(
        f"# WITNESS 1-page Treatments — {run_label}\n\n"
        + "\n\n---\n\n".join(_render_treatment(t) for _, _, t, _, _ in pairs),
        encoding="utf-8",
    )
    # Stage D output
    Path(out_scores_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_scores_json).write_text(
        json.dumps({
            "run_label": run_label,
            "schema_version": "story_viability_scores_v1",
            "scores": [sc.to_dict() for _, _, _, sc, _ in pairs],
        }, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    # Stage F output
    Path(out_audit_json).write_text(
        json.dumps({
            "run_label": run_label,
            "schema_version": "story_viability_audit_v1",
            "audits": [ar.to_dict() for _, _, _, _, ar in pairs],
        }, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    # Final integrated report
    Path(out_report_md).write_text(
        _render_final_report(run_label, pairs), encoding="utf-8",
    )

    n_strong = sum(1 for _, _, _, sc, _ in pairs if sc.grade == "strong_viable")
    n_viable = sum(1 for _, _, _, sc, _ in pairs if sc.grade == "viable_with_gaps")
    n_audit_fail = sum(1 for _, _, _, _, ar in pairs if ar.overall == "audit_fail")
    print(
        f"Wrote 5 outputs:\n"
        f"  {out_briefs}\n  {out_treatments}\n  {out_scores_json}\n"
        f"  {out_audit_json}\n  {out_report_md}\n"
        f"Total: {len(pairs)} candidates  strong={n_strong}  "
        f"viable_with_gaps={n_viable}  audit_fail={n_audit_fail}"
    )


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates", default="data/narrative/story_candidates.json")
    ap.add_argument("--cross-seed",
                    default="data/narrative/cross_seed_story_patterns.json")
    ap.add_argument("--out-briefs",
                    default="docs/portfolio/SCENE_BRIEFS.md")
    ap.add_argument("--out-treatments",
                    default="docs/portfolio/ONE_PAGE_TREATMENTS.md")
    ap.add_argument("--out-scores",
                    default="data/narrative/story_viability_scores.json")
    ap.add_argument("--out-audit",
                    default="data/narrative/story_viability_audit.json")
    ap.add_argument("--out-report",
                    default="docs/portfolio/STORY_VIABILITY_REPORT.md")
    ns = ap.parse_args()
    main(
        ns.candidates, ns.cross_seed,
        ns.out_briefs, ns.out_treatments,
        ns.out_scores, ns.out_audit, ns.out_report,
    )


if __name__ == "__main__":
    cli()
