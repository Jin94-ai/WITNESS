"""Phase G Step G4 — Threshold calibration (percentile-based only).

Rule #20 엄수: 분포 기반만. "느낌으로 조정" 금지.

Formulas (spec §4.2):
    reproduction_threshold = canonical_like.drift P90
    noise_threshold        = obvious_noise.drift P10
    character_min          = plausible_alternative.character_composite P25
    copy_threshold         = canonical_like.novelty_drift P10

Outputs:
    data/reference/calibrated_thresholds.json
    Confusion matrix printed + saved
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3_measurement.analyze_reference_distribution import percentile  # noqa: E402
from scripts.v3_measurement.run_reference_evaluation import (  # noqa: E402
    build_evaluator,
    evaluate_all,
)


def compute_calibrated_thresholds(results: list[dict]) -> dict:
    by_cat: dict[str, list[dict]] = {
        "canonical_like": [],
        "plausible_alternative": [],
        "obvious_noise": [],
    }
    for r in results:
        by_cat[r["category"]].append(r)

    can_drift = [r["scores"]["canon_soft_drift"] for r in by_cat["canonical_like"]]
    noi_drift = [r["scores"]["canon_soft_drift"] for r in by_cat["obvious_noise"]]
    alt_char = [r["scores"]["character_composite"]
                for r in by_cat["plausible_alternative"]]
    can_nov = [r["scores"]["novelty_drift"] for r in by_cat["canonical_like"]]

    reproduction_threshold = percentile(can_drift, 90)
    noise_threshold = percentile(noi_drift, 10)
    character_min = percentile(alt_char, 25)
    copy_threshold = percentile(can_nov, 10)

    return {
        "reproduction_threshold": reproduction_threshold,
        "noise_threshold": noise_threshold,
        "character_min_composite": character_min,
        "copy_threshold": copy_threshold,
        "formulas": {
            "reproduction_threshold": "canonical_like.drift P90",
            "noise_threshold": "obvious_noise.drift P10",
            "character_min_composite": "plausible_alternative.character_composite P25",
            "copy_threshold": "canonical_like.novelty_drift P10",
        },
        "source_distributions": {
            "canonical_drift": {"p10": percentile(can_drift, 10),
                                "p50": percentile(can_drift, 50),
                                "p90": percentile(can_drift, 90),
                                "n": len(can_drift)},
            "noise_drift": {"p10": percentile(noi_drift, 10),
                            "p50": percentile(noi_drift, 50),
                            "p90": percentile(noi_drift, 90),
                            "n": len(noi_drift)},
            "alternative_character": {
                "p25": percentile(alt_char, 25),
                "p50": percentile(alt_char, 50),
                "p75": percentile(alt_char, 75),
                "n": len(alt_char),
            },
        },
    }


def build_calibrated_evaluator(thresholds: dict):
    return build_evaluator(
        reproduction_threshold=thresholds["reproduction_threshold"],
        noise_threshold=thresholds["noise_threshold"],
        copy_threshold=thresholds["copy_threshold"],
        character_min=thresholds["character_min_composite"],
    )


def confusion_matrix(results: list[dict]) -> dict:
    """Build actual vs predicted matrix after re-evaluation."""
    # Map discovery_class to the three actual categories
    def predicted_category(cls: str) -> str:
        if cls == "canonical_reproduction":
            return "canonical"
        if cls in ("canon_compatible_alternative", "character_consistent_novel"):
            return "alternative"
        if cls == "not_discovery_noise":
            return "noise"
        return "other"

    matrix = {
        "canonical_like":         {"canonical": 0, "alternative": 0, "noise": 0, "other": 0, "n": 0},
        "plausible_alternative":  {"canonical": 0, "alternative": 0, "noise": 0, "other": 0, "n": 0},
        "obvious_noise":          {"canonical": 0, "alternative": 0, "noise": 0, "other": 0, "n": 0},
    }
    for r in results:
        actual = r["category"]
        predicted = predicted_category(r["discovery_class"])
        matrix[actual][predicted] += 1
        matrix[actual]["n"] += 1

    # compute rates
    rates = {}
    for actual, row in matrix.items():
        n = row["n"] or 1
        rates[actual] = {
            k: (v / n if k != "n" else n)
            for k, v in row.items()
        }
    return {"counts": matrix, "rates": rates}


def meets_target(rates: dict) -> tuple[bool, list[str]]:
    """Per Phase G §4.3 target:
       canon>80% / <15% alt / <5% noise
       alt <10% / >70% alt / <20% noise
       noise <5% / <10% alt / >85% noise
    """
    issues: list[str] = []
    r = rates
    if r["canonical_like"]["canonical"] < 0.80:
        issues.append(
            f"canonical→canonical {r['canonical_like']['canonical']:.0%} < 80%"
        )
    if r["canonical_like"]["alternative"] > 0.15:
        issues.append(
            f"canonical→alternative {r['canonical_like']['alternative']:.0%} > 15%"
        )
    if r["canonical_like"]["noise"] > 0.05:
        issues.append(
            f"canonical→noise {r['canonical_like']['noise']:.0%} > 5%"
        )
    if r["plausible_alternative"]["alternative"] < 0.70:
        issues.append(
            f"alt→alternative {r['plausible_alternative']['alternative']:.0%} < 70%"
        )
    if r["plausible_alternative"]["canonical"] > 0.10:
        issues.append(
            f"alt→canonical {r['plausible_alternative']['canonical']:.0%} > 10%"
        )
    if r["plausible_alternative"]["noise"] > 0.20:
        issues.append(
            f"alt→noise {r['plausible_alternative']['noise']:.0%} > 20%"
        )
    if r["obvious_noise"]["noise"] < 0.85:
        issues.append(
            f"noise→noise {r['obvious_noise']['noise']:.0%} < 85%"
        )
    if r["obvious_noise"]["canonical"] > 0.05:
        issues.append(
            f"noise→canonical {r['obvious_noise']['canonical']:.0%} > 5%"
        )
    if r["obvious_noise"]["alternative"] > 0.10:
        issues.append(
            f"noise→alternative {r['obvious_noise']['alternative']:.0%} > 10%"
        )
    return (not issues), issues


def main() -> int:
    # Load G2 output
    eval_path = ROOT / "data" / "reference" / "evaluation_results.json"
    if not eval_path.exists():
        print(f"[G4] {eval_path} missing -- run G2 first")
        return 1
    eval_payload = json.loads(eval_path.read_text(encoding="utf-8"))
    pre_results = eval_payload["results"]

    # Step 1: compute percentile-based thresholds
    thresholds = compute_calibrated_thresholds(pre_results)
    print("[G4] Calibrated thresholds (percentile-based):")
    for k in ("reproduction_threshold", "noise_threshold",
              "character_min_composite", "copy_threshold"):
        print(f"  {k:<30} = {thresholds[k]:.3f}")

    # Step 2: re-evaluate with new thresholds
    calibrated = build_calibrated_evaluator(thresholds)
    post_payload = evaluate_all(
        evaluator=calibrated,
        out_path=ROOT / "data" / "reference" / "evaluation_results_calibrated.json",
    )
    post_results = post_payload["results"]

    # Step 3: confusion matrix
    cm = confusion_matrix(post_results)
    print("\n[G4] Confusion matrix (actual → predicted):")
    print(f"{'actual':<24} | {'canonical':>10} | {'alternative':>12} | {'noise':>7}")
    print("-" * 65)
    for actual in ("canonical_like", "plausible_alternative", "obvious_noise"):
        r = cm["rates"][actual]
        print(
            f"{actual:<24} | {r['canonical']:>10.0%} | "
            f"{r['alternative']:>12.0%} | {r['noise']:>7.0%}"
        )

    # Step 4: target check
    ok, issues = meets_target(cm["rates"])
    print(f"\n[G4] Target met: {ok}")
    if issues:
        print("Issues:")
        for i in issues:
            print(f"  - {i}")

    # Save
    out = {
        "schema_version": "witness.v3.calibrated-thresholds.0.1",
        "calibrated_thresholds": thresholds,
        "confusion_matrix": cm,
        "meets_target": ok,
        "issues": issues,
    }
    out_path = ROOT / "data" / "reference" / "calibrated_thresholds.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\n  saved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
