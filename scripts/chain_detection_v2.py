"""Baseline comparison V2 — tightened chain detection + arrest split.

실행:
    python scripts/chain_detection_v2.py

변경점 vs v1:
  (1) causal chain을 tick-gap 제약으로 재정의:
      inform → ≤30t → surveillance → ≤30t → betray → ≤30t → arrest
  (2) arrest 측정 2분할:
      endogenous_arrest = trigger-fired ("arrest_trigger") or hazard event ("arrest")
      canonical_arrest  = canonical event "scene_08_arrest" fired

산출:
    docs/person/paper_data/baseline_comparison_v2.json
    docs/person/paper_data/baseline_comparison_v2.txt

기존 엔진/콘텐츠 수정 없음. 새 스크립트만 추가.
"""

from __future__ import annotations

import copy
import json
import statistics
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.peter.pom_scorecard import make_peter_scorecard
from engine.core.world import SimulationConfig
from engine.io.loader import (
    load_agent_state,
    load_behavior_profile,
    load_events,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.rules.base import RuleEngine
from engine.rules.emotional import (
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.slow_recovery import SlowStateFieldRecoveryRule
from engine.rules.temporal import HomeostasisRule
from engine.simulation.pom import evaluate_pom
from engine.simulation.world import SimulationWorld

CONTENT = ROOT / "content"
OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

for _name, _cls in [
    ("faith_journey", FaithJourneyState),
    ("betrayal_psychology", BetrayalPsychologyState),
    ("political_calculation", PoliticalCalculationState),
    ("crowd_dynamics", CrowdDynamicsState),
]:
    register_domain_type(_name, _cls)

N_SEEDS = 10
MAX_TICK = 300
CHAIN_MAX_GAP = 30  # tick


# ===========================================================================
# v1과 동일한 setup 유틸 (복제 — v1 파일 수정 금지 원칙)
# ===========================================================================


def _rules(with_slow_recovery: bool = False) -> RuleEngine:
    rules = [
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ]
    if with_slow_recovery:
        rules.append(SlowStateFieldRecoveryRule(
            moral_injury_rate_per_hour=0.002,
            trust_scar_rate_per_hour=0.001,
        ))
    return RuleEngine(rules)


def _load_base() -> dict:
    return {
        "peter": load_agent_state(CONTENT / "peter" / "initial_state.json"),
        "judas": load_agent_state(CONTENT / "judas" / "initial_state.json"),
        "caiaphas": load_agent_state(CONTENT / "caiaphas" / "initial_state.json"),
        "crowd": load_agent_state(CONTENT / "crowd" / "initial_state.json"),
        "events": load_events(CONTENT / "peter" / "canonical_events.json"),
        "triggers": load_triggers(CONTENT / "shared" / "triggers.json"),
        "hazards": load_hazard_events(CONTENT / "peter" / "hazard_events.json"),
        "profiles": {
            n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
            for n in ["peter", "judas", "caiaphas", "crowd"]
        },
    }


def _randomize_profile(profile: Any) -> Any:
    p = copy.deepcopy(profile)
    for action in p.actions:
        wf = action.weight_formula
        wf.base_weight = 1.0
        wf.state_multipliers = []
    return p


def _run_config(
    base: dict,
    *,
    triggers: Any,
    hazards: Any,
    events: Any,
    profiles: dict,
    agents: list[str],
    rules_engine: RuleEngine,
    seed: int,
) -> Any:
    agent_states = [base[a] for a in agents]
    config = SimulationConfig(
        initial_state=agent_states[0],
        initial_states=agent_states,
        max_tick=MAX_TICK, state_noise_scale=0.02,
        events=events if events else [],
        triggers=triggers if triggers else [],
        hazard_events=hazards if hazards else [],
    )
    return SimulationWorld(
        config, rules_engine,
        behavior_profiles={n: profiles[n] for n in agents if n in profiles},
    ).run(seed=seed)


# ===========================================================================
# v2 측정 함수: chain + split arrest
# ===========================================================================

CANONICAL_ARREST_ID = "scene_08_arrest"
HAZARD_ARREST_ID = "arrest"
ARREST_TRIGGER_ID = "arrest_trigger"


def _split_arrest(result) -> tuple[int | None, int | None]:
    """Returns (canonical_arrest_tick, endogenous_arrest_tick).

    canonical: fired_events 중 event_id == 'scene_08_arrest'
    endogenous: fired_events 중 event_id == 'arrest' (hazard)
                또는 fired_triggers 중 trigger_id == 'arrest_trigger'
    각각 가장 이른 tick (또는 None).
    """
    canonical_tick: int | None = None
    endogenous_tick: int | None = None

    for ev in getattr(result, "fired_events", []):
        eid = str(ev.get("event_id", ""))
        t = int(ev.get("tick", -1))
        if eid == CANONICAL_ARREST_ID:
            if canonical_tick is None or t < canonical_tick:
                canonical_tick = t
        elif eid == HAZARD_ARREST_ID:
            if endogenous_tick is None or t < endogenous_tick:
                endogenous_tick = t

    for tr in getattr(result, "fired_triggers", []):
        tid = str(tr.get("trigger_id", ""))
        t = int(tr.get("tick", -1))
        if tid == ARREST_TRIGGER_ID:
            if endogenous_tick is None or t < endogenous_tick:
                endogenous_tick = t

    return canonical_tick, endogenous_tick


def _chain_with_gap(result, max_gap: int = CHAIN_MAX_GAP) -> tuple[bool, dict]:
    """inform → surveillance → betray → arrest, 각 단계 간 max_gap 이하.

    각 단계 signal source (tick-ordered list의 마지막 match):
      inform:      Caiaphas action 'inform_authorities' OR event/trigger id with 'inform'
      surveillance: Caiaphas action 'order_surveillance' OR trigger 'surveillance'
      betray:      Judas action 'betray' OR event/trigger id with 'betray'
      arrest:      canonical 'scene_08_arrest' OR hazard 'arrest' OR trigger 'arrest_trigger'

    Returns (chain_observed: bool, gap_details: dict) — gap_details는 관측 시 tick 정보.
    """
    keywords = ["inform", "surveillance", "betray", "arrest"]

    # (tick, label_lower, source_tag)
    timeline: list[tuple[int, str, str]] = []

    for e in getattr(result, "fired_events", []):
        eid = str(e.get("event_id", "")).lower()
        t = int(e.get("tick", 0))
        timeline.append((t, eid, "event"))

    for tr in getattr(result, "fired_triggers", []):
        tid = str(tr.get("trigger_id", "")).lower()
        t = int(tr.get("tick", 0))
        timeline.append((t, tid, "trigger"))

    for aid, history in getattr(result, "action_histories", {}).items():
        for a in history:
            action_id = str(getattr(a, "chosen_action", "")).lower()
            t = int(getattr(a, "tick", 0))
            timeline.append((t, f"{aid.lower()}:{action_id}", "action"))

    timeline.sort(key=lambda x: x[0])

    # Greedy sequential search with gap constraint:
    last_tick: int | None = None
    step_ticks: list[int] = []
    idx = 0
    for tick, label, _src in timeline:
        if idx >= len(keywords):
            break
        if keywords[idx] in label:
            if idx == 0:
                # 첫 step: gap 제약 없음
                step_ticks.append(tick)
                last_tick = tick
                idx += 1
            else:
                # 이후 step: last_tick 후 max_gap 이내에만 count
                if last_tick is not None and (tick - last_tick) <= max_gap:
                    step_ticks.append(tick)
                    last_tick = tick
                    idx += 1
                elif last_tick is not None and (tick - last_tick) > max_gap:
                    # gap 초과 → 현재 진행 폐기, 다시 새 inform부터 시작 (greedy restart)
                    # 다만 만약 지금 라벨이 keyword[0] (inform) 이면 새 시작
                    if keywords[0] in label:
                        step_ticks = [tick]
                        last_tick = tick
                        idx = 1

    observed = idx == len(keywords)
    details: dict[str, Any] = {
        "chain_observed": observed,
        "max_gap_constraint": max_gap,
    }
    if observed:
        details["step_ticks"] = step_ticks
        details["gaps"] = [
            step_ticks[i + 1] - step_ticks[i] for i in range(len(step_ticks) - 1)
        ]
    return observed, details


def _multiagent_to_peter_sim_result(result) -> Any:
    all_action_histories = getattr(result, "action_histories", {})
    peter_actions = all_action_histories.get("peter", [])
    all_snaps = getattr(result, "state_snapshots", {})
    peter_snaps = all_snaps.get("peter", {}) if isinstance(all_snaps, dict) else {}
    peter_final = getattr(result, "final_states", {}).get("peter")
    if peter_final is None and peter_snaps:
        peter_final = peter_snaps[max(peter_snaps.keys())]
    return SimpleNamespace(
        action_history=peter_actions,
        state_snapshots=peter_snaps,
        final_state=peter_final,
        fired_events=getattr(result, "fired_events", []),
    )


def _pom_all_pass(result) -> bool:
    adapter = _multiagent_to_peter_sim_result(result)
    if adapter.final_state is None:
        return False
    try:
        ev = evaluate_pom(adapter, make_peter_scorecard())
        return all(ev.values())
    except Exception:
        return False


def _measure_condition_v2(runs: list[Any]) -> dict[str, Any]:
    canonical_ticks: list[int] = []
    endogenous_ticks: list[int] = []
    chain_hits = 0
    chain_gaps: list[list[int]] = []
    pom_passes = 0
    final_fears: list[float] = []
    final_hopes: list[float] = []

    for r in runs:
        can_t, endo_t = _split_arrest(r)
        if can_t is not None and can_t > 0:
            canonical_ticks.append(can_t)
        if endo_t is not None and endo_t > 0:
            endogenous_ticks.append(endo_t)
        observed, details = _chain_with_gap(r)
        if observed:
            chain_hits += 1
            chain_gaps.append(details.get("gaps", []))
        if _pom_all_pass(r):
            pom_passes += 1
        peter_state = getattr(r, "final_states", {}).get("peter")
        if peter_state is not None:
            final_fears.append(float(peter_state.emotions.fear))
            final_hopes.append(float(peter_state.emotions.hope))

    n = len(runs)
    # 평균 gap (step 3개, chain 관측된 run만)
    mean_gaps: list[float] | None = None
    if chain_gaps:
        by_step = list(zip(*chain_gaps))
        mean_gaps = [round(statistics.mean(step_vals), 2) for step_vals in by_step]

    return {
        "n_runs": n,
        "canonical_arrest_rate": len(canonical_ticks) / n if n else 0.0,
        "canonical_arrest_tick_mean": (
            round(statistics.mean(canonical_ticks), 2) if canonical_ticks else None
        ),
        "endogenous_arrest_rate": len(endogenous_ticks) / n if n else 0.0,
        "endogenous_arrest_tick_mean": (
            round(statistics.mean(endogenous_ticks), 2)
            if endogenous_ticks else None
        ),
        "causal_chain_rate_gap_constrained": chain_hits / n if n else 0.0,
        "chain_mean_gaps_per_step": mean_gaps,  # [inform→surv, surv→betray, betray→arrest]
        "pom_all_pass_rate": pom_passes / n if n else 0.0,
        "final_fear_mean": (
            round(statistics.mean(final_fears), 3) if final_fears else None
        ),
        "final_hope_mean": (
            round(statistics.mean(final_hopes), 3) if final_hopes else None
        ),
    }


# ===========================================================================
# Baselines (v1과 동일 조건)
# ===========================================================================


def baseline_no_trigger(base):
    print("[baseline] no_trigger ...")
    runs = [
        _run_config(base, triggers=[], hazards=base["hazards"], events=base["events"],
                    profiles=base["profiles"],
                    agents=["peter", "judas", "caiaphas", "crowd"],
                    rules_engine=_rules(), seed=s)
        for s in range(N_SEEDS)
    ]
    return _measure_condition_v2(runs)


def baseline_exogenous_only(base):
    print("[baseline] exogenous_only ...")
    runs = [
        _run_config(base, triggers=[], hazards=[], events=base["events"],
                    profiles=base["profiles"],
                    agents=["peter", "judas", "caiaphas", "crowd"],
                    rules_engine=_rules(), seed=s)
        for s in range(N_SEEDS)
    ]
    return _measure_condition_v2(runs)


def baseline_single_agent(base):
    print("[baseline] single_agent ...")
    runs = [
        _run_config(base, triggers=[], hazards=base["hazards"], events=base["events"],
                    profiles={"peter": base["profiles"]["peter"]},
                    agents=["peter"],
                    rules_engine=_rules(), seed=s)
        for s in range(N_SEEDS)
    ]
    return _measure_condition_v2(runs)


def baseline_random_behavior(base):
    print("[baseline] random_behavior ...")
    randomized = {n: _randomize_profile(p) for n, p in base["profiles"].items()}
    runs = [
        _run_config(base, triggers=base["triggers"], hazards=base["hazards"],
                    events=base["events"], profiles=randomized,
                    agents=["peter", "judas", "caiaphas", "crowd"],
                    rules_engine=_rules(), seed=s)
        for s in range(N_SEEDS)
    ]
    return _measure_condition_v2(runs)


def full_system(base):
    print("[baseline] full_system ...")
    runs = [
        _run_config(base, triggers=base["triggers"], hazards=base["hazards"],
                    events=base["events"], profiles=base["profiles"],
                    agents=["peter", "judas", "caiaphas", "crowd"],
                    rules_engine=_rules(), seed=s)
        for s in range(N_SEEDS)
    ]
    return _measure_condition_v2(runs)


# ===========================================================================
# Ablation levels (v1과 동일)
# ===========================================================================


def ablation_level_0(base):
    print("[ablation] level_0_hazard_only ...")
    runs = [_run_config(base, triggers=[], hazards=base["hazards"], events=[],
                        profiles={"peter": base["profiles"]["peter"]},
                        agents=["peter"], rules_engine=_rules(), seed=s)
            for s in range(N_SEEDS)]
    return _measure_condition_v2(runs)


def ablation_level_1(base):
    print("[ablation] level_1_hazard_trigger ...")
    runs = [_run_config(base, triggers=base["triggers"], hazards=base["hazards"],
                        events=[], profiles={"peter": base["profiles"]["peter"]},
                        agents=["peter"], rules_engine=_rules(), seed=s)
            for s in range(N_SEEDS)]
    return _measure_condition_v2(runs)


def ablation_level_2(base):
    print("[ablation] level_2_multi_agent ...")
    runs = [_run_config(base, triggers=base["triggers"], hazards=base["hazards"],
                        events=[], profiles=base["profiles"],
                        agents=["peter", "judas", "caiaphas", "crowd"],
                        rules_engine=_rules(), seed=s)
            for s in range(N_SEEDS)]
    return _measure_condition_v2(runs)


def ablation_level_3(base):
    print("[ablation] level_3_with_canonical ...")
    runs = [_run_config(base, triggers=base["triggers"], hazards=base["hazards"],
                        events=base["events"], profiles=base["profiles"],
                        agents=["peter", "judas", "caiaphas", "crowd"],
                        rules_engine=_rules(with_slow_recovery=False), seed=s)
            for s in range(N_SEEDS)]
    return _measure_condition_v2(runs)


def ablation_level_4(base):
    print("[ablation] level_4_full_system ...")
    runs = [_run_config(base, triggers=base["triggers"], hazards=base["hazards"],
                        events=base["events"], profiles=base["profiles"],
                        agents=["peter", "judas", "caiaphas", "crowd"],
                        rules_engine=_rules(with_slow_recovery=True), seed=s)
            for s in range(N_SEEDS)]
    return _measure_condition_v2(runs)


# ===========================================================================
# Output helpers
# ===========================================================================


def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.3f}"
    if isinstance(v, list):
        return "[" + ",".join(f"{x:.1f}" if isinstance(x, float) else str(x) for x in v) + "]"
    return str(v)


def _write_text_summary(out: dict) -> None:
    lines = []
    lines.append(
        f"Witness baseline v2 — chain(gap<={CHAIN_MAX_GAP}) + arrest split"
    )
    lines.append(f"(n_seeds={out['n_seeds']}, max_tick={out['max_tick']})")
    lines.append("=" * 100)
    lines.append("")

    hdr = (
        f"{'condition':<26} {'can_arr':>8} {'endo_arr':>9} "
        f"{'chain':>7} {'POM':>7} {'fear':>7} {'gaps':>24}"
    )
    lines.append(hdr)
    lines.append("-" * len(hdr))

    lines.append("[BASELINES vs FULL]")
    order = [
        "no_trigger", "exogenous_only", "single_agent",
        "random_behavior", "full_system",
    ]
    for k in order:
        d = out["baselines"][k]
        lines.append(
            f"{k:<26} "
            f"{_fmt(d['canonical_arrest_rate']):>8} "
            f"{_fmt(d['endogenous_arrest_rate']):>9} "
            f"{_fmt(d['causal_chain_rate_gap_constrained']):>7} "
            f"{_fmt(d['pom_all_pass_rate']):>7} "
            f"{_fmt(d['final_fear_mean']):>7} "
            f"{_fmt(d['chain_mean_gaps_per_step']):>24}"
        )

    lines.append("")
    lines.append("[ABLATION HIERARCHY]")
    lines.append("-" * len(hdr))
    for k in [
        "level_0_hazard_only", "level_1_hazard_trigger",
        "level_2_multi_agent", "level_3_with_canonical",
        "level_4_full_system",
    ]:
        d = out["ablation"][k]
        lines.append(
            f"{k:<26} "
            f"{_fmt(d['canonical_arrest_rate']):>8} "
            f"{_fmt(d['endogenous_arrest_rate']):>9} "
            f"{_fmt(d['causal_chain_rate_gap_constrained']):>7} "
            f"{_fmt(d['pom_all_pass_rate']):>7} "
            f"{_fmt(d['final_fear_mean']):>7} "
            f"{_fmt(d['chain_mean_gaps_per_step']):>24}"
        )

    lines.append("")
    lines.append("=" * 100)
    full = out["baselines"]["full_system"]
    lines.append("VERDICT v2 (Full vs each baseline, chain-strict + endo_arrest metrics):")
    for k in ["no_trigger", "exogenous_only", "single_agent", "random_behavior"]:
        b = out["baselines"][k]
        endo_better = full["endogenous_arrest_rate"] >= b["endogenous_arrest_rate"]
        chain_better = (
            full["causal_chain_rate_gap_constrained"]
            >= b["causal_chain_rate_gap_constrained"]
        )
        pom_better = full["pom_all_pass_rate"] >= b["pom_all_pass_rate"]
        all_three = endo_better and chain_better and pom_better
        lines.append(
            f"  Full > {k}: "
            f"endo_arrest={endo_better}, chain={chain_better}, POM={pom_better}  "
            f"[{'PASS' if all_three else 'MIXED'}]"
        )

    text = "\n".join(lines) + "\n"
    (OUT_DIR / "baseline_comparison_v2.txt").write_text(text, encoding="utf-8")
    for line in lines:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))


