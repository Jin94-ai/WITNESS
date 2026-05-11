"""Phase G Step G3 — distribution analysis on reference rubric scores.

Reads data/reference/evaluation_results.json (produced by G2) and emits:
  data/reference/distribution_analysis.json
  docs/person/V3_REFERENCE_DISTRIBUTION_REPORT.md

Each category × 4 score axis: min / q1 / median / q3 / max / mean / stdev +
coarse histogram (10 bins).
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

SCORE_KEYS = [
    "character_composite",
    "canon_soft_drift",
    "causal_smoothness",
    "novelty_drift",
]


def percentile(values: list[float], p: float) -> float:
    """Linear interpolation percentile (p in [0, 100])."""
    if not values:
        return float("nan")
    vs = sorted(values)
    if p <= 0:
        return vs[0]
    if p >= 100:
        return vs[-1]
    k = (len(vs) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(vs) - 1)
    if f == c:
        return vs[f]
    return vs[f] + (vs[c] - vs[f]) * (k - f)


def describe(values: list[float]) -> dict:
    if not values:
        return {k: float("nan") for k in (
            "min", "q1", "median", "q3", "max", "mean", "stdev",
        )}
    return {
        "min": min(values),
        "q1": percentile(values, 25),
        "median": statistics.median(values),
        "q3": percentile(values, 75),
        "max": max(values),
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "n": len(values),
    }


def histogram(values: list[float], bins: int = 10) -> dict:
    if not values:
        return {"bins": [], "counts": []}
    lo, hi = min(values), max(values)
    if lo == hi:
        return {"bins": [lo, hi], "counts": [len(values)]}
    width = (hi - lo) / bins
    edges = [lo + i * width for i in range(bins + 1)]
    counts = [0] * bins
    for v in values:
        idx = min(int((v - lo) / width), bins - 1)
        counts[idx] += 1
    return {"bins": edges, "counts": counts}


def analyze(eval_results: list[dict]) -> dict:
    by_cat: dict[str, list[dict]] = {
        "canonical_like": [],
        "plausible_alternative": [],
        "obvious_noise": [],
        "noise_level_1": [],
        "noise_level_2": [],
        "noise_level_3": [],
    }
    for r in eval_results:
        by_cat[r["category"]].append(r)
        if r["category"] == "obvious_noise" and r.get("noise_level"):
            by_cat[f"noise_level_{r['noise_level']}"].append(r)

    out: dict = {}
    for cat_name, results in by_cat.items():
        cat_data = {"n": len(results)}
        for key in SCORE_KEYS:
            vals = [r["scores"][key] for r in results]
            cat_data[key] = {
                "stats": describe(vals),
                "histogram": histogram(vals, bins=10),
                "values": sorted(vals),
            }
        # Additional: canon_valid rate, novelty_band distribution
        cat_data["canon_valid_rate"] = (
            sum(1 for r in results if r["scores"]["canon_valid"]) / len(results)
            if results else 0.0
        )
        cat_data["novelty_band_counts"] = dict(Counter(
            r["scores"]["novelty_band"] for r in results
        ))
        cat_data["discovery_class_counts"] = dict(Counter(
            r["discovery_class"] for r in results
        ))
        out[cat_name] = cat_data
    return out


# =============================================================================
# Report writer
# =============================================================================

def fmt_stats(s: dict) -> str:
    return (
        f"min={s['min']:.2f}  q1={s['q1']:.2f}  med={s['median']:.2f}  "
        f"q3={s['q3']:.2f}  max={s['max']:.2f}  "
        f"mean={s['mean']:.2f}±{s['stdev']:.2f}"
    )


def write_report(analysis: dict, thresholds: dict, out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# V3 Reference Distribution Report (Phase G Step G3)\n")
    lines.append(f"**Generated:** 2026-04-23\n")
    lines.append("**Source:** `data/reference/evaluation_results.json` (45 trajectories)\n")
    lines.append("")
    lines.append("**Current evaluator thresholds:**")
    for k, v in thresholds.items():
        lines.append(f"- `{k}` = {v}")
    lines.append("")
    lines.append("---")

    # Section 1: Per-axis distribution table
    lines.append("\n## 1. Score distribution by category\n")
    for key in SCORE_KEYS:
        lines.append(f"\n### {key}\n")
        lines.append("| category | n | min | q1 | median | q3 | max | mean ± stdev |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for cat in (
            "canonical_like", "plausible_alternative", "obvious_noise",
            "noise_level_1", "noise_level_2", "noise_level_3",
        ):
            s = analysis[cat][key]["stats"]
            if s.get("n", 0) == 0:
                continue
            lines.append(
                f"| {cat} | {s['n']} | {s['min']:.2f} | {s['q1']:.2f} | "
                f"{s['median']:.2f} | {s['q3']:.2f} | {s['max']:.2f} | "
                f"{s['mean']:.2f} ± {s['stdev']:.2f} |"
            )

    # Section 2: canon_valid + novelty_band
    lines.append("\n## 2. Canon valid + novelty band\n")
    lines.append("| category | n | canon_valid_rate | novelty_band counts |")
    lines.append("|---|---:|---:|---|")
    for cat in (
        "canonical_like", "plausible_alternative", "obvious_noise",
        "noise_level_1", "noise_level_2", "noise_level_3",
    ):
        d = analysis[cat]
        if d["n"] == 0:
            continue
        lines.append(
            f"| {cat} | {d['n']} | {d['canon_valid_rate']:.0%} | "
            f"{d['novelty_band_counts']} |"
        )

    # Section 3: current DiscoveryClass distribution
    lines.append("\n## 3. Current DiscoveryClass classification (before calibration)\n")
    for cat in ("canonical_like", "plausible_alternative", "obvious_noise"):
        d = analysis[cat]
        lines.append(f"\n**{cat}** (n={d['n']}): {d['discovery_class_counts']}")

    # Section 4: category separation
    lines.append("\n## 4. Category separation analysis\n")

    # drift separation
    def _pct_overlap(a_vals: list[float], b_vals: list[float]) -> str:
        a_min, a_max = min(a_vals), max(a_vals)
        b_min, b_max = min(b_vals), max(b_vals)
        overlap_lo = max(a_min, b_min)
        overlap_hi = min(a_max, b_max)
        if overlap_hi < overlap_lo:
            return "NO OVERLAP"
        total_span = max(a_max, b_max) - min(a_min, b_min)
        if total_span == 0:
            return "identical"
        ov = (overlap_hi - overlap_lo) / total_span
        return f"{ov:.0%} overlap of combined range"

    lines.append("\n### drift (canon_soft_drift)")
    can_drift = analysis["canonical_like"]["canon_soft_drift"]["values"]
    alt_drift = analysis["plausible_alternative"]["canon_soft_drift"]["values"]
    noi_drift = analysis["obvious_noise"]["canon_soft_drift"]["values"]
    lines.append(f"- canonical vs alternative: {_pct_overlap(can_drift, alt_drift)}")
    lines.append(f"- alternative vs noise:     {_pct_overlap(alt_drift, noi_drift)}")
    lines.append(f"- canonical vs noise:       {_pct_overlap(can_drift, noi_drift)}")

    lines.append("\n### character_composite")
    can_cc = analysis["canonical_like"]["character_composite"]["values"]
    alt_cc = analysis["plausible_alternative"]["character_composite"]["values"]
    noi_cc = analysis["obvious_noise"]["character_composite"]["values"]
    lines.append(f"- canonical vs alternative: {_pct_overlap(can_cc, alt_cc)}")
    lines.append(f"- alternative vs noise:     {_pct_overlap(alt_cc, noi_cc)}")
    lines.append(f"- canonical vs noise:       {_pct_overlap(can_cc, noi_cc)}")

    # Section 5: threshold suitability
    lines.append("\n## 5. Current threshold diagnosis\n")
    rep_t = thresholds.get("reproduction_threshold", 3.0)
    noi_t = thresholds.get("noise_threshold", 20.0)

    under_rep = sum(1 for v in can_drift if v < rep_t)
    lines.append(
        f"- canonical_like under reproduction_threshold={rep_t}: "
        f"{under_rep}/{len(can_drift)} ({under_rep/len(can_drift):.0%})"
    )
    over_noise = sum(1 for v in noi_drift if v > noi_t)
    lines.append(
        f"- obvious_noise over noise_threshold={noi_t}: "
        f"{over_noise}/{len(noi_drift)} ({over_noise/len(noi_drift):.0%})"
    )
    mid_alt = sum(1 for v in alt_drift if rep_t <= v <= noi_t)
    lines.append(
        f"- plausible_alternative in [rep_t, noise_t]: "
        f"{mid_alt}/{len(alt_drift)} ({mid_alt/len(alt_drift):.0%})"
    )

    lines.append("\n## 6. Calibration targets (G4 input)\n")
    lines.append("Per Phase G spec §4.2:")
    lines.append("- `reproduction_threshold = canonical.drift P90`")
    lines.append("- `noise_threshold        = obvious_noise.drift P10`")
    lines.append(
        "- `character_min_composite = plausible_alternative.character P25`"
    )
    lines.append(
        "- `copy_threshold          = canonical.novelty_drift P10`"
    )
    lines.append("")

    target_rep = percentile(can_drift, 90)
    target_noi = percentile(noi_drift, 10)
    target_char = percentile(alt_cc, 25)
    lines.append(f"**Computed targets (preview):**")
    lines.append(f"- reproduction_threshold ← canonical.drift P90 = **{target_rep:.2f}**")
    lines.append(f"- noise_threshold        ← obvious_noise.drift P10 = **{target_noi:.2f}**")
    lines.append(f"- character_min_composite ← alt.character P25 = **{target_char:.3f}**")

    out_path.write_text("\n".join(lines), encoding="utf-8")


# =============================================================================
# Main
# =============================================================================

def main() -> int:
    eval_path = ROOT / "data" / "reference" / "evaluation_results.json"
    if not eval_path.exists():
        print(f"[G3] {eval_path} missing -- run G2 first")
        return 1

    payload = json.loads(eval_path.read_text(encoding="utf-8"))
    results = payload["results"]
    thresholds = payload["summary"]["evaluator_thresholds"]

    analysis = analyze(results)

    # Save JSON
    out_json = ROOT / "data" / "reference" / "distribution_analysis.json"
    # Strip raw values from JSON to reduce size
    lean = {cat: {
        "n": d["n"],
        "canon_valid_rate": d["canon_valid_rate"],
        "novelty_band_counts": d["novelty_band_counts"],
        "discovery_class_counts": d["discovery_class_counts"],
        **{k: {"stats": d[k]["stats"], "histogram": d[k]["histogram"]}
           for k in SCORE_KEYS},
    } for cat, d in analysis.items()}
    out_json.write_text(json.dumps({
        "schema_version": "witness.v3.distribution-analysis.0.1",
        "thresholds": thresholds,
        "analysis": lean,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown report
    md_path = ROOT / "docs" / "person" / "V3_REFERENCE_DISTRIBUTION_REPORT.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    write_report(analysis, thresholds, md_path)

    print(f"[G3] Saved:\n  {out_json}\n  {md_path}")
    # Print summary
    print("\nDrift medians:")
    for cat in ("canonical_like", "plausible_alternative", "obvious_noise"):
        s = analysis[cat]["canon_soft_drift"]["stats"]
        print(f"  {cat:<24} med={s['median']:.2f}  q1-q3={s['q1']:.2f}-{s['q3']:.2f}  range={s['min']:.2f}-{s['max']:.2f}")
    print("\nCharacter composite medians:")
    for cat in ("canonical_like", "plausible_alternative", "obvious_noise"):
        s = analysis[cat]["character_composite"]["stats"]
        print(f"  {cat:<24} med={s['median']:.3f}  q1-q3={s['q1']:.3f}-{s['q3']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
