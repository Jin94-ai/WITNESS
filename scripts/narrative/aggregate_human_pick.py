"""Aggregate Human Pick Test responses — Stage E (Story Viability Validation).

Per `docs/WITNESS_STORY_VIABILITY_VALIDATION_PLAN.md` §9.

Reads `data/narrative/human_pick_responses.json` (filled by reviewers via
HUMAN_PICK_TEST_PACK.md) and emits:

    data/narrative/human_pick_results.json   — machine-readable
    docs/portfolio/HUMAN_PICK_RESULT.md      — human-readable

Per-candidate pass criteria (plan §9):
    human_pick_score = mean(q1) / 5   ≥ 0.70
    selection_rate   = picks / reviewers ≥ 0.33
    no major over-inference complaint

Usage:
    python scripts/narrative/aggregate_human_pick.py
    python scripts/narrative/aggregate_human_pick.py \\
        --input data/narrative/human_pick_responses.json \\
        --out-md docs/portfolio/HUMAN_PICK_RESULT.md \\
        --out-json data/narrative/human_pick_results.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


# Plan §9 thresholds
THRESHOLD_AVG_Q1   = 3.5    # /5
THRESHOLD_PICK_RATE = 1 / 3  # ≥ 1/3 of reviewers picked it
OVER_INFERENCE_REPEAT_THRESHOLD = 2  # same complaint from ≥2 reviewers


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def _candidate_ids_from(responses: dict) -> list[str]:
    """Discover which candidate IDs reviewers actually answered."""
    ids: set[str] = set()
    for r in responses.get("reviewers", []):
        ids.update(r.get("responses", {}).keys())
    return sorted(ids)


def _q6_overlap(reviewers: list[dict], candidate_id: str) -> list[str]:
    """Find Q6 (over-inference complaint) phrases that appear in ≥ N reviewers
    for the same candidate. Naive substring match on lowercase."""
    raw = []
    for r in reviewers:
        text = r.get("responses", {}).get(candidate_id, {}).get("q6") or ""
        text = text.strip().lower()
        if text:
            raw.append(text)
    if len(raw) < OVER_INFERENCE_REPEAT_THRESHOLD:
        return []
    # Find "common substring" — split into tokens, count tokens appearing in ≥2 responses
    token_to_reviewers: dict[str, set[int]] = {}
    for i, t in enumerate(raw):
        tokens = {tok.strip(".,;:?!\"'()") for tok in t.split() if len(tok) > 4}
        for tok in tokens:
            token_to_reviewers.setdefault(tok, set()).add(i)
    repeats = [t for t, s in token_to_reviewers.items()
               if len(s) >= OVER_INFERENCE_REPEAT_THRESHOLD]
    return sorted(repeats)


def aggregate(responses: dict) -> dict:
    reviewers = responses.get("reviewers", [])
    n = len(reviewers)
    candidate_ids = _candidate_ids_from(responses)

    per_candidate: dict[str, dict] = {}
    pick_counter: Counter = Counter()
    medium_counter: dict[str, Counter] = {cid: Counter() for cid in candidate_ids}

    for r in reviewers:
        top = r.get("q2_top_pick")
        if top:
            pick_counter[top] += 1

    for cid in candidate_ids:
        q1_scores = []
        for r in reviewers:
            resp = r.get("responses", {}).get(cid, {})
            q1 = resp.get("q1")
            if isinstance(q1, (int, float)):
                q1_scores.append(float(q1))
            q7 = (resp.get("q7") or "").strip().lower()
            if q7:
                medium_counter[cid][q7] += 1

        avg_q1 = sum(q1_scores) / len(q1_scores) if q1_scores else 0.0
        human_pick_score = avg_q1 / 5.0
        picks = pick_counter[cid]
        sel_rate = picks / n if n else 0.0

        repeat_complaints = _q6_overlap(reviewers, cid)
        over_inference_repeated = len(repeat_complaints) > 0

        passes_q1   = avg_q1 >= THRESHOLD_AVG_Q1
        passes_pick = sel_rate >= THRESHOLD_PICK_RATE
        passes_q6   = not over_inference_repeated
        overall_pass = passes_q1 and passes_pick and passes_q6

        per_candidate[cid] = {
            "candidate_id": cid,
            "n_responses": len(q1_scores),
            "avg_q1": round(avg_q1, 2),
            "human_pick_score": round(human_pick_score, 3),
            "picks": picks,
            "selection_rate": round(sel_rate, 3),
            "medium_distribution": dict(medium_counter[cid]),
            "repeat_complaints": repeat_complaints,
            "passes_q1": passes_q1,
            "passes_pick_rate": passes_pick,
            "passes_complaint_check": passes_q6,
            "overall_pass": overall_pass,
        }

    n_pass = sum(1 for v in per_candidate.values() if v["overall_pass"])
    return {
        "schema_version": "human_pick_results_v1",
        "anchor_id": responses.get("_meta", {}).get("anchor_id", "unknown"),
        "n_reviewers": n,
        "candidates": per_candidate,
        "summary": {
            "candidates_total": len(candidate_ids),
            "candidates_passing": n_pass,
            "thresholds": {
                "avg_q1_min": THRESHOLD_AVG_Q1,
                "selection_rate_min": THRESHOLD_PICK_RATE,
                "complaint_repeat_threshold": OVER_INFERENCE_REPEAT_THRESHOLD,
            },
        },
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_md(result: dict, raw_responses: dict) -> str:
    n = result["n_reviewers"]
    s = result["summary"]
    head = f"""# WITNESS — Human Pick Test Result

