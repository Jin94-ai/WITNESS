"""Hazard scaling experiment (counterfactual_experiment_prompt.md — 실험 2).

실행:
    python scripts/hazard_scaling.py

모든 hazard event의 base_rate를 factor로 곱해서 6개 조건 측정:
  factor ∈ [1.0, 0.75, 0.5, 0.25, 0.10, 0.0]

factor=0.0 → hazards=[] (완전 제거).

측정: v2 메트릭 (canonical_arrest / endogenous_arrest / chain / POM / fear).

Pattern 판정:
  - emergence: 1.0→0.0 갈수록 endo_arrest 점진적 감소 (monotonic drop)
  - threshold: 중간 factor에서 급감 (all-or-nothing)
  - inevitability: 어떤 factor에서도 endo_arrest ≈ 1.0 유지

산출: docs/person/paper_data/hazard_scaling.json + .txt
기존 코드 수정 금지. base_rate 수정은 deepcopy 후 메모리 내에서만.
"""

from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from chain_detection_v2 import (  # noqa: E402
    CHAIN_MAX_GAP,
    MAX_TICK,
    N_SEEDS,
    _load_base,
    _measure_condition_v2,
    _rules,
    _run_config,
)

OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FACTORS = [1.0, 0.75, 0.5, 0.25, 0.10, 0.0]
ALL_AGENTS = ["peter", "judas", "caiaphas", "crowd"]

ARREST_TRIGGER_ID = "arrest_trigger"


def _trigger_arrest_rate(runs: list) -> float:
    """arrest_trigger가 fire된 run 비율 (V3 metric)."""
    if not runs:
        return 0.0
    hits = 0
    for r in runs:
        for tr in getattr(r, "fired_triggers", []):
            if str(tr.get("trigger_id", "")) == ARREST_TRIGGER_ID:
                hits += 1
                break
    return hits / len(runs)


def _measure_extended(runs: list):
    d = _measure_condition_v2(runs)
    d["trigger_arrest_rate"] = _trigger_arrest_rate(runs)
    return d


def _scaled_hazards(base_hazards: list, factor: float) -> list:
    """hazard_events deepcopy + base_rate *= factor.

    factor=0.0 이면 빈 리스트 반환 (완전 제거).
    """
    if factor == 0.0:
        return []
    scaled = copy.deepcopy(base_hazards)
    for h in scaled:
        # HazardEvent.hazard: HazardFunction with base_rate attribute
        hf = getattr(h, "hazard", None)
        if hf is None:
            continue
        current = getattr(hf, "base_rate", 0.0)
        try:
            # Pydantic BaseModel이면 setattr 가능 (Pydantic v2)
            hf.base_rate = float(current) * factor
        except Exception:
            # validation 차단된 경우 dict 거쳐서 재설정
            try:
                h.hazard = hf.model_copy(
                    update={"base_rate": float(current) * factor},
                )
            except Exception:
                pass
    return scaled


def _run_factor(base: dict, factor: float) -> dict[str, Any]:
    print(f"[hazard_scaling] factor={factor:.2f} ...")
    hazards = _scaled_hazards(base["hazards"], factor)
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=hazards,
            events=base["events"], profiles=base["profiles"],
            agents=ALL_AGENTS, rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_extended(runs)


def _classify_pattern(factor_results: dict[str, dict]) -> dict[str, Any]:
    """endogenous_arrest_rate vs factor의 관계로 pattern 판정.

    emergence:    factor 감소 시 endo_arrest 유의하게 감소 (max-min >= 0.3 AND monotonic)
    threshold:    중간 factor에서 급감 (인접 factor 간 delta >= 0.5)
    inevitability: 모든 factor에서 endo_arrest >= 0.9
    """
    sorted_factors = sorted(
        [float(f) for f in factor_results.keys()], reverse=True,
    )
    endo = [factor_results[f"{f:.2f}"]["endogenous_arrest_rate"] for f in sorted_factors]

    max_e = max(endo)
    min_e = min(endo)
    spread = max_e - min_e

    # monotonic (strictly non-increasing)
    monotonic = all(endo[i] >= endo[i + 1] for i in range(len(endo) - 1))

    # adjacent max delta
    max_delta = max(
        (endo[i] - endo[i + 1]) for i in range(len(endo) - 1)
    ) if len(endo) > 1 else 0.0

    # collapse factor: endo_arrest가 처음으로 0.2 이하로 떨어진 factor
    collapse_factor: float | None = None
    for f, e in zip(sorted_factors, endo):
        if e <= 0.2:
            collapse_factor = f
            break

    if min_e >= 0.9:
        pattern = "inevitability"
    elif spread >= 0.3 and monotonic:
        pattern = "emergence"
    elif max_delta >= 0.5:
        pattern = "threshold"
    else:
        pattern = "mixed"

    return {
        "pattern": pattern,
        "endo_arrest_range": [min_e, max_e],
        "spread": round(spread, 3),
        "monotonic_non_increasing": monotonic,
        "max_adjacent_delta": round(max_delta, 3),
        "collapse_factor": collapse_factor,
        "endo_by_factor_descending": list(zip(sorted_factors, endo)),
    }