def main() -> None:
    t0 = time.time()
    base = _load_base()
    out: dict[str, Any] = {
        "schema_version": 2,
        "n_seeds": N_SEEDS,
        "max_tick": MAX_TICK,
        "chain_max_gap_tick": CHAIN_MAX_GAP,
        "notes": (
            "V2 measurements: "
            "(1) chain requires inform→surv→betray→arrest with each step within "
            f"{CHAIN_MAX_GAP} tick of previous; "
            "(2) arrest split into canonical (scene_08_arrest) vs endogenous "
            "(hazard 'arrest' or fired_trigger 'arrest_trigger')."
        ),
    }
    out["baselines"] = {
        "no_trigger": baseline_no_trigger(base),
        "exogenous_only": baseline_exogenous_only(base),
        "single_agent": baseline_single_agent(base),
        "random_behavior": baseline_random_behavior(base),
        "full_system": full_system(base),
    }
    out["ablation"] = {
        "level_0_hazard_only": ablation_level_0(base),
        "level_1_hazard_trigger": ablation_level_1(base),
        "level_2_multi_agent": ablation_level_2(base),
        "level_3_with_canonical": ablation_level_3(base),
        "level_4_full_system": ablation_level_4(base),
    }
    out["total_runtime_seconds"] = round(time.time() - t0, 2)

    dest = OUT_DIR / "baseline_comparison_v2.json"
    dest.write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8",
    )
    print()
    _write_text_summary(out)
    print(f"[done] wrote {dest} ({out['total_runtime_seconds']}s)")


if __name__ == "__main__":
    main()
