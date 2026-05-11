"""Validate annotated v4 fields across baseline + S5 + S4 probes (LOOP 64).

v4 adds: Top blame target field (Q3b interpersonal axis surface).

Per BRANCH_C_PREP_SPEC.md §2.3 + LOOP 64 v4 extension:
- All 12 baseline P{1-12}_ANNOTATED.txt must contain v4 fields including top_blame_target
- All 9 S5 P_PV_*.txt + 9 S4 P_CV_*.txt also must contain v4 fields
- Primary pressure detection must match ground truth (12/12 = 100%)
- Final summary must use one of 5 valid labels

Usage:
    PYTHONHASHSEED=0 python scripts/b_direction/validate_annotated_v4.py

Exit code 0 = all checks pass, 1 = any failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROBES = ROOT / "docs" / "b_direction" / "readability_probes"

REQUIRED_PATTERNS = {
    "header_v4_baseline": r"=== PROBE P\d+_ANNOTATED \(annotated supplement, v4\) ===",
    "final_summary": r"Final summary:\s+(LOW_ACTIVITY|RECOVERY_DOMINATED|SATURATION_DOMINATED|MIXED|PARTIAL)",
    "primary_pressure": r"Primary pressure:\s+(\w+)",
    "crowd_blame": r"Crowd blame total:\s+",
    "public_suspicion": r"Public suspicion:\s+",
    "authority_vigilance": r"Authority vigilance:\s+",
    "top_blame_target": r"Top blame target:\s+",
}

# Ground truth scenario per probe (READABILITY_BLIND_GROUND_TRUTH.md)
GT_SCENARIO = {
    "P1": "scarcity", "P2": "scarcity", "P3": "accusation",
    "P4": "sacred", "P5": "sacred", "P6": "scarcity",
    "P7": "sacred", "P8": "accusation", "P9": "scarcity",
    "P10": "accusation", "P11": "accusation", "P12": "sacred",
}


def validate_probe(probe_id: str) -> list[str]:
    """Return list of failures for given probe (empty if all pass)."""
    failures: list[str] = []
    path = PROBES / f"{probe_id}_ANNOTATED.txt"
    if not path.exists():
        return [f"{probe_id}: file not found at {path}"]
    text = path.read_text(encoding="utf-8")

    for name, pattern in REQUIRED_PATTERNS.items():
        if not re.search(pattern, text):
            failures.append(f"{probe_id}: missing pattern '{name}'")

    m = re.search(REQUIRED_PATTERNS["primary_pressure"], text)
    if m:
        detected = m.group(1)
        expected = GT_SCENARIO[probe_id]
        if detected != expected:
            failures.append(
                f"{probe_id}: primary_pressure={detected} vs GT={expected}"
            )

    return failures


def validate_branch_c_probes() -> list[str]:
    """Validate S5 placement + S4 cast + S3 event density probes pass v4."""
    failures: list[str] = []
    placement_dir = ROOT / "docs" / "b_direction" / "readability_probes_placement"
    cast_dir = ROOT / "docs" / "b_direction" / "readability_probes_cast"
    density_dir = ROOT / "docs" / "b_direction" / "readability_probes_event_density"
    scarcity_depth_dir = ROOT / "docs" / "b_direction" / "readability_probes_scarcity_depth"

    s5_header_re = r"=== PROBE P_PV_\d+ \(placement variant: \w+/\w+, v4\) ==="
    s4_header_re = r"=== PROBE P_CV_\d+ \(cast variant: \w+/\w+, n=\d+, v4\) ==="
    s3_header_re = r"=== PROBE P_ED_\d+ \(event density: \w+/\w+-density/\w+-spacing, v4\) ==="
    s2_header_re = r"=== PROBE P_S2_\d+ \(scarcity depth: \w+-events/\w+-density, v4\) ==="

    for path in sorted(placement_dir.glob("P_PV_*.txt")) if placement_dir.exists() else []:
        text = path.read_text(encoding="utf-8")
        if not re.search(s5_header_re, text):
            failures.append(f"S5 {path.name}: missing v4 header")
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "header_v4_baseline":
                continue
            if not re.search(pattern, text):
                failures.append(f"S5 {path.name}: missing pattern '{name}'")

    for path in sorted(cast_dir.glob("P_CV_*.txt")) if cast_dir.exists() else []:
        text = path.read_text(encoding="utf-8")
        if not re.search(s4_header_re, text):
            failures.append(f"S4 {path.name}: missing v4 header")
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "header_v4_baseline":
                continue
            if not re.search(pattern, text):
                failures.append(f"S4 {path.name}: missing pattern '{name}'")

    for path in sorted(density_dir.glob("P_ED_*.txt")) if density_dir.exists() else []:
        text = path.read_text(encoding="utf-8")
        if not re.search(s3_header_re, text):
            failures.append(f"S3 {path.name}: missing v4 header")
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "header_v4_baseline":
                continue
            if not re.search(pattern, text):
                failures.append(f"S3 {path.name}: missing pattern '{name}'")

    for path in sorted(scarcity_depth_dir.glob("P_S2_*.txt")) if scarcity_depth_dir.exists() else []:
        text = path.read_text(encoding="utf-8")
        if not re.search(s2_header_re, text):
            failures.append(f"S2 {path.name}: missing v4 header")
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "header_v4_baseline":
                continue
            if not re.search(pattern, text):
                failures.append(f"S2 {path.name}: missing pattern '{name}'")

    return failures


def main() -> int:
    all_failures: list[str] = []
    for i in range(1, 13):
        all_failures.extend(validate_probe(f"P{i}"))

    if all_failures:
        print("FAIL - Annotated v4 baseline validation:")
        for f in all_failures:
            print(f"  {f}")
        return 1

    print("PASS - 12/12 baseline probes contain v4 fields (incl. top_blame_target)")
    print("PASS - 12/12 primary pressure matches ground truth scenario")

    branch_c_failures = validate_branch_c_probes()
    if branch_c_failures:
        print("\nFAIL - Branch C v4 validation:")
        for f in branch_c_failures:
            print(f"  {f}")
        return 1

    placement_count = len(list((ROOT / "docs/b_direction/readability_probes_placement").glob("P_PV_*.txt")))
    cast_count = len(list((ROOT / "docs/b_direction/readability_probes_cast").glob("P_CV_*.txt")))
    density_count = len(list((ROOT / "docs/b_direction/readability_probes_event_density").glob("P_ED_*.txt")))
    s2_count = len(list((ROOT / "docs/b_direction/readability_probes_scarcity_depth").glob("P_S2_*.txt")))
    print(f"PASS - Branch C S5 ({placement_count}) + S4 ({cast_count}) + S3 ({density_count}) + S2 ({s2_count}) probes contain v4 fields")
    print(f"PASS - Total {12 + placement_count + cast_count + density_count + s2_count} probes validated against v4 spec")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