# ===========================================================================
# output
# ===========================================================================


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.3f}"
    if isinstance(v, list):
        return (
            "[" +
            ",".join(f"{x:.1f}" if isinstance(x, float) else str(x) for x in v) +
            "]"
        )
    return str(v)


def _write_text_summary(out: dict) -> None:
    lines = []
    lines.append(
        f"Witness hazard scaling "
        f"(n_seeds={out['n_seeds']}, max_tick={out['max_tick']}, "
        f"chain_gap<={CHAIN_MAX_GAP})"
    )
    lines.append("=" * 100)
    lines.append("")

    hdr = (
        f"{'factor':<8} {'can_arr':>8} {'endo_arr':>9} {'trig_arr':>9} "
        f"{'chain':>7} {'POM':>7} {'fear':>7} {'endo_mean_tick':>16}"
    )
    lines.append(hdr)
    lines.append("-" * len(hdr))

    for f in sorted(out["factors"].keys(), key=lambda x: -float(x)):
        d = out["factors"][f]
        lines.append(
            f"{f:<8} "
            f"{_fmt(d['canonical_arrest_rate']):>8} "
            f"{_fmt(d['endogenous_arrest_rate']):>9} "
            f"{_fmt(d['trigger_arrest_rate']):>9} "
            f"{_fmt(d['causal_chain_rate_gap_constrained']):>7} "
            f"{_fmt(d['pom_all_pass_rate']):>7} "
            f"{_fmt(d['final_fear_mean']):>7} "
            f"{_fmt(d['endogenous_arrest_tick_mean']):>16}"
        )

    lines.append("")
    lines.append("PATTERN CLASSIFICATION")
    lines.append("-" * len(hdr))
    p = out["pattern_analysis"]
    lines.append(f"  pattern:            {p['pattern']}")
    lines.append(
        f"  endo_arrest range:  "
        f"[{p['endo_arrest_range'][0]:.3f}, {p['endo_arrest_range'][1]:.3f}]"
    )
    lines.append(f"  spread:             {p['spread']}")
    lines.append(f"  monotonic:          {p['monotonic_non_increasing']}")
    lines.append(f"  max adjacent delta: {p['max_adjacent_delta']}")
    lines.append(
        f"  collapse factor:    {p['collapse_factor']}  "
        "(first factor where endo_arrest <= 0.2; None = never collapses)"
    )

    text = "\n".join(lines) + "\n"
    (OUT_DIR / "hazard_scaling.txt").write_text(text, encoding="utf-8")
    for line in lines:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))


def main() -> None:
    t0 = time.time()
    base = _load_base()
    out: dict[str, Any] = {
        "schema_version": 1,
        "experiment": "hazard_scaling",
        "n_seeds": N_SEEDS,
        "max_tick": MAX_TICK,
        "chain_max_gap_tick": CHAIN_MAX_GAP,
        "factors_applied": FACTORS,
        "notes": (
            "Scale every hazard_event.hazard.base_rate by factor. "
            "factor=0.0 → hazards=[]. "
            "All other config unchanged (triggers, canonical_events, 4 agents, "
            "default profiles)."
        ),
    }
    out["factors"] = {
        f"{f:.2f}": _run_factor(base, f) for f in FACTORS
    }
    out["pattern_analysis"] = _classify_pattern(out["factors"])
    out["total_runtime_seconds"] = round(time.time() - t0, 2)

    dest = OUT_DIR / "hazard_scaling.json"
    dest.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print()
    _write_text_summary(out)
    print(f"[done] wrote {dest} ({out['total_runtime_seconds']}s)")


if __name__ == "__main__":
    main()
