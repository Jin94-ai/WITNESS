"""Stage 4 Cleaning — Step 1 Taxonomy Repair.

Per docs/WITNESS_GEMMA_WEAK_LABEL_DATASET_CLEANING_PLAN.md §3.

Input:  data/external_private/gemma_review/work_e46069c4b4_stage3_private.jsonl (225 records)
Output: data/external_private/gemma_review/work_e46069c4b4_stage3_repaired_private.jsonl
        docs/results/gemma_labeling_poc/stage3_repair_report.md
        docs/results/gemma_labeling_poc/stage3_repair_summary.json

Repair rules (§3.2):
  R1. "unknown" in primary_desires/secondary_desires → remove. primary 비면 needs_review.
  R2. invalid conflict_axis → "unknown". original 보존. needs_review.
  R3. "love" in primary_desires/secondary_desires → remove from desires, add to
      secondary_pressures. 중복 제거.

NOT 자동 학습. raw passage public 노출 0.

Run:
    python -m scripts.labeling.stage4_repair
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "external_private" / "gemma_review" / "work_e46069c4b4_stage3_private.jsonl"
PRIVATE_OUT = ROOT / "data" / "external_private" / "gemma_review" / "work_e46069c4b4_stage3_repaired_private.jsonl"
PUBLIC_REPORT = ROOT / "docs" / "results" / "gemma_labeling_poc" / "stage3_repair_report.md"
PUBLIC_SUMMARY = ROOT / "docs" / "results" / "gemma_labeling_poc" / "stage3_repair_summary.json"

ALLOWED_PRESSURES = {
    "fear", "shame_self", "hope", "grief", "confusion", "love",
    "authority_vigilance", "public_suspicion", "blame_concentration",
    "group_tension", "crowd_mood",
}
ALLOWED_DESIRES = {
    "loyalty", "survival", "control", "exposure_avoidance",
    "identity_preservation", "commitment", "trust", "group_safety",
}
ALLOWED_CONFLICT_AXES = {
    "loyalty_vs_survival", "uncertainty_vs_commitment",
    "control_vs_exposure", "collective_fear_vs_scapegoating",
    "identity_vs_failure", "atmosphere_vs_action",
    "trust_vs_self_protection", "unknown",
}


def _dedupe(lst: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in lst or []:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def validate_label(label: dict) -> dict:
    """Returns dict of issues (empty = valid)."""
    issues: dict = {}
    pp = label.get("primary_pressures", []) or []
    sp = label.get("secondary_pressures", []) or []
    pd = label.get("primary_desires", []) or []
    sd = label.get("secondary_desires", []) or []

    # unknown leakage
    if "unknown" in pp:
        issues["unknown_in_primary_pressures"] = True
    if "unknown" in sp:
        issues["unknown_in_secondary_pressures"] = True
    if "unknown" in pd:
        issues["unknown_in_primary_desires"] = True
    if "unknown" in sd:
        issues["unknown_in_secondary_desires"] = True

    # love leakage
    if "love" in pd:
        issues["love_in_primary_desires"] = True
    if "love" in sd:
        issues["love_in_secondary_desires"] = True

    # taxonomy validity
    inv_p = [v for v in (pp + sp) if v not in ALLOWED_PRESSURES]
    if inv_p:
        issues["invalid_pressures"] = inv_p
    inv_d = [v for v in (pd + sd) if v not in ALLOWED_DESIRES]
    if inv_d:
        issues["invalid_desires"] = inv_d
    axis = label.get("conflict_axis", "")
    if axis and axis not in ALLOWED_CONFLICT_AXES:
        issues["invalid_conflict_axis"] = axis
    return issues


def apply_repair(label: dict) -> tuple[dict, list[str], bool, dict]:
    """Apply R1/R2/R3 to a single label.

    Returns (repaired_label_copy, applied_rules, needs_review, original_fields_for_log).
    """
    out = json.loads(json.dumps(label, ensure_ascii=False))  # deep copy
    rules: list[str] = []
    needs_review = False
    orig: dict = {}

    pp = list(out.get("primary_pressures") or [])
    sp = list(out.get("secondary_pressures") or [])
    pd = list(out.get("primary_desires") or [])
    sd = list(out.get("secondary_desires") or [])

    # R3 — love in desires (먼저 처리, 그래야 R1 unknown 검사가 통일된 desires에서 작동)
    if "love" in pd or "love" in sd:
        rules.append("R3_love_desires_to_secondary_pressures")
        if "love" in pd:
            pd = [x for x in pd if x != "love"]
        if "love" in sd:
            sd = [x for x in sd if x != "love"]
        # Add to secondary_pressures (dedupe)
        if "love" not in sp:
            sp.append("love")
        sp = _dedupe(sp)

    # R1 — unknown in desires
    if "unknown" in pd or "unknown" in sd:
        rules.append("R1_remove_unknown_from_desires")
        pd = [x for x in pd if x != "unknown"]
        sd = [x for x in sd if x != "unknown"]
        if not pd:
            needs_review = True

    # R2 — invalid conflict_axis → unknown
    axis = out.get("conflict_axis", "")
    if axis and axis not in ALLOWED_CONFLICT_AXES:
        rules.append("R2_invalid_axis_to_unknown")
        orig["original_conflict_axis"] = axis
        out["conflict_axis"] = "unknown"
        needs_review = True

    out["primary_pressures"] = pp
    out["secondary_pressures"] = sp
    out["primary_desires"] = pd
    out["secondary_desires"] = sd

    return out, rules, needs_review, orig


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(INPUT_PATH)

    PRIVATE_OUT.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_REPORT.parent.mkdir(parents=True, exist_ok=True)

    # Stats
    total = 0
    invalid_before_total = 0
    invalid_before_types = Counter()
    repair_rule_counter = Counter()
    needs_review_count = 0
    invalid_after_total = 0
    invalid_after_types = Counter()

    pressure_before = Counter()
    pressure_after = Counter()
    desire_before = Counter()
    desire_after = Counter()
    axis_before = Counter()
    axis_after = Counter()

    with INPUT_PATH.open(encoding="utf-8") as fin, PRIVATE_OUT.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total += 1
            label = rec.get("label", {})
            # Skip errored records (won't have proper label structure)
            if "_error" in label:
                rec["validation_before_repair"] = {"is_valid": False, "issues": {"label_error": True}}
                rec["repair"] = {"applied": False, "rules": [], "needs_review": True}
                rec["validation_after_repair"] = {"is_valid": False, "issues": {"label_error": True}}
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue

            # Before stats
            for p in label.get("primary_pressures", []) or []:
                pressure_before[f"primary:{p}"] += 1
            for d in label.get("primary_desires", []) or []:
                desire_before[f"primary:{d}"] += 1
            axis_before[label.get("conflict_axis", "")] += 1

            issues_before = validate_label(label)
            if issues_before:
                invalid_before_total += 1
                for k in issues_before:
                    invalid_before_types[k] += 1

            repaired, rules, nr, orig_fields = apply_repair(label)
            applied = bool(rules)
            for r in rules:
                repair_rule_counter[r] += 1
            if nr:
                needs_review_count += 1

            issues_after = validate_label(repaired)
            if issues_after:
                invalid_after_total += 1
                for k in issues_after:
                    invalid_after_types[k] += 1

            # After stats
            for p in repaired.get("primary_pressures", []) or []:
                pressure_after[f"primary:{p}"] += 1
            for d in repaired.get("primary_desires", []) or []:
                desire_after[f"primary:{d}"] += 1
            axis_after[repaired.get("conflict_axis", "")] += 1

            # Build record
            out_rec = dict(rec)
            out_rec["label"] = repaired
            out_rec["validation_before_repair"] = {
                "is_valid": not bool(issues_before),
                "issues": issues_before,
            }
            out_rec["repair"] = {
                "applied": applied,
                "rules": rules,
                "needs_review": nr,
                **orig_fields,
            }
            out_rec["validation_after_repair"] = {
                "is_valid": not bool(issues_after),
                "issues": issues_after,
            }
            # original raw label 보존
            out_rec["label_raw_before_repair"] = label
            fout.write(json.dumps(out_rec, ensure_ascii=False) + "\n")

    # Build summary JSON
    summary = {
        "stage": "stage4_repair",
        "schema_version": "stage3_repair_summary_v1",
        "input_path": str(INPUT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "output_path": str(PRIVATE_OUT.relative_to(ROOT)).replace("\\", "/"),
        "completed_at_iso": datetime.now(timezone.utc).isoformat(),
        "totals": {
            "total_records": total,
            "invalid_before_repair": invalid_before_total,
            "repair_applied": sum(repair_rule_counter.values()) > 0 and total or 0,  # placeholder
            "needs_review": needs_review_count,
            "invalid_after_repair": invalid_after_total,
        },
        "invalid_types_before": dict(invalid_before_types),
        "invalid_types_after": dict(invalid_after_types),
        "repair_rule_distribution": dict(repair_rule_counter),
        "primary_pressure_distribution_before": dict(pressure_before),
        "primary_pressure_distribution_after": dict(pressure_after),
        "primary_desire_distribution_before": dict(desire_before),
        "primary_desire_distribution_after": dict(desire_after),
        "conflict_axis_distribution_before": dict(axis_before),
        "conflict_axis_distribution_after": dict(axis_after),
    }
    # records with applied repair
    records_with_repair = sum(repair_rule_counter.values())  # may double-count if multiple rules on one record
    summary["totals"]["repair_applied_records_estimate"] = records_with_repair
    # accurate count via second pass on file
    applied_records = 0
    with PRIVATE_OUT.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("repair", {}).get("applied"):
                applied_records += 1
    summary["totals"]["repair_applied_records"] = applied_records
    del summary["totals"]["repair_applied"]
    del summary["totals"]["repair_applied_records_estimate"]

    PUBLIC_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[repair] {total} records, invalid before/after: {invalid_before_total} / {invalid_after_total}")
    print(f"[repair] repair applied to {applied_records} records, needs_review: {needs_review_count}")
    print(f"[repair] private out: {PRIVATE_OUT}")
    print(f"[repair] public summary: {PUBLIC_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