> Stage E aggregator output. Plan §9 thresholds: avg_q1 ≥ 3.5/5, selection_rate ≥ 1/3, no repeated over-inference complaint.

## Run summary

- Anchor: `{result['anchor_id']}`
- Reviewers: **{n}**
- Candidates evaluated: **{s['candidates_total']}**
- Candidates passing all 3 criteria: **{s['candidates_passing']}/{s['candidates_total']}**

---

## Per-candidate result

| Candidate | n | avg Q1 | pick rate | repeated complaints | overall |
|---|---:|---:|---:|---|---|
"""
    rows = []
    for cid, r in result["candidates"].items():
        avg_str = f"{r['avg_q1']}" if r["n_responses"] else "—"
        pick_str = f"{r['picks']}/{n} ({r['selection_rate']*100:.0f}%)"
        complaints = ", ".join(f"`{c}`" for c in r["repeat_complaints"][:5]) or "—"
        overall = "✅ PASS" if r["overall_pass"] else "❌ fail"
        rows.append(
            f"| `{cid}` | {r['n_responses']} | {avg_str} | {pick_str} | {complaints} | {overall} |"
        )
    head += "\n".join(rows) + "\n\n"

    # Per-candidate detail
    head += "## Detail\n\n"
    for cid, r in result["candidates"].items():
        passes = []
        if r["passes_q1"]:   passes.append(f"Q1 avg `{r['avg_q1']}` ≥ {THRESHOLD_AVG_Q1}")
        else:                passes.append(f"Q1 avg `{r['avg_q1']}` < {THRESHOLD_AVG_Q1} ❌")
        if r["passes_pick_rate"]: passes.append(f"selection {r['selection_rate']*100:.0f}% ≥ {THRESHOLD_PICK_RATE*100:.0f}%")
        else:                     passes.append(f"selection {r['selection_rate']*100:.0f}% < {THRESHOLD_PICK_RATE*100:.0f}% ❌")
        if r["passes_complaint_check"]: passes.append("no repeated over-inference complaint")
        else:                            passes.append(f"repeated complaint: {', '.join(r['repeat_complaints'][:3])} ❌")

        medium_dist = r["medium_distribution"]
        medium_str = ", ".join(f"{m}={c}" for m, c in
                                sorted(medium_dist.items(), key=lambda x: -x[1])) or "(none)"

        head += f"""### {cid}

- **Overall**: {'✅ PASS' if r['overall_pass'] else '❌ fail'}
- {' · '.join(passes)}
- Best-fit medium distribution: {medium_str}
- n responses: {r['n_responses']} (of {n} reviewers)

"""

    # Decision (plan §15)
    head += "## Decision (Plan §9 + §15)\n\n"
    n_pass = s["candidates_passing"]
    if n_pass >= 1:
        head += f"**SHIP** — {n_pass} candidate(s) passed all 3 Stage E criteria.\n\n"
    else:
        head += "**Review needed** — no candidate passed all 3 criteria. Possible actions:\n\n" \
                "- More reviewers (current sample may be too small)\n" \
                "- Calibrate auto-score weights against human signal\n" \
                "- Re-examine premise / arc templates for the failing candidates\n\n"

    # Reviewer notes
    if raw_responses.get("reviewers"):
        head += "## Reviewer notes (Q3 — pick reasons)\n\n"
        for r in raw_responses["reviewers"]:
            top = r.get("q2_top_pick")
            reason = (r.get("q3_pick_reason") or "").strip()
            if top and reason:
                head += f"- **{r.get('id', '?')}** picked `{top}` — {reason}\n"
        head += "\n"

    head += "\n---\n\n*Generated by* `scripts/narrative/aggregate_human_pick.py`.\n"
    return head


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(in_path: str, out_md: str, out_json: str) -> int:
    p = Path(in_path)
    if not p.exists():
        print(f"ERROR: {in_path} not found.", file=sys.stderr)
        print(
            "Copy data/narrative/human_pick_responses_template.json to "
            "data/narrative/human_pick_responses.json, fill in reviewer "
            "responses, then re-run.", file=sys.stderr,
        )
        return 1

    responses = json.loads(p.read_text(encoding="utf-8"))
    # Filter out reviewers with no q1 answers (template stubs)
    filtered = []
    for r in responses.get("reviewers", []):
        any_q1 = any(
            isinstance(resp.get("q1"), (int, float))
            for resp in r.get("responses", {}).values()
        )
        if any_q1:
            filtered.append(r)
    responses["reviewers"] = filtered

    if not filtered:
        print(
            "ERROR: no reviewer has filled q1. Template stubs only — fill in "
            "responses before aggregating.", file=sys.stderr,
        )
        return 1

    result = aggregate(responses)
    md = render_md(result, responses)

    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text(md, encoding="utf-8")
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    s = result["summary"]
    print(
        f"Wrote {out_md}\n"
        f"Wrote {out_json}\n"
        f"Reviewers: {result['n_reviewers']}  "
        f"Candidates passing: {s['candidates_passing']}/{s['candidates_total']}"
    )
    return 0


def cli() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--input",
                    default="data/narrative/human_pick_responses.json")
    ap.add_argument("--out-md",
                    default="docs/portfolio/HUMAN_PICK_RESULT.md")
    ap.add_argument("--out-json",
                    default="data/narrative/human_pick_results.json")
    ns = ap.parse_args()
    sys.exit(main(ns.input, ns.out_md, ns.out_json))


if __name__ == "__main__":
    cli()
