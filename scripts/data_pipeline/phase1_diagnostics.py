"""Spike 6 연장 — Phase 1 진단 6종 실행기 (read-only).

Spec: WITNESS_SPIKE_6_DATA_PIPELINE.md §2. Engine / content 수정 금지.

실행:
    python scripts/data_pipeline/phase1_diagnostics.py

산출물: docs/person/diagnostics/*.md 6개
"""

from __future__ import annotations

import copy
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DIAG = ROOT / "docs" / "person" / "diagnostics"
CONTENT = ROOT / "content"

from content.caiaphas.domain_politics import PoliticalCalculationState  # noqa: E402
from content.crowd.domain_crowd import CrowdDynamicsState  # noqa: E402
from content.judas.domain_betrayal import BetrayalPsychologyState  # noqa: E402
from content.peter.domain_faith import FaithJourneyState  # noqa: E402
from engine.core.state import AgentState, EmotionalState, PhysicalState  # noqa: E402
from engine.core.world import SimulationConfig  # noqa: E402
from engine.io.loader import (  # noqa: E402
    load_agent_state,
    load_behavior_profile,
    load_events,
    load_hazard_events,
    load_triggers,
    register_domain_type,
)
from engine.policies.neural.dataset import build_behavior_cloning_dataset  # noqa: E402
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import (  # noqa: E402
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from engine.simulation.decision import decide_action  # noqa: E402
from engine.simulation.training_samples import state_to_feature_vector  # noqa: E402
from engine.simulation.world import SimulationWorld  # noqa: E402

FEATURE_NAMES = [
    "emotions.fear", "emotions.hope", "emotions.grief",
    "emotions.confusion", "emotions.love",
    "physical.fatigue", "physical.hunger", "physical.health",
    "slow_state.moral_injury", "slow_state.identity_shift",
    "slow_state.event_trauma", "slow_state.trust_scar",
]


def _register() -> None:
    for t, c in [
        ("faith_journey", FaithJourneyState),
        ("betrayal_psychology", BetrayalPsychologyState),
        ("political_calculation", PoliticalCalculationState),
        ("crowd_dynamics", CrowdDynamicsState),
    ]:
        register_domain_type(t, c)


def _rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _profiles() -> dict:
    return {
        "peter": load_behavior_profile(CONTENT / "peter" / "behavior_profile.json"),
        "judas": load_behavior_profile(CONTENT / "judas" / "behavior_profile.json"),
        "caiaphas": load_behavior_profile(CONTENT / "caiaphas" / "behavior_profile.json"),
        "crowd": load_behavior_profile(CONTENT / "crowd" / "behavior_profile.json"),
    }


def _build_config(max_tick: int = 100, *, seed_override: AgentState | None = None) -> SimulationConfig:
    peter = seed_override or load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    return SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )


def _run_peter(seed: int, max_tick: int = 100, peter_override: AgentState | None = None):
    cfg = _build_config(max_tick=max_tick, seed_override=peter_override)
    return SimulationWorld(cfg, _rules(), behavior_profiles=_profiles()).run(seed=seed)


# =====================================================================
# Diagnostic 1: existing sample distribution
# =====================================================================

