"""Build Narrative IR from story features.

Per `docs/story/STORY_OUTPUT_SPEC.md` §4. Reads
`data/story/story_features/{probe_id}.json` and produces semantic narrative
fields (world_opening, initial_tension, pressure_arc, group_response,
turning_point, outcome, world_aftereffect, dominant_mode).

This is rule-based mapping. Each field is a SHORT phrase tagged with semantic
intent — actual Korean rendering happens in `render_story_ko.py`.

Usage:
    python scripts/story/build_narrative_ir.py P6
    python scripts/story/build_narrative_ir.py --all
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FEATURES_DIR = ROOT / "data" / "story" / "story_features"
OUT_DIR = ROOT / "data" / "story" / "narrative_ir"


# Semantic atoms for each field — picked by feature properties.
# Each atom is a (key, params) pair; renderer uses these to build Korean text.

def _scenario_location_names(pressure: str, n_locations: int) -> list[str]:
    """D-1: map L1/L2/L3 → scenario-specific semantic names."""
    if pressure == "scarcity":
        names = ["곡물 창고", "빈민가", "시장"]
    elif pressure == "accusation":
        names = ["윗방", "관청 안마당", "거리"]
    elif pressure == "sacred":
        names = ["성전 바깥뜰", "성전 안", "거리"]
    else:
        names = ["한 자리", "다른 자리", "또 다른 자리"]
    return names[:max(1, n_locations)]


def build_world_opening(f: dict) -> dict:
    """Initial atmosphere before any event."""
    pressure = f["primary_pressure"]
    locations_n = len(f["locations_present"])
    roles = f["roles_present"]
    return {
        "key": "opening",
        "pressure_type": pressure,
        "n_locations": locations_n,
        "has_authority": "authority" in roles or "authority_priest" in roles,
        "has_outsider": "outsider" in roles,
        "location_names": _scenario_location_names(pressure, locations_n),
    }


def build_initial_tension(f: dict) -> dict:
    """The first event."""
    if f["primary_pressure"] == "scarcity":
        target = f["accusation_targets"][0] if f["accusation_targets"] else None
        return {
            "key": "tension_scarcity_accusation",
            "target_role": target or "merchant",
            "n_accusations": f["accusations_count"],
        }
    if f["primary_pressure"] == "accusation":
        target = f["accusation_targets"][0] if f["accusation_targets"] else None
        return {
            "key": "tension_direct_accusation",
            "target_role": target,
            "n_accusations": f["accusations_count"],
        }
    if f["primary_pressure"] == "sacred":
        return {
            "key": "tension_sacred_event",
        }
    if f["primary_pressure"] == "none_clear" or f["final_summary"] == "LOW_ACTIVITY":
        return {
            "key": "tension_none",
        }
    return {"key": "tension_generic"}


def build_pressure_arc(f: dict) -> dict:
    """How pressure rose."""
    blame_peak = f.get("crowd_blame_peak", 0)
    blame_final = f.get("crowd_blame_final", 0) or 0
    susp_peak = f.get("public_suspicion_peak") or 0
    auth_peak = f.get("authority_vigilance_peak") or 0
    auth_final = f.get("authority_vigilance_final") or 0
    confessions = f["confessions_count"]
    pressure = f.get("primary_pressure", "")

    # B-1: blame_band 3단계 (FAILURE_MODES.md HIGH priority)
    if blame_peak < 0.5:
        blame_band = "absent"
    elif blame_peak < 1.5:
        blame_band = "weak"
    elif blame_peak < 3.0:
        blame_band = "strong"
    else:
        blame_band = "dominant"

    # B-2: confession volume scenario-normalized (FAILURE_MODES.md LOW)
    if pressure == "sacred":
        # sacred는 confessions 자체가 적음 → threshold 낮춤
        if confessions >= 60:
            confession_volume = "high"
        elif confessions >= 20:
            confession_volume = "moderate"
        else:
            confession_volume = "low"
    else:
        if confessions >= 100:
            confession_volume = "high"
        elif confessions >= 30:
            confession_volume = "moderate"
        else:
            confession_volume = "low"

    # D-2: authority decay 패턴 (peak vs final)
    if auth_peak >= 0.2:
        if auth_final < auth_peak * 0.5:
            authority_pattern = "decayed"   # 풀림
        elif auth_final >= auth_peak * 0.85:
            authority_pattern = "sustained" # 지속
        else:
            authority_pattern = "loosened"
    else:
        authority_pattern = "absent"

    return {
        "key": "arc",
        "blame_band": blame_band,
        "blame_strong": blame_peak >= 1.0,  # backward compat for renderer
        "blame_persists": blame_final >= 1.0,
        "suspicion_strong": susp_peak >= 0.3,
        "suspicion_persists": (f.get("public_suspicion_final") or 0) >= 0.3,
        "authority_strong": auth_peak >= 0.2,
        "authority_pattern": authority_pattern,
        "authority_persists": auth_final >= 0.2,
        "top_blame_target": f.get("top_blame_target_role"),
        "top_blame_strong": (f.get("top_blame_target_peak") or 0) >= 0.3,
        "confession_volume": confession_volume,
        "pressure_type": pressure,  # for renderer scenario branching
    }


def build_group_response(f: dict) -> dict:
    """How cohorts responded."""
    pressure = f.get("primary_pressure", "")
    cohorts_raw = f["cohort_outcomes"]
    arc_counts = {"recovery": 0, "saturation": 0, "partial": 0, "no_shame": 0}
    for c in cohorts_raw:
        arc_counts[c["arc"]] = arc_counts.get(c["arc"], 0) + 1
    n_total = sum(arc_counts.values())

    # D-1: enrich each cohort with semantic location name based on L# index
    location_names = _scenario_location_names(pressure, len(f.get("locations_present") or []))
    cohorts_detail = []
    for c in cohorts_raw:
        loc_id = c.get("location", "")
        idx = -1
        if loc_id and loc_id.startswith("L"):
            try:
                idx = int(loc_id[1:]) - 1
            except ValueError:
                idx = -1
        loc_name = location_names[idx] if 0 <= idx < len(location_names) else "한 자리"
        cohorts_detail.append({**c, "location_name": loc_name})

    return {
        "key": "response",
        "n_cohorts": n_total,
        "n_recovery": arc_counts.get("recovery", 0),
        "n_saturation": arc_counts.get("saturation", 0),
        "n_partial": arc_counts.get("partial", 0),
        "n_no_shame": arc_counts.get("no_shame", 0),
        "split": (arc_counts.get("recovery", 0) > 0 and arc_counts.get("saturation", 0) > 0),
        "cohorts_detail": cohorts_detail,
        # B-3: shame_residue_ratio (saturated cohorts proportion)
        "shame_residue_ratio": (
            arc_counts.get("saturation", 0) / n_total if n_total > 0 else 0.0
        ),
    }


def build_turning_point(f: dict) -> dict:
    """The pivot point."""
    fs = f["final_summary"]
    if fs == "RECOVERY_DOMINATED":
        return {
            "key": "turning_recovery",
            "confessions": f["confessions_count"],
            "forgiveness": f["forgiveness_count"],
        }
    if fs == "SATURATION_DOMINATED":
        return {
            "key": "turning_saturation",
            "failure_mode": f.get("failure_mode"),
        }
    if fs == "MIXED":
        return {
            "key": "turning_split",
        }
    if fs == "PARTIAL":
        return {
            "key": "turning_partial",
        }
    if fs == "LOW_ACTIVITY":
        return {
            "key": "turning_none",
        }
    return {"key": "turning_unclear"}


def build_outcome(f: dict) -> dict:
    return {
        "key": "outcome",
        "final_summary": f["final_summary"],
        "failure_mode": f.get("failure_mode"),
    }


def build_world_aftereffect(f: dict) -> dict:
    """Lingering world state."""
    susp_final = f.get("public_suspicion_final") or 0
    auth_final = f.get("authority_vigilance_final") or 0
    blame_final = f.get("crowd_blame_final") or 0
    return {
        "key": "aftereffect",
        "suspicion_residue": susp_final >= 0.2,
        "suspicion_strong_residue": susp_final >= 0.4,
        "authority_residue": auth_final >= 0.2,
        "blame_residue": blame_final >= 1.0,
        "blame_strong_residue": blame_final >= 3.0,
        "shame_residue_count": sum(
            1 for c in f["cohort_outcomes"]
            if c["arc"] == "saturation" and (c.get("final") or 0) >= 7
        ),
    }


def build_ir(features: dict) -> dict:
    fs = features["final_summary"]
    dominant_mode_map = {
        "RECOVERY_DOMINATED": "recovery_dominated",
        "SATURATION_DOMINATED": "saturation_dominated",
        "MIXED": "mixed",
        "PARTIAL": "partial",
        "LOW_ACTIVITY": "low_activity",
    }
    return {
        "probe_id": features["probe_id"],
        "title_hint": "",
        "world_opening": build_world_opening(features),
        "initial_tension": build_initial_tension(features),
        "pressure_arc": build_pressure_arc(features),
        "group_response": build_group_response(features),
        "turning_point": build_turning_point(features),
        "outcome": build_outcome(features),
        "world_aftereffect": build_world_aftereffect(features),
        "dominant_mode": dominant_mode_map.get(fs, "unclear"),
        "notes": [],
    }


def process(probe_id: str) -> dict:
    f_path = FEATURES_DIR / f"{probe_id}.json"
    if not f_path.exists():
        raise FileNotFoundError(f"Features not found: {f_path}")
    features = json.loads(f_path.read_text(encoding="utf-8"))
    ir = build_ir(features)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{probe_id}.json"
    out_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False), encoding="utf-8")
    return ir


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python scripts/story/build_narrative_ir.py <P_id|--all>")
        return 2

    if sys.argv[1] == "--all":
        for n in range(1, 13):
            probe_id = f"P{n}"
            try:
                ir = process(probe_id)
                gr = ir["group_response"]
                print(f"  {probe_id}: {ir['dominant_mode']:<22} cohorts(rec/sat/par)={gr['n_recovery']}/{gr['n_saturation']}/{gr['n_partial']}")
            except FileNotFoundError:
                print(f"  {probe_id}: skipped (no features)")
    elif sys.argv[1] == "--branch-c":
        for prefix in ["P_PV", "P_CV", "P_ED", "P_S2"]:
            for n in range(1, 10):
                probe_id = f"{prefix}_{n:02d}"
                try:
                    ir = process(probe_id)
                    gr = ir["group_response"]
                    print(f"  {probe_id}: {ir['dominant_mode']:<22} cohorts(rec/sat/par)={gr['n_recovery']}/{gr['n_saturation']}/{gr['n_partial']}")
                except FileNotFoundError:
                    print(f"  {probe_id}: skipped (no features)")
    else:
        ir = process(sys.argv[1])
        print(json.dumps(ir, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
