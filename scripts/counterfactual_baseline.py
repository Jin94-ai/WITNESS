"""Counterfactual causal metric (counterfactual_experiment_prompt.md — 실험 1).

실행:
    python scripts/counterfactual_baseline.py

5 조건 × 10 seed × 300 tick:
  (1) full_system
  (2) judas_removed
  (3) caiaphas_removed
  (4) trigger_removed
  (5) random_no_judas

측정: v2 메트릭 (canonical_arrest / endogenous_arrest / chain gap<=30 / POM / emotion).

3 verdict 자동 판정:
  - causal_dependency (Judas 제거 시 endo_arrest 소멸?)
  - trigger_necessity (trigger 제거 시 chain 소멸?)
  - random_chain_nature (random+no-Judas chain이 random chain보다 감소?)

산출: docs/person/paper_data/causal_counterfactual.json + .txt
기존 코드 수정 금지. scripts/chain_detection_v2.py의 helpers 재사용.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# chain_detection_v2.py의 helpers 재사용 (V2 측정 통일성)
from chain_detection_v2 import (  # noqa: E402
    CHAIN_MAX_GAP,
    MAX_TICK,
    N_SEEDS,
    _load_base,
    _measure_condition_v2,
    _randomize_profile,
    _rules,
    _run_config,
)

OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ===========================================================================
# V3 metric: trigger_arrest_rate — arrest_trigger fired_triggers only
# (hazard "arrest" event와 분리)
# ===========================================================================

ARREST_TRIGGER_ID = "arrest_trigger"


def _trigger_arrest_rate(runs: list) -> float:
    """arrest_trigger가 실제 fire된 run 비율.

    V2 endogenous_arrest는 hazard event "arrest" + trigger "arrest_trigger" 합.
    V3는 trigger만 분리 측정 — 진짜 causal chain의 end-point 지표.
    """
    if not runs:
        return 0.0
    hits = 0
    for r in runs:
        for tr in getattr(r, "fired_triggers", []):
            if str(tr.get("trigger_id", "")) == ARREST_TRIGGER_ID:
                hits += 1
                break
    return hits / len(runs)


def _measure_extended(runs: list) -> dict[str, Any]:
    d = _measure_condition_v2(runs)
    d["trigger_arrest_rate"] = _trigger_arrest_rate(runs)
    return d


# ===========================================================================
# 5 conditions
# ===========================================================================

ALL_AGENTS = ["peter", "judas", "caiaphas", "crowd"]


def cond_full_system(base: dict) -> dict[str, Any]:
    print("[cond] full_system ...")
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=base["profiles"],
            agents=ALL_AGENTS, rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_extended(runs)


def cond_judas_removed(base: dict) -> dict[str, Any]:
    """initial_states에서 judas 제거 + profiles에서 judas 제거."""
    print("[cond] judas_removed ...")
    agents = [a for a in ALL_AGENTS if a != "judas"]
    profiles = {n: p for n, p in base["profiles"].items() if n != "judas"}
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=profiles,
            agents=agents, rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_extended(runs)


def cond_caiaphas_removed(base: dict) -> dict[str, Any]:
    print("[cond] caiaphas_removed ...")
    agents = [a for a in ALL_AGENTS if a != "caiaphas"]
    profiles = {n: p for n, p in base["profiles"].items() if n != "caiaphas"}
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=profiles,
            agents=agents, rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_extended(runs)


def cond_trigger_removed(base: dict) -> dict[str, Any]:
    print("[cond] trigger_removed ...")
    runs = [
        _run_config(
            base, triggers=[], hazards=base["hazards"],
            events=base["events"], profiles=base["profiles"],
            agents=ALL_AGENTS, rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_extended(runs)


def cond_random_no_judas(base: dict) -> dict[str, Any]:
    """Judas 제거 + 나머지 profile을 uniform random."""
    print("[cond] random_no_judas ...")
    agents = [a for a in ALL_AGENTS if a != "judas"]
    randomized = {
        n: _randomize_profile(p)
        for n, p in base["profiles"].items() if n != "judas"
    }
    runs = [
        _run_config(
            base, triggers=base["triggers"], hazards=base["hazards"],
            events=base["events"], profiles=randomized,
            agents=agents, rules_engine=_rules(), seed=s,
        )
        for s in range(N_SEEDS)
    ]
    return _measure_extended(runs)


# ===========================================================================
# Verdict logic
# ===========================================================================


def _compute_verdicts(
    conditions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    full = conditions["full_system"]
    judas_removed = conditions["judas_removed"]
    trigger_removed = conditions["trigger_removed"]
    random_no_judas = conditions["random_no_judas"]

    # (1) causal_dependency: Judas 제거 시 endogenous arrest 소멸?
    #   V2 기준: endogenous_arrest = hazard "arrest" event OR arrest_trigger
    #       → Judas 없어도 hazard 'arrest'는 fire되므로 1.0 유지 (CAUSAL_FAIL 예상)
    #   V3 기준: trigger_arrest_rate만으로 판정 — arrest_trigger가 Judas 조건 필요
    #       → Judas 제거 시 arrest_trigger fire 불가 → 0.0 (CAUSAL_PASS 기대)
    full_endo = full["endogenous_arrest_rate"]
    jr_endo = judas_removed["endogenous_arrest_rate"]
    if full_endo >= 0.8 and jr_endo <= 0.2:
        causal_verdict_v2 = "CAUSAL_PASS"
    else:
        causal_verdict_v2 = "CAUSAL_FAIL"

    # V3 (trigger_arrest_rate only — Judas의 state_conditions가 arrest_trigger에 걸려있음)
    full_trig = full["trigger_arrest_rate"]
    jr_trig = judas_removed["trigger_arrest_rate"]
    if full_trig >= 0.5 and jr_trig <= 0.2:
        causal_verdict_v3 = "CAUSAL_PASS"
    else:
        causal_verdict_v3 = "CAUSAL_FAIL"

    causal_verdict = causal_verdict_v3  # V3가 더 정확


    # (2) trigger_necessity:
    #   full chain ≥ 0.05 AND trigger_removed chain == 0.0 → TRIGGER_NECESSARY
    full_chain = full["causal_chain_rate_gap_constrained"]
    tr_chain = trigger_removed["causal_chain_rate_gap_constrained"]
    if full_chain >= 0.05 and tr_chain == 0.0:
        trigger_verdict = "TRIGGER_NECESSARY"
    else:
        trigger_verdict = "TRIGGER_NOT_NECESSARY"

    # (3) random_chain_nature: random_no_judas chain < baseline v2 random(0.60)
    #   random_no_judas chain이 더 작으면 SPURIOUS (random의 chain 구조적 아님)
    RANDOM_WITH_JUDAS_BASELINE = 0.60  # chain_detection_v2.py 결과
    rnj_chain = random_no_judas["causal_chain_rate_gap_constrained"]
    if rnj_chain < RANDOM_WITH_JUDAS_BASELINE:
        random_verdict = "RANDOM_CHAIN_SPURIOUS"
    else:
        random_verdict = "RANDOM_CHAIN_STRUCTURAL"

    return {
        "causal_dependency": causal_verdict,
        "causal_dependency_v2": causal_verdict_v2,
        "causal_dependency_v3": causal_verdict_v3,
        "causal_dependency_detail": {
            "v2_endogenous_arrest_inc_hazard": {
                "full": full_endo, "judas_removed": jr_endo,
                "note": (
                    "V2 endogenous_arrest includes hazard 'arrest' events "
                    "(Peter-state driven) → Judas removal doesn't shrink."
                ),
            },
            "v3_trigger_arrest_only": {
                "full": full_trig, "judas_removed": jr_trig,
                "note": (
                    "V3 isolates arrest_trigger whose state_conditions require "
                    "Judas disillusionment + Caiaphas threat + Judas betray action. "
                    "Judas removal → trigger cannot fire."
                ),
            },
            "thresholds": {
                "v2_full_ge": 0.8, "v2_removed_le": 0.2,
                "v3_full_ge": 0.5, "v3_removed_le": 0.2,
            },
        },
        "trigger_necessity": trigger_verdict,
        "trigger_necessity_detail": {
            "full_chain_rate": full_chain,
            "trigger_removed_chain_rate": tr_chain,
            "threshold_full_ge": 0.05,
            "threshold_removed_eq": 0.0,
        },
        "random_chain_nature": random_verdict,
        "random_chain_nature_detail": {
            "random_with_judas_baseline_v2": RANDOM_WITH_JUDAS_BASELINE,
            "random_no_judas_chain": rnj_chain,
            "judged_spurious_if_less_than": RANDOM_WITH_JUDAS_BASELINE,
        },
    }


# ===========================================================================
# Output
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
        f"Witness counterfactual causal metric "
        f"(n_seeds={out['n_seeds']}, max_tick={out['max_tick']}, "
        f"chain_gap<={CHAIN_MAX_GAP})"
    )
    lines.append("=" * 100)
    lines.append("")

    hdr = (
        f"{'condition':<22} {'can_arr':>8} {'endo_arr':>9} "
        f"{'trig_arr':>9} {'chain':>7} {'POM':>7} {'fear':>7} {'hope':>7}"
    )
    lines.append(hdr)
    lines.append("-" * len(hdr))

    order = [
        "full_system", "judas_removed", "caiaphas_removed",
        "trigger_removed", "random_no_judas",
    ]
    for k in order:
        d = out["conditions"][k]
        lines.append(
            f"{k:<22} "
            f"{_fmt(d['canonical_arrest_rate']):>8} "
            f"{_fmt(d['endogenous_arrest_rate']):>9} "
            f"{_fmt(d['trigger_arrest_rate']):>9} "
            f"{_fmt(d['causal_chain_rate_gap_constrained']):>7} "
            f"{_fmt(d['pom_all_pass_rate']):>7} "
            f"{_fmt(d['final_fear_mean']):>7} "
            f"{_fmt(d['final_hope_mean']):>7}"
        )

    lines.append("")
    lines.append("VERDICTS")
    lines.append("-" * len(hdr))
    v = out["verdicts"]
    v2_det = v["causal_dependency_detail"]["v2_endogenous_arrest_inc_hazard"]
    v3_det = v["causal_dependency_detail"]["v3_trigger_arrest_only"]
    lines.append(
        f"  causal_dependency [V3/final]: {v['causal_dependency']}  "
        f"(V3 trigger_arrest: full={_fmt(v3_det['full'])} "
        f"vs judas_removed={_fmt(v3_det['judas_removed'])})"
    )
    lines.append(
        f"  causal_dependency [V2/hazard-incl]: {v['causal_dependency_v2']}  "
        f"(V2 endo inc hazard: full={_fmt(v2_det['full'])} "
        f"vs judas_removed={_fmt(v2_det['judas_removed'])} — "
        f"Judas 제거 시에도 hazard 'arrest' event는 fire되므로 V2는 FAIL 예상)"
    )
    lines.append(
        f"  trigger_necessity:   {v['trigger_necessity']}  "
        f"(full chain {_fmt(v['trigger_necessity_detail']['full_chain_rate'])} "
        f"vs trigger_removed chain "
        f"{_fmt(v['trigger_necessity_detail']['trigger_removed_chain_rate'])})"
    )
    lines.append(
        f"  random_chain_nature: {v['random_chain_nature']}  "
        f"(random+no-judas chain "
        f"{_fmt(v['random_chain_nature_detail']['random_no_judas_chain'])} "
        f"vs random-with-judas baseline "
        f"{_fmt(v['random_chain_nature_detail']['random_with_judas_baseline_v2'])})"
    )

    lines.append("")
    lines.append("=" * 100)
    all_pass = (
        v["causal_dependency"] == "CAUSAL_PASS"
        and v["trigger_necessity"] == "TRIGGER_NECESSARY"
        and v["random_chain_nature"] == "RANDOM_CHAIN_SPURIOUS"
    )
    lines.append(
        f"FINAL: Full system causal structure counterfactually validated? "
        f"{'YES' if all_pass else 'NO'}"
    )

    text = "\n".join(lines) + "\n"
    (OUT_DIR / "causal_counterfactual.txt").write_text(text, encoding="utf-8")
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
        "experiment": "counterfactual_causal",
        "n_seeds": N_SEEDS,
        "max_tick": MAX_TICK,
        "chain_max_gap_tick": CHAIN_MAX_GAP,
        "notes": (
            "Counterfactual agent/trigger removal to validate causal structure. "
            "Each condition is a single modification from full_system. "
            "Measurements use v2 definitions: split arrest (canonical vs endogenous) "
            f"and chain with gap<={CHAIN_MAX_GAP} tick constraint."
        ),
    }
    out["conditions"] = {
        "full_system": cond_full_system(base),
        "judas_removed": cond_judas_removed(base),
        "caiaphas_removed": cond_caiaphas_removed(base),
        "trigger_removed": cond_trigger_removed(base),
        "random_no_judas": cond_random_no_judas(base),
    }
    out["verdicts"] = _compute_verdicts(out["conditions"])
    out["total_runtime_seconds"] = round(time.time() - t0, 2)

    dest = OUT_DIR / "causal_counterfactual.json"
    dest.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print()
    _write_text_summary(out)
    print(f"[done] wrote {dest} ({out['total_runtime_seconds']}s)")


if __name__ == "__main__":
    main()
