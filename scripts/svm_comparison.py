"""LDA vs RBF-kernel SVM comparison (PROJECT_DIRECTION_v2.md §6 — task 3).

Entry:
    python scripts/svm_comparison.py

Decides next Stage 2 step:
- SVM > LDA (>=5%p) → 비선형 구조 존재 → PyTorch MLP 도입 정당화
- SVM ≈ LDA → linear 한계 → MLP 도입 보류, Future Work로 기록

Scenarios: Peter (multi-agent passion), Van Gogh (Arles period)
Output: docs/person/paper_data/svm_comparison.json + svm_comparison.txt

기존 코드 수정 금지. sklearn만 사용.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from content.caiaphas.domain_politics import PoliticalCalculationState
from content.crowd.domain_crowd import CrowdDynamicsState
from content.gauguin.domain_artistic_ego import ArtisticEgoState
from content.judas.domain_betrayal import BetrayalPsychologyState
from content.peter.domain_faith import FaithJourneyState
from content.theo.domain_patron import PatronState
from content.vangogh.domain_creative import CreativeDriveState
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
from engine.rules.temporal import HomeostasisRule
from engine.simulation.drive_training import (
    collect_trajectories,
    trajectories_to_samples,
)
from engine.simulation.training_samples import state_to_feature_vector
from engine.simulation.world import SimulationWorld

CONTENT = ROOT / "content"
OUT_DIR = ROOT / "docs" / "person" / "paper_data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

for _name, _cls in [
    ("faith_journey", FaithJourneyState),
    ("betrayal_psychology", BetrayalPsychologyState),
    ("political_calculation", PoliticalCalculationState),
    ("crowd_dynamics", CrowdDynamicsState),
    ("creative_drive", CreativeDriveState),
    ("artistic_ego", ArtisticEgoState),
    ("patron", PatronState),
]:
    register_domain_type(_name, _cls)


def _emotion_rules() -> RuleEngine:
    return RuleEngine([
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(), HomeostasisRule(),
    ])


def _peter_runner(seed: int, max_tick: int = 300):
    peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
    crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
    events = load_events(CONTENT / "peter" / "canonical_events.json")
    triggers = load_triggers(CONTENT / "shared" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
    profiles = {
        n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
        for n in ["peter", "judas", "caiaphas", "crowd"]
    }
    config = SimulationConfig(
        initial_state=peter,
        initial_states=[peter, judas, cai, crowd],
        max_tick=max_tick, state_noise_scale=0.02,
        events=events, triggers=triggers, hazard_events=hazards,
    )
    return SimulationWorld(
        config, _emotion_rules(), behavior_profiles=profiles,
    ).run(seed=seed)


def _vg_runner(seed: int, max_tick: int = 150):
    vg = load_agent_state(CONTENT / "vangogh" / "initial_state.json")
    gauguin = load_agent_state(CONTENT / "gauguin" / "initial_state.json")
    theo = load_agent_state(CONTENT / "theo" / "initial_state.json")
    triggers = load_triggers(CONTENT / "vangogh" / "triggers.json")
    hazards = load_hazard_events(CONTENT / "vangogh" / "hazard_events.json")
    profiles = {
        n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
        for n in ["vangogh", "gauguin", "theo"]
    }
    config = SimulationConfig(
        max_tick=max_tick, initial_state=vg,
        initial_states=[vg, gauguin, theo],
        triggers=triggers, hazard_events=hazards,
        state_noise_scale=0.05,
    )
    return SimulationWorld(
        config, _emotion_rules(), behavior_profiles=profiles,
    ).run(seed=seed)


def _compare(scenario: str, run_fn, n_seeds: int = 10) -> dict[str, Any]:
    print(f"[svm_compare] {scenario} ({n_seeds} seeds) ...")
    t0 = time.time()
    results = collect_trajectories(run_fn, n_runs=n_seeds)
    samples = [s for s in trajectories_to_samples(results) if s.action is not None]

    cnt = Counter(s.action for s in samples)
    keep = {a for a, n in cnt.items() if n >= 3}
    samples = [s for s in samples if s.action in keep]

    X = np.array([state_to_feature_vector(s.state) for s in samples])
    y = np.array([s.action for s in samples])
    majority = max(set(y), key=list(y).count)
    majority_acc = float(np.mean(y == majority))

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.3, random_state=0, stratify=y,
    )

    # Standardize for both LDA and SVM fairness
    scaler = StandardScaler()
    Xtr_s = scaler.fit_transform(Xtr)
    Xte_s = scaler.transform(Xte)

    # LDA
    lda = LinearDiscriminantAnalysis()
    lda.fit(Xtr_s, ytr)
    lda_train = float(lda.score(Xtr_s, ytr))
    lda_test = float(lda.score(Xte_s, yte))

    # RBF SVM (defaults: C=1.0, gamma='scale')
    svm = SVC(kernel="rbf", C=1.0, gamma="scale", random_state=0)
    svm.fit(Xtr_s, ytr)
    svm_train = float(svm.score(Xtr_s, ytr))
    svm_test = float(svm.score(Xte_s, yte))

    # Decision
    gap = svm_test - lda_test
    if gap >= 0.05:
        verdict = "nonlinear_structure_present_mlp_justified"
    elif gap >= 0.02:
        verdict = "modest_nonlinear_gain_mlp_may_help"
    else:
        verdict = "linear_limit_mlp_unlikely_to_help"

    dt = time.time() - t0
    return {
        "scenario": scenario,
        "n_seeds": n_seeds,
        "n_samples": len(samples),
        "n_action_classes": len(keep),
        "majority_baseline": majority_acc,
        "lda_train_acc": lda_train,
        "lda_test_acc": lda_test,
        "svm_rbf_train_acc": svm_train,
        "svm_rbf_test_acc": svm_test,
        "svm_minus_lda": round(gap, 4),
        "verdict": verdict,
        "runtime_seconds": round(dt, 2),
    }


def main() -> None:
    out: dict[str, Any] = {
        "schema_version": 1,
        "notes": (
            "LDA vs RBF-kernel SVM on held-out 30% split. "
            "Features = 12-dim state_to_feature_vector (emotions + physical + slow_state). "
            "SVM > LDA + 0.05 판단 시 비선형 구조 존재 → PyTorch MLP 도입 정당화. "
            "PROJECT_DIRECTION_v2.md §3.3 분기 기준."
        ),
    }

    out["peter"] = _compare("peter", _peter_runner)
    out["vangogh"] = _compare("vangogh", _vg_runner)

    # summary
    total_gap = out["peter"]["svm_minus_lda"] + out["vangogh"]["svm_minus_lda"]
    out["summary"] = {
        "peter_verdict": out["peter"]["verdict"],
        "vangogh_verdict": out["vangogh"]["verdict"],
        "average_gap": round(total_gap / 2, 4),
        "recommendation": (
            "proceed_with_pytorch_mlp"
            if total_gap / 2 >= 0.05
            else "modest_if_any_gain_mlp_optional"
            if total_gap / 2 >= 0.02
            else "defer_mlp_log_as_future_work"
        ),
    }

    dest = OUT_DIR / "svm_comparison.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # plain text summary
    txt = [
        "LDA vs RBF SVM - feasibility of nonlinear Stage 2",
        "=" * 55,
        "",
        f"{'scenario':<12} {'majority':>10} {'LDA test':>10} {'SVM test':>10} {'gap':>8} verdict",
        "-" * 90,
    ]
    for key in ["peter", "vangogh"]:
        r = out[key]
        txt.append(
            f"{r['scenario']:<12} "
            f"{r['majority_baseline']:>10.3f} "
            f"{r['lda_test_acc']:>10.3f} "
            f"{r['svm_rbf_test_acc']:>10.3f} "
            f"{r['svm_minus_lda']:>+8.3f} "
            f"{r['verdict']}"
        )
    txt.append("")
    txt.append(f"Average SVM - LDA gap: {out['summary']['average_gap']:+.3f}")
    txt.append(f"Recommendation: {out['summary']['recommendation']}")

    (OUT_DIR / "svm_comparison.txt").write_text(
        "\n".join(txt) + "\n", encoding="utf-8",
    )
    # Windows cp949 호환 출력: ASCII only로 제한
    for line in txt:
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("ascii", errors="replace").decode("ascii"))
    print(f"\n[done] wrote {dest}")


if __name__ == "__main__":
    main()