def diag_1_distribution() -> str:
    ds = build_behavior_cloning_dataset(
        lambda seed: _run_peter(seed, max_tick=100),
        agent_id="peter", seeds=10,
    )
    X = ds.X
    feat_stats: list[dict[str, float]] = []
    for i, name in enumerate(FEATURE_NAMES):
        col = X[:, i]
        feat_stats.append({
            "feature": name,
            "min": float(col.min()), "max": float(col.max()),
            "mean": float(col.mean()), "std": float(col.std()),
            "unique": int(len(np.unique(col))),
        })

    # Action → state cluster
    action_state_means: dict[str, list[float]] = {}
    for a_idx, a in enumerate(ds.action_vocab):
        mask = ds.y == a_idx
        if mask.sum() > 0:
            action_state_means[a] = X[mask].mean(axis=0).tolist()

    action_counts = Counter(ds.y.tolist())

    lines = [
        "# Phase 1.1 — 기존 108 샘플 분포 진단",
        "",
        "**생성**: 2026-04-22, `scripts/data_pipeline/phase1_diagnostics.py`",
        "",
        f"- 총 샘플: {ds.n_samples}",
        f"- Action vocab: {ds.action_vocab}",
        f"- Feature dim: {ds.feature_dim}",
        "",
        "## Action 분포 (class imbalance)",
        "",
        "| action | count | % |",
        "|---|---:|---:|",
    ]
    for a_idx, a in enumerate(ds.action_vocab):
        c = action_counts.get(a_idx, 0)
        lines.append(f"| {a} | {c} | {100*c/max(1,ds.n_samples):.1f}% |")

    lines += [
        "",
        "## Feature statistics (전체 샘플)",
        "",
        "| feature | min | max | mean | std | unique |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for s in feat_stats:
        lines.append(
            f"| {s['feature']} | {s['min']:.2f} | {s['max']:.2f} | "
            f"{s['mean']:.2f} | {s['std']:.2f} | {s['unique']} |",
        )

    lines += ["", "## 해석 — 얼마나 좁은 공간인가", ""]
    # Coverage: 이론 공간 [0,10]^12 대비 관찰 공간 부피 근사 (per-feature range)
    total_range = 1.0
    for s in feat_stats:
        r = max(0.1, s["max"] - s["min"])
        total_range *= r / 10.0
    lines.append(
        f"- **Volume ratio** (per-feature range product / full [0,10]^12): "
        f"{total_range:.2e}",
    )
    lines.append("- 1.0에 가까울수록 넓은 공간 커버. 현재 값은 실측 공간이 얼마나 좁은지의 지표.")
    lines.append("")

    lines += ["## Action별 state mean (decision boundary 위치)", ""]
    lines.append("| action | " + " | ".join(
        f"{n.split('.')[-1]}" for n in FEATURE_NAMES
    ) + " |")
    lines.append("|---|" + "---|" * len(FEATURE_NAMES))
    for a, means in action_state_means.items():
        cells = " | ".join(f"{m:.2f}" for m in means)
        lines.append(f"| {a} | {cells} |")

    path = DIAG / "existing_sample_distribution.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# =====================================================================
# Diagnostic 2: initial state bounds
# =====================================================================

def _make_peter(
    fear: float = 5.0, hope: float = 5.0, grief: float = 5.0,
    confusion: float = 5.0, love: float = 5.0,
    fatigue: float = 5.0, hunger: float = 5.0, health: float = 5.0,
) -> AgentState:
    tmpl = load_agent_state(CONTENT / "peter" / "initial_state.json")
    tmpl.emotions = EmotionalState(
        fear=fear, hope=hope, grief=grief, confusion=confusion, love=love,
    )
    tmpl.physical = PhysicalState(fatigue=fatigue, hunger=hunger, health=health)
    return tmpl


def diag_2_initial_bounds() -> str:
    results: list[dict[str, Any]] = []
    # Sweep each emotion 0..10 step 2, fixed others at 5
    for var_name, setter in [
        ("fear", lambda v: _make_peter(fear=v)),
        ("hope", lambda v: _make_peter(hope=v)),
        ("grief", lambda v: _make_peter(grief=v)),
        ("confusion", lambda v: _make_peter(confusion=v)),
        ("love", lambda v: _make_peter(love=v)),
        ("fatigue", lambda v: _make_peter(fatigue=v)),
        ("hunger", lambda v: _make_peter(hunger=v)),
        ("health", lambda v: _make_peter(health=v)),
    ]:
        for val in [0.0, 2.0, 4.0, 6.0, 8.0, 10.0]:
            try:
                peter = setter(val)
                result = _run_peter(seed=0, max_tick=30, peter_override=peter)
                peter_actions = result.action_histories.get("peter", [])
                final = peter_actions[-1].chosen_action if peter_actions else "idle"
                results.append({
                    "var": var_name, "val": val,
                    "crashed": False, "n_actions": len(peter_actions),
                    "final_action": final,
                })
            except Exception as e:
                results.append({
                    "var": var_name, "val": val,
                    "crashed": True, "error": str(e)[:80],
                })

    # Extreme combo test
    combos = [
        {"fear": 10, "hope": 10},
        {"fear": 10, "grief": 10, "confusion": 10},
        {"fatigue": 10, "hunger": 10, "health": 0},
        {"fear": 0, "hope": 0, "love": 0, "grief": 0, "confusion": 0},
    ]
    combo_results = []
    for c in combos:
        try:
            peter = _make_peter(**c)
            result = _run_peter(seed=0, max_tick=30, peter_override=peter)
            peter_actions = result.action_histories.get("peter", [])
            combo_results.append({
                "combo": c, "crashed": False, "n_actions": len(peter_actions),
            })
        except Exception as e:
            combo_results.append({"combo": c, "crashed": True, "error": str(e)[:80]})

    lines = [
        "# Phase 1.2 — Initial state bounds 진단",
        "",
        "각 feature를 0, 2, 4, 6, 8, 10 으로 sweep, 다른 값 고정 (5.0).",
        "30 tick 시뮬레이션 후 crash / 행동 수 기록.",
        "",
        "## Single-variable sweep",
        "",
        "| var | val | crashed | n_actions | final_action |",
        "|---|---:|---|---:|---|",
    ]
    for r in results:
        if r.get("crashed"):
            lines.append(f"| {r['var']} | {r['val']} | YES | — | `{r.get('error','?')}` |")
        else:
            lines.append(
                f"| {r['var']} | {r['val']} | no | {r['n_actions']} | {r['final_action']} |",
            )

    crashes = sum(1 for r in results if r.get("crashed"))
    lines += [
        "",
        f"- **Crash 횟수 (single sweep)**: {crashes} / {len(results)}",
        "",
        "## Extreme combo",
        "",
        "| combo | crashed | n_actions |",
        "|---|---|---:|",
    ]
    for r in combo_results:
        if r["crashed"]:
            lines.append(f"| {r['combo']} | YES | {r.get('error','?')} |")
        else:
            lines.append(f"| {r['combo']} | no | {r['n_actions']} |")

    lines += [
        "",
        "## 결론",
        "",
        (
            "- Engine이 0–10 범위의 어떤 단일 변수 설정에서도 crash하지 않으면 "
            "Phase 2C rare-action sweep은 **±0–10 전체 범위 허용**."
        ),
        (
            "- Extreme combo에서도 정상이면 Phase 2D stress injection (fear=9.5) 안전."
        ),
    ]
    path = DIAG / "initial_state_bounds.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# =====================================================================
# Diagnostic 3: tick extension
# =====================================================================

def diag_3_tick_extension() -> str:
    results = []
    for max_tick in [50, 100, 200, 500]:
        try:
            result = _run_peter(seed=0, max_tick=max_tick)
            actions = result.action_histories.get("peter", [])
            snaps = result.state_snapshots.get("peter", {})
            final_tick = max(snaps.keys()) if snaps else 0
            final = snaps[final_tick] if snaps else None
            final_feat = state_to_feature_vector(final) if final else []
            results.append({
                "max_tick": max_tick, "crashed": False,
                "n_actions": len(actions), "final_tick": final_tick,
                "final_feat": final_feat,
            })
        except Exception as e:
            results.append({"max_tick": max_tick, "crashed": True, "error": str(e)[:80]})

    lines = [
        "# Phase 1.3 — Tick extension 진단",
        "",
        "seed=0, canonical_events + behavior_profile 정상 load.",
        "",
        "| max_tick | crashed | n_actions | final_tick | final fear | final hope | final fatigue |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        if r["crashed"]:
            lines.append(f"| {r['max_tick']} | YES | — | — | — | — | — |")
        else:
            f = r["final_feat"] or [0]*12
            lines.append(
                f"| {r['max_tick']} | no | {r['n_actions']} | {r['final_tick']} | "
                f"{f[0]:.2f} | {f[1]:.2f} | {f[5]:.2f} |",
            )

    # Attractor check: last state's feat vs mid-state
    if results and not results[-1].get("crashed"):
        lines += [
            "",
            "## 긴 궤적 attractor 관찰",
            "",
            (
                f"- 500 tick까지 완주: {not results[-1].get('crashed')}"
            ),
            (
                f"- 500 tick 마지막 state fear/hope: "
                f"{results[-1]['final_feat'][0]:.2f} / "
                f"{results[-1]['final_feat'][1]:.2f}"
            ),
            "- saturation vs oscillation 구분은 snapshot 궤적 추가 분석 필요.",
        ]
    path = DIAG / "tick_extension_test.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# =====================================================================
# Diagnostic 4: environment responsiveness
# =====================================================================

def diag_4_environment() -> str:
    # EnvironmentState를 바꾼 run vs 기본 run 비교
    lines = [
        "# Phase 1.4 — Environment responsiveness 진단",
        "",
        "SimulationConfig 자체는 environment 필드 미노출. "
        "엔진 내부에서 EnvironmentState를 쓰는 지점과 Peter의 반응 여부 확인.",
        "",
    ]

    # 현재 SimulationWorld가 environment를 어떻게 취급하는지 static grep
    world_path = ROOT / "engine" / "simulation" / "world.py"
    content = world_path.read_text(encoding="utf-8")
    env_mentions = content.count("environment")
    env_params = [
        line.strip() for line in content.split("\n")
        if "environment" in line and ("def " in line or "self." in line)
    ][:15]

    lines += [
        f"- engine/simulation/world.py에서 'environment' 등장 횟수: **{env_mentions}**",
        "- 주요 등장 위치:",
    ]
    for p in env_params:
        lines.append(f"  - `{p}`")

    # behavior_profile의 weight_formula에서 environment 참조 여부
    peter_profile = load_behavior_profile(CONTENT / "peter" / "behavior_profile.json")
    env_refs = 0
    for action in peter_profile.actions:
        wf = action.weight_formula
        for mult in wf.state_multipliers:
            if getattr(mult, "field_path", "").startswith("env."):
                env_refs += 1
    lines += [
        "",
        f"- **Peter behavior_profile의 state_multipliers 중 `env.` 경로 참조: {env_refs}**",
        "",
    ]

    # Direct test: run with no environment override vs environment override (if supported)
    base_result = _run_peter(seed=0, max_tick=30)
    base_actions = [r.chosen_action for r in base_result.action_histories.get("peter", [])]
    lines += [
        "## 실측 비교 (seed=0, 30 tick)",
        "",
        f"- Base run peter actions ({len(base_actions)}): `{base_actions[:10]}{'...' if len(base_actions)>10 else ''}`",
        "",
    ]

    # 결론
    lines += [
        "## 결론",
        "",
    ]
    if env_refs == 0:
        lines += [
            "- **Peter behavior_profile은 environment를 직접 참조하지 않음.** "
            "즉 Phase 2E environment 다양화는 **현 구조에서 Peter 행동에 영향을 주지 못함.**",
            "- Phase 2E는 Option B (건너뜀) 권고.",
        ]
    else:
        lines += [
            "- Peter behavior_profile이 environment를 참조. Phase 2E environment "
            "다양화 유의미 가능.",
        ]
    path = DIAG / "environment_responsiveness.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# =====================================================================
# Diagnostic 5: forced action feasibility
# =====================================================================

def diag_5_forced_action() -> str:
    lines = [
        "# Phase 1.5 — Forced action feasibility 진단",
        "",
        "현재 구조에서 '이 tick에 이 action을 강제 실행' 가능한지 확인.",
        "",
    ]

    peter_profile = load_behavior_profile(CONTENT / "peter" / "behavior_profile.json")
    actions = list(peter_profile.actions)
    lines += [f"- Peter action 수: {len(actions)}", "- action_ids:"]
    for a in actions:
        lines.append(f"  - `{a.action_id}`")

    # Approach: use DecisionPolicy that forces a specific action via weight mask
    #   (we demonstrate the mechanism without running a full sim)
    class _ForcedPolicy:
        def __init__(self, action_id: str):
            self.action_id = action_id
        def weights(self, state, options, environment=None):
            return [100.0 if o.action_id == self.action_id else 0.0 for o in options]

    # Verify the policy mechanism works with decide_action
    from engine.core.event import ActionOption, WeightFormula
    opts = [
        ActionOption(
            action_id=a.action_id,
            weight_formula=WeightFormula(base_weight=1.0, state_multipliers=[]),
        )
        for a in actions[:3]
    ]
    rng = random.Random(0)
    dummy_state = AgentState(agent_id="peter")
    forced = _ForcedPolicy(actions[1].action_id)
    picks = [
        decide_action(dummy_state, opts, rng, policy=forced).action_id
        for _ in range(20)
    ]
    forced_ratio = sum(1 for p in picks if p == actions[1].action_id) / 20

    lines += [
        "",
        "## 메커니즘 테스트 (20회 decide_action with weight-mask policy)",
        "",
        f"- Target action: `{actions[1].action_id}`",
        f"- Forced ratio: **{forced_ratio:.0%}** (100%면 완전 강제 가능)",
        "",
        "## 결론",
        "",
    ]
    if forced_ratio == 1.0:
        lines += [
            "- **Forced action은 DecisionPolicy weight-mask로 100% 달성 가능.** "
            "별도 engine 수정 불필요. ChatGPT의 'forced action rollouts' 전략 적용 가능.",
            "- Phase 2에서 `{action_id: 100.0, others: 0.0}` 형태의 `ForcingPolicy`를 "
            "주입한 뒤 N tick rollout → rare action 주변 state 분포 수집 가능.",
        ]
    else:
        lines += [
            "- Forced action이 완벽하지 않음. select_action / decide_action의 "
            "sampling 경로 재조사 필요.",
        ]
    path = DIAG / "forced_action_feasibility.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


# =====================================================================
# Diagnostic 6: counterfactual branching
# =====================================================================

def diag_6_branching() -> str:
    # Deep copy state and replay with different rng seeds → collect divergence
    result = _run_peter(seed=0, max_tick=50)
    snapshots = result.state_snapshots.get("peter", {})
    if not snapshots:
        raise RuntimeError("no snapshots for peter")
    ticks = sorted(snapshots.keys())
    mid_tick = ticks[len(ticks) // 2]
    base_state = snapshots[mid_tick]

    # Deep-copy check
    cloned = copy.deepcopy(base_state)
    assert cloned is not base_state
    assert cloned.emotions.fear == base_state.emotions.fear

    # Perturb and resume: because SimulationWorld doesn't accept 'start from state',
    # we simulate branching by running from initial with different seeds and
    # documenting divergence. True mid-run branching would require a new entry point.
    seeds = [0, 1, 2, 3, 4]
    finals: list[tuple[int, str]] = []
    for s in seeds:
        r = _run_peter(seed=s, max_tick=50)
        acts = r.action_histories.get("peter", [])
        finals.append((s, acts[-1].chosen_action if acts else "idle"))

    action_set = {a for _, a in finals}

    lines = [
        "# Phase 1.6 — Counterfactual branching 진단",
        "",
        "## Deep-copy 안전성",
        "",
        f"- `copy.deepcopy(AgentState)` 동작: OK (cloned.emotions.fear={cloned.emotions.fear})",
        f"- 원본과 clone이 서로 다른 객체: {cloned is not base_state}",
        "",
        "## Branch divergence (현재 가능한 방식 — 다른 seed로 재실행)",
        "",
        "| seed | 마지막 action |",
        "|---:|---|",
    ]
    for s, a in finals:
        lines.append(f"| {s} | {a} |")
    lines += [
        "",
        f"- 5 seed에서 관찰된 distinct final actions: **{len(action_set)}** (`{action_set}`)",
        "",
        "## Mid-run branching 가능성",
        "",
        "- 현재 `SimulationWorld.run(seed)` 는 처음부터 재시작만 지원.",
        "- **Mid-run branching** (tick k의 state에서 여러 branch) 은 SimulationWorld에 "
        "`resume(from_state, from_tick, seed)` API 신설 필요.",
        "- 이는 engine/ 수정이므로 Lee 확인 대상 (Rule #6).",
        "",
        "## 결론",
        "",
        "- Deep-copy 자체는 안전. State 격리 가능.",
        "- Seed 재실행을 통한 초기 branching은 가능하지만 *mid-trajectory*가 아닌 *initial-state* "
        "branching. Phase 2B 구현 시 처음부터 perturbed state로 새 run을 시작하는 방식으로 근사 가능.",
        "- 엔진에 `resume_from_state` API를 추가하지 않는 한 "
        "\"동일 궤적의 tick k부터 분기\" 는 불가능.",
    ]
    path = DIAG / "counterfactual_branching.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def main() -> int:
    _register()
    DIAG.mkdir(parents=True, exist_ok=True)

    out: list[str] = []
    for name, fn in [
        ("1 sample distribution", diag_1_distribution),
        ("2 initial bounds",      diag_2_initial_bounds),
        ("3 tick extension",      diag_3_tick_extension),
        ("4 environment",         diag_4_environment),
        ("5 forced action",       diag_5_forced_action),
        ("6 counterfactual",      diag_6_branching),
    ]:
        print(f"[running] {name}")
        path = fn()
        print(f"  saved: {path}")
        out.append(path)

    # Index summary
    idx = DIAG / "INDEX.md"
    idx.write_text(
        "\n".join([
            "# Phase 1 진단 보고서 인덱스",
            "",
            "| # | 항목 | 파일 |",
            "|---|---|---|",
            *[f"| {i+1} | {Path(p).stem.replace('_', ' ')} | [{Path(p).name}]({Path(p).name}) |"
              for i, p in enumerate(out)],
        ]),
        encoding="utf-8",
    )
    print(f"\nindex: {idx}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
