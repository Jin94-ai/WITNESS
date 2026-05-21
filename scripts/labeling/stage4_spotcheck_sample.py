"""Stage 4 Cleaning — Step 2 Spot Check Sample Generation.

Per docs/WITNESS_GEMMA_WEAK_LABEL_DATASET_CLEANING_PLAN.md §4.

Input:  data/external_private/gemma_review/work_e46069c4b4_stage3_repaired_private.jsonl
Output: data/external_private/gemma_review/work_e46069c4b4_stage3_spotcheck_private.jsonl (50 samples)

Sample 구성:
  A. confidence ≤ 0.75 중에서 10개
  B. conflict_axis == "unknown" 10개
  C. primary_pressures에 "group_tension" 포함 15개
  D. primary_pressures에 "group_tension" 미포함 10개
  E. repair.applied == True 5개 이상

중복 제거 후 총 50개 (deterministic seed=42).

Run:
    python -m scripts.labeling.stage4_spotcheck_sample
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "external_private" / "gemma_review" / "work_e46069c4b4_stage3_repaired_private.jsonl"
OUTPUT_PATH = ROOT / "data" / "external_private" / "gemma_review" / "work_e46069c4b4_stage3_spotcheck_private.jsonl"

SEED = 42
TARGET_SIZE = 50


def load_records(path: Path) -> list[dict]:
    out: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(INPUT_PATH)
    records = load_records(INPUT_PATH)
    # exclude error records
    records = [r for r in records if "_error" not in r.get("label", {})]

    rng = random.Random(SEED)

    def label(r: dict) -> dict:
        return r.get("label", {}) or {}

    def conf(r: dict) -> float:
        c = label(r).get("confidence")
        try:
            return float(c) if c is not None else 0.0
        except (TypeError, ValueError):
            return 0.0

    # Category A — low confidence (≤ 0.75) 10
    a_pool = sorted([r for r in records if conf(r) <= 0.75], key=lambda r: r["passage_id"])
    rng.shuffle(a_pool)
    a_pick = a_pool[:10]

    # Category B — conflict_axis unknown 10
    b_pool = sorted([r for r in records if label(r).get("conflict_axis") == "unknown"], key=lambda r: r["passage_id"])
    rng.shuffle(b_pool)
    b_pick = b_pool[:10]

    # Category C — group_tension primary 15
    c_pool = sorted([r for r in records if "group_tension" in (label(r).get("primary_pressures") or [])], key=lambda r: r["passage_id"])
    rng.shuffle(c_pool)
    c_pick = c_pool[:15]

    # Category D — non-group_tension primary 10
    d_pool = sorted([r for r in records if "group_tension" not in (label(r).get("primary_pressures") or [])], key=lambda r: r["passage_id"])
    rng.shuffle(d_pool)
    d_pick = d_pool[:10]

    # Category E — repaired 5+
    e_pool = sorted([r for r in records if r.get("repair", {}).get("applied")], key=lambda r: r["passage_id"])
    rng.shuffle(e_pool)
    e_pick = e_pool[:10]  # take up to 10 just in case

    # Merge and dedupe by passage_id
    chosen: dict[str, dict] = {}
    category_tag: dict[str, list[str]] = {}
    for label_name, picks in [("A_low_conf", a_pick), ("B_unknown_axis", b_pick),
                                ("C_gt_primary", c_pick), ("D_non_gt_primary", d_pick),
                                ("E_repaired", e_pick)]:
        for r in picks:
            pid = r["passage_id"]
            chosen[pid] = r
            category_tag.setdefault(pid, []).append(label_name)

    # If under TARGET_SIZE, supplement deterministically from non-chosen records
    if len(chosen) < TARGET_SIZE:
        remaining = sorted([r for r in records if r["passage_id"] not in chosen], key=lambda r: r["passage_id"])
        rng.shuffle(remaining)
        for r in remaining:
            if len(chosen) >= TARGET_SIZE:
                break
            chosen[r["passage_id"]] = r
            category_tag.setdefault(r["passage_id"], []).append("supplement")
    # If over, trim — preserve at least 5 each of A/B/C/D + 5 from E
    # We aim for exactly 50: keep first 50 by stable order: A, B, C, D, E, then supplement
    ordered_ids: list[str] = []
    seen: set[str] = set()
    for label_name, picks in [("A_low_conf", a_pick), ("B_unknown_axis", b_pick),
                                ("C_gt_primary", c_pick), ("D_non_gt_primary", d_pick),
                                ("E_repaired", e_pick)]:
        for r in picks:
            pid = r["passage_id"]
            if pid not in seen:
                seen.add(pid)
                ordered_ids.append(pid)
    # supplement if needed
    if len(ordered_ids) < TARGET_SIZE:
        remaining_ids = [pid for pid in chosen if pid not in seen]
        ordered_ids.extend(remaining_ids[: TARGET_SIZE - len(ordered_ids)])
    ordered_ids = ordered_ids[:TARGET_SIZE]

    # Final list
    final: list[dict] = []
    for pid in ordered_ids:
        r = chosen[pid]
        out_rec = dict(r)
        out_rec["spotcheck_categories"] = category_tag.get(pid, [])
        out_rec["lee_review"] = {
            "characters_ok": None,
            "pressure_ok": None,
            "desire_ok": None,
            "conflict_axis_ok": None,
            "confidence_ok": None,
            "overall_quality": None,  # Excellent / Good / Weak / Bad
            "note": "",
        }
        final.append(out_rec)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Stats
    cat_counts = {"A_low_conf": 0, "B_unknown_axis": 0, "C_gt_primary": 0,
                  "D_non_gt_primary": 0, "E_repaired": 0, "supplement": 0}
    for r in final:
        for c in r["spotcheck_categories"]:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    print(f"[spotcheck] generated {len(final)} samples")
    print(f"[spotcheck] category counts (with overlaps): {cat_counts}")
    print(f"[spotcheck] private out: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
