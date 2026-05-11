"""Extract story features from annotated probe (.txt) -> JSON.

Per `docs/story/STORY_OUTPUT_SPEC.md` §3 (input schema). Reads
`docs/b_direction/readability_probes/P{n}_ANNOTATED.txt` and produces
`data/story/story_features/{probe_id}.json`.

Pure parser. No story rendering, no narrative IR yet.

Usage:
    python scripts/story/extract_story_features.py P6
    python scripts/story/extract_story_features.py --all   # P1..P12
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROBES_DIR = ROOT / "docs" / "b_direction" / "readability_probes"
OUT_DIR = ROOT / "data" / "story" / "story_features"

# Branch C 36 probes — 4 slices x 9 each
BRANCH_C_DIRS = {
    "P_PV": ROOT / "docs" / "b_direction" / "readability_probes_placement",   # S5
    "P_CV": ROOT / "docs" / "b_direction" / "readability_probes_cast",        # S4
    "P_ED": ROOT / "docs" / "b_direction" / "readability_probes_event_density",  # S3
    "P_S2": ROOT / "docs" / "b_direction" / "readability_probes_scarcity_depth",  # S2
}


def parse_probe(text: str) -> dict:
    """Parse annotated probe .txt -> features dict.

    Returns dict matching SPEC §3.
    """
    out: dict = {}

    # probe_id from header — supports baseline (P\d+_ANNOTATED) + Branch C (P_PV_NN, P_CV_NN, P_ED_NN, P_S2_NN)
    m = re.search(r"=== PROBE (P\d+)_ANNOTATED", text)
    if m:
        out["probe_id"] = m.group(1)
    else:
        m = re.search(r"=== PROBE (P_(?:PV|CV|ED|S2)_\d+)", text)
        out["probe_id"] = m.group(1) if m else "unknown"

    m = re.search(r"Final summary:\s+(\w+)", text)
    out["final_summary"] = m.group(1) if m else None

    m = re.search(r"Primary pressure:\s+(\w+)", text)
    out["primary_pressure"] = m.group(1) if m else None

    m = re.search(r"Failure mode:\s+(\w+)", text)
    out["failure_mode"] = m.group(1) if m else None

    # Cohort outcomes (multiple lines)
    cohorts = []
    cohort_block = re.search(
        r"Cohort outcomes:\n((?:\s+\[L\d+ cohort.*\n)+)", text,
    )
    if cohort_block:
        for line in cohort_block.group(1).strip().split("\n"):
            cm = re.search(
                r"\[(L\d+) cohort,\s*(\d+) agents\]:\s+(.+)", line.strip(),
            )
            if cm:
                arc_text = cm.group(3)
                arc_type = "no_shame"
                peak = None
                final = None
                if "no shame" in arc_text:
                    arc_type = "no_shame"
                elif "recovery" in arc_text:
                    arc_type = "recovery"
                elif "saturation" in arc_text:
                    arc_type = "saturation"
                elif "partial" in arc_text:
                    arc_type = "partial"
                pm = re.search(r"peak~?([\d.]+)", arc_text)
                if pm:
                    peak = float(pm.group(1))
                fm = re.search(r"final~?([\d.]+)", arc_text)
                if fm:
                    final = float(fm.group(1))
                cohorts.append({
                    "location": cm.group(1),
                    "agents_count": int(cm.group(2)),
                    "arc": arc_type,
                    "peak": peak,
                    "final": final,
                })
    out["cohort_outcomes"] = cohorts

    # Accusations: "Accusations: N fired (targets: X, Y)"
    m = re.search(r"Accusations:\s+(\d+)\s+fired", text)
    out["accusations_count"] = int(m.group(1)) if m else 0
    m = re.search(r"targets:\s+([^)]+)\)", text)
    out["accusation_targets"] = (
        [t.strip() for t in m.group(1).split(",")] if m else []
    )

    # Recovery actions: "N confessions, N forgiveness rumors emitted"
    m = re.search(r"Recovery actions:\s+(\d+)\s+confessions,\s+(\d+)\s+forgiveness", text)
    out["confessions_count"] = int(m.group(1)) if m else 0
    out["forgiveness_count"] = int(m.group(2)) if m else 0

    # Crowd blame total
    m = re.search(
        r"Crowd blame total:\s+peak\s+([\d.]+)(?:\s+at\s+t=(\d+))?\s*(?:→|->)\s+final\s+([\d.]+)",
        text,
    )
    if m:
        out["crowd_blame_peak"] = float(m.group(1))
        out["crowd_blame_peak_t"] = int(m.group(2)) if m.group(2) else None
        out["crowd_blame_final"] = float(m.group(3))
    else:
        out["crowd_blame_peak"] = 0.0
        out["crowd_blame_final"] = 0.0
        out["crowd_blame_peak_t"] = None

    # Public suspicion
    m = re.search(
        r"Public suspicion:\s+peak\s+([\d.]+)\s*(?:→|->)\s+final\s+([\d.]+)",
        text,
    )
    if m:
        out["public_suspicion_peak"] = float(m.group(1))
        out["public_suspicion_final"] = float(m.group(2))
    elif "Public suspicion:    negligible" in text:
        out["public_suspicion_peak"] = 0.0
        out["public_suspicion_final"] = 0.0
    else:
        out["public_suspicion_peak"] = None
        out["public_suspicion_final"] = None

    # Authority vigilance
    m = re.search(
        r"Authority vigilance:\s+peak\s+([\d.]+)\s*(?:→|->)\s+final\s+([\d.]+)",
        text,
    )
    if m:
        out["authority_vigilance_peak"] = float(m.group(1))
        out["authority_vigilance_final"] = float(m.group(2))
    elif "Authority vigilance: negligible" in text:
        out["authority_vigilance_peak"] = 0.0
        out["authority_vigilance_final"] = 0.0
    else:
        out["authority_vigilance_peak"] = None
        out["authority_vigilance_final"] = None

    # Top blame target (v4)
    m = re.search(
        r"Top blame target:\s+(\w+)\s+\(peak\s+([\d.]+)(?:,\s+weak)?\)", text,
    )
    if m:
        out["top_blame_target_role"] = m.group(1)
        out["top_blame_target_peak"] = float(m.group(2))
    else:
        out["top_blame_target_role"] = None
        out["top_blame_target_peak"] = 0.0

    # Roles (Agents line): "Agents: A1=merchant, A2=family, ..."
    m = re.search(r"Agents:\s+(.+)", text)
    roles_present = []
    if m:
        for entry in m.group(1).split(","):
            entry = entry.strip()
            if "=" in entry:
                roles_present.append(entry.split("=", 1)[1].strip())
    out["roles_present"] = sorted(set(roles_present))

    # Locations
    m = re.search(r"Locations:\s+(.+)", text)
    if m:
        out["locations_present"] = [s.strip() for s in m.group(1).split(",")]
    else:
        out["locations_present"] = []

    # Key events first 30 lines from event log
    out["key_events_sample"] = []
    eventlog = re.search(
        r"--- Event log[^\n]*\n((?:.+\n)+?)(?=\n=|\Z)", text,
    )
    if eventlog:
        for line in eventlog.group(1).split("\n")[:30]:
            line = line.strip()
            if line and not line.startswith("---") and not line.startswith("("):
                out["key_events_sample"].append(line)

    return out


def _resolve_probe_path(probe_id: str) -> Path:
    """Find probe file. Baseline: docs/b_direction/readability_probes/P{n}_ANNOTATED.txt
    Branch C: by prefix, in matching readability_probes_* directory."""
    if probe_id.startswith("P_"):
        prefix = "_".join(probe_id.split("_")[:2])  # P_PV / P_CV / P_ED / P_S2
        directory = BRANCH_C_DIRS.get(prefix)
        if directory is None:
            raise FileNotFoundError(f"Unknown Branch C prefix: {prefix}")
        return directory / f"{probe_id}.txt"
    return PROBES_DIR / f"{probe_id}_ANNOTATED.txt"


def process_probe(probe_id: str) -> dict:
    path = _resolve_probe_path(probe_id)
    if not path.exists():
        raise FileNotFoundError(f"Probe not found: {path}")
    text = path.read_text(encoding="utf-8")
    features = parse_probe(text)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{probe_id}.json"
    out_path.write_text(json.dumps(features, indent=2, ensure_ascii=False), encoding="utf-8")
    return features


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/story/extract_story_features.py <P_id|--all>")
        return 2

    if sys.argv[1] == "--all":
        for n in range(1, 13):
            probe_id = f"P{n}"
            try:
                f = process_probe(probe_id)
                print(f"  {probe_id}: {f['final_summary']:<22} / {f['primary_pressure']:<12} / cohorts={len(f['cohort_outcomes'])}")
            except FileNotFoundError as e:
                print(f"  {probe_id}: skipped ({e})")
    elif sys.argv[1] == "--branch-c":
        for prefix in ["P_PV", "P_CV", "P_ED", "P_S2"]:
            for n in range(1, 10):
                probe_id = f"{prefix}_{n:02d}"
                try:
                    f = process_probe(probe_id)
                    print(f"  {probe_id}: {f['final_summary']:<22} / {f['primary_pressure']:<12} / cohorts={len(f['cohort_outcomes'])}")
                except FileNotFoundError as e:
                    print(f"  {probe_id}: skipped ({e})")
    else:
        probe_id = sys.argv[1]
        f = process_probe(probe_id)
        print(json.dumps(f, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
