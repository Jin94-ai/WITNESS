"""Validate annotated v3 fields across all 12 probes (Branch C prep, LOOP 51).

Per BRANCH_C_PREP_SPEC.md §2.3:
- All 12 P{1-12}_ANNOTATED.txt must contain required v3 fields
- Primary pressure detection must match ground truth (12/12 = 100%)
- Final summary must use one of 5 valid labels

Usage:
    PYTHONHASHSEED=0 python scripts/b_direction/validate_annotated_v3.py

Exit code 0 = all checks pass, 1 = any failure.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROBES = ROOT / "docs" / "b_direction" / "readability_probes"

REQUIRED_PATTERNS = {
    "header_v3": r"=== PROBE P\d+_ANNOTATED \(annotated supplement, v3\) ===",
    "final_summary": r"Final summary:\s+(LOW_ACTIVITY|RECOVERY_DOMINATED|SATURATION_DOMINATED|MIXED|PARTIAL)",
    "primary_pressure": r"Primary pressure:\s+(\w+)",
    "crowd_blame": r"Crowd blame total:\s+",
    "public_suspicion": r"Public suspicion:\s+",
    "authority_vigilance": r"Authority vigilance:\s+",
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

    # Pattern presence
    for name, pattern in REQUIRED_PATTERNS.items():
        if not re.search(pattern, text):
            failures.append(f"{probe_id}: missing pattern '{name}'")

    # Primary pressure must match GT
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
    """Validate S5 placement + S4 cast probes also pass v3 acceptance."""
    failures: list[str] = []
    placement_dir = ROOT / "docs" / "b_direction" / "readability_probes_placement"
    cast_dir = ROOT / "docs" / "b_direction" / "readability_probes_cast"

    for path in sorted(placement_dir.glob("P_PV_*.txt")) if placement_dir.exists() else []:
        text = path.read_text(encoding="utf-8")
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "header_v3":
                continue  # different header format
            if not re.search(pattern, text):
                failures.append(f"S5 {path.name}: missing pattern '{name}'")

    for path in sorted(cast_dir.glob("P_CV_*.txt")) if cast_dir.exists() else []:
        text = path.read_text(encoding="utf-8")
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "header_v3":
                continue
            if not re.search(pattern, text):
                failures.append(f"S4 {path.name}: missing pattern '{name}'")

    return failures


def main() -> int:
    all_failures: list[str] = []
    for i in range(1, 13):
        all_failures.extend(validate_probe(f"P{i}"))

    if all_failures:
        print("FAIL - Annotated v3 validation:")
        for f in all_failures:
            print(f"  {f}")
        return 1

    print("PASS - 12/12 annotated probes contain v3 fields")
    print("PASS - 12/12 primary pressure matches ground truth scenario")
    print("PASS - Branch C acceptance criteria section 2 met")

    # Branch C extension: validate S5+S4 probes as well
    branch_c_failures = validate_branch_c_probes()
    if branch_c_failures:
        print("\nWARN - Branch C extension validation:")
        for f in branch_c_failures:
            print(f"  {f}")
    else:
        placement_count = len(list((ROOT / "docs/b_direction/readability_probes_placement").glob("P_PV_*.txt")))
        cast_count = len(list((ROOT / "docs/b_direction/readability_probes_cast").glob("P_CV_*.txt")))
        if placement_count or cast_count:
            print(f"PASS - Branch C S5 placement ({placement_count}) + S4 cast ({cast_count}) probes contain v3 fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
