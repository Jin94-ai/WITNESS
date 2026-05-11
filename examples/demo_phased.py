"""Witness v1.2 데모 — phase-linked continuous life architecture.

베드로 공생애 4개 phase를 순차 실행하고 time_axis로 absolute-hours
좌표계 trajectory를 출력한다. Phase 5(수난)는 기존 demo_v07.py로 분리.

포함 기능 (v1.2 Iter 20-27):
1. PhasedSimulationWorld — phase 별 tick_scale_hours + canonical_events_path
2. PhaseHandoffSpec — slow_state carry-all + explicit field mapping
3. time_axis — absolute hours 좌표계
4. SlowStateFieldRecoveryRule (opt-in, 기본 zero-effect)
5. Phase-variable dt propagation to hazard + inhibitor

Usage:
    python demo_phased.py                   # 기본 (seed=0)
    python demo_phased.py --seed 42
    python demo_phased.py --with-recovery   # slow state 회복 rule 활성화
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _wrap_stdout_utf8() -> None:
    """Wrap stdout/stderr in UTF-8 TextIOWrapper. Call from main() only —
    doing this at import time breaks pytest capture and any other consumer
    that imports this module's helpers."""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace",
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace",
        )

from content.caiaphas.domain_politics import PoliticalCalculationState  # noqa: E402
from content.crowd.domain_crowd import CrowdDynamicsState  # noqa: E402
from content.judas.domain_betrayal import BetrayalPsychologyState  # noqa: E402
from content.peter.domain_faith import FaithJourneyState  # noqa: E402
from engine.core.phase import (  # noqa: E402
    FieldMapping,
    Phase,
    PhaseExitCondition,
    PhaseHandoffSpec,
)
from engine.core.world import SimulationConfig  # noqa: E402
from engine.io.loader import load_agent_state, register_domain_type  # noqa: E402
from engine.rules.base import RuleEngine  # noqa: E402
from engine.rules.emotional import (  # noqa: E402
    ConfusionRule,
    FearResponseRule,
    GriefRule,
    HopeRule,
    LoveRule,
)
from engine.rules.slow_recovery import SlowStateFieldRecoveryRule  # noqa: E402
from engine.rules.temporal import HomeostasisRule  # noqa: E402
from engine.simulation.phased_world import PhasedSimulationWorld  # noqa: E402
from engine.simulation.time_axis import hours_to_days  # noqa: E402

CONTENT = ROOT / "content"


def _rules(with_recovery: bool = False) -> RuleEngine:
    rules = [
        FearResponseRule(), HopeRule(), GriefRule(),
        ConfusionRule(), LoveRule(),
        HomeostasisRule(),
    ]
    if with_recovery:
        rules.append(SlowStateFieldRecoveryRule(
            moral_injury_rate_per_hour=0.002,
            trust_scar_rate_per_hour=0.001,
            identity_shift_recovery_rate_per_hour=0.0005,
        ))
    return RuleEngine(rules)


def _handoff() -> PhaseHandoffSpec:
    carried = [
        "domain_state.obedience_maturity",
        "domain_state.jesus_understanding",
        "emotions.awe", "emotions.hope", "emotions.fear",
        "emotions.grief", "emotions.confusion", "emotions.love",
    ]
    return PhaseHandoffSpec(
        mappings=[FieldMapping("peter", f, "peter", f) for f in carried],
    )


def _build_config(with_passion: bool = False) -> SimulationConfig:
    peter = load_agent_state(CONTENT / "peter" / "initial_state_calling.json")
    judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
    initial_states = [peter, judas]

    phases = [
        Phase(
            phase_id="01_calling",
            agents_active=["peter"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=84),
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "01_calling" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="02_galilean",
            agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=60),  # MVP 단축
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "02_galilean" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="03_confession",
            agents_active=["peter", "judas"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=50),  # MVP 단축
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "03_confession" / "canonical_events.json",
            ),
            handoff_to_next=_handoff(),
        ),
        Phase(
            phase_id="04_journey",
            agents_active=["peter", "judas"],
            tick_scale_hours=24.0,
            exit_condition=PhaseExitCondition(max_tick=30),  # MVP 단축
            canonical_events_path=str(
                CONTENT / "peter" / "phases" / "04_journey_to_jerusalem" / "canonical_events.json",
            ),
            handoff_to_next=_handoff() if with_passion else None,
        ),
    ]
    if with_passion:
        caiaphas = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
        crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
        initial_states.extend([caiaphas, crowd])
        phases.append(Phase(
            phase_id="05_passion",
            agents_active=["peter", "judas", "caiaphas", "crowd"],
            tick_scale_hours=2.0,
            exit_condition=PhaseExitCondition(max_tick=500),
            canonical_events_path=str(
                CONTENT / "peter" / "canonical_events.json",
            ),
        ))
    return SimulationConfig(
        initial_state=peter,
        initial_states=initial_states,
        max_tick=5000,
        state_noise_scale=0.02,
        phases=phases,
    )


def _print_header(title: str) -> None:
    print()
    print("=" * 68)
    print(f" {title}")
    print("=" * 68)


def _print_phase_boundaries(result) -> None:
    _print_header("Phase Boundaries (absolute time)")
    enriched = result.phase_hours_table()
    print(f"{'Phase':<18} {'Ticks':<16} {'Hours':<16} {'Days':>8}")
    print("-" * 68)
    for b in enriched:
        tick_range = f"{b['start_tick']}-{b['end_tick']}"
        hour_range = f"{b['start_hours']:.1f}-{b['end_hours']:.1f}"
        days = hours_to_days(b["duration_hours"])
        print(f"{b['phase_id']:<18} {tick_range:<16} {hour_range:<16} {days:>8.2f}")
    total = enriched[-1]["end_hours"]
    print("-" * 68)
    print(f"Total: {total:.1f}h ≈ {hours_to_days(total):.1f} days")


def _print_peter_trajectory(result, field_path: str, label: str) -> None:
    _print_header(f"Peter trajectory — {label} ({field_path})")
    traj = result.extract_absolute_trajectory("peter", field_path)
    if not traj:
        print("(no data)")
        return
    # sample 한 phase당 최대 5개
    by_phase: dict[str, list] = {}
    for p in traj:
        by_phase.setdefault(p.phase_id, []).append(p)
    for phase_id, points in by_phase.items():
        step = max(1, len(points) // 4)
        sample = points[::step] + [points[-1]]
        deduped = {p.hours: p for p in sample}
        print(f"  [{phase_id}]")
        for p in sorted(deduped.values(), key=lambda x: x.hours):
            print(f"    t={p.hours:>7.1f}h (tick={p.local_tick:>3})  {label}={p.value:.2f}")


def _fit_lda_on_peter_pilot(dim: int):
    """Iter 74: --encoder learned 사용 시 LDA를 위한 pilot 학습 샘플 준비.

    Peter 수난 3-seed를 가볍게 실행해서 trajectory 추출 → LDA fit → 반환.
    Stage 2 real training loop는 아니지만 "learned encoder가 어떻게 다른가"
    를 사용자가 즉시 볼 수 있게 함.
    """
    from content.caiaphas.domain_politics import PoliticalCalculationState
    from content.crowd.domain_crowd import CrowdDynamicsState
    from engine.core.latent_drive import LearnedLinearEncoder
    from engine.io.loader import load_behavior_profile, load_hazard_events, load_triggers
    from engine.simulation.drive_training import (
        collect_trajectories,
        trajectories_to_samples,
    )
    from engine.simulation.world import SimulationWorld

    # peter/judas는 이미 register됨. caiaphas/crowd 추가.
    register_domain_type("political_calculation", PoliticalCalculationState)
    register_domain_type("crowd_dynamics", CrowdDynamicsState)

    def _pilot_run(seed: int):
        peter = load_agent_state(CONTENT / "peter" / "initial_state.json")
        judas = load_agent_state(CONTENT / "judas" / "initial_state.json")
        cai = load_agent_state(CONTENT / "caiaphas" / "initial_state.json")
        crowd = load_agent_state(CONTENT / "crowd" / "initial_state.json")
        from engine.io.loader import load_events
        events = load_events(CONTENT / "peter" / "canonical_events.json")
        triggers = load_triggers(CONTENT / "shared" / "triggers.json")
        hazards = load_hazard_events(CONTENT / "peter" / "hazard_events.json")
        profiles = {
            n: load_behavior_profile(CONTENT / n / "behavior_profile.json")
            for n in ["peter", "judas", "caiaphas", "crowd"]
        }
        config = SimulationConfig(
            initial_state=peter, initial_states=[peter, judas, cai, crowd],
            max_tick=150, state_noise_scale=0.02,
            events=events, triggers=triggers, hazard_events=hazards,
        )
        return SimulationWorld(
            config, _rules(False), behavior_profiles=profiles,
        ).run(seed=seed)

    print("  [fitting LDA on Peter passion pilot (3 seeds × 150 tick)...]")
    results = collect_trajectories(_pilot_run, n_runs=3)
    samples = [s for s in trajectories_to_samples(results) if s.action is not None]
    lda = LearnedLinearEncoder(dim=dim)
    lda.fit(samples)
    return lda


def _print_drive_trajectory(result, drive_dim: int) -> None:
    """Peter의 latent drive vector 궤적 — phase 별 첫/마지막 tick 샘플링."""
    _print_header(f"Peter latent drive (dim={drive_dim}) — Stage 2 bridge")
    for phase_id, phase_result in result.per_phase_results.items():
        snaps = phase_result.state_snapshots.get("peter", {})
        if not snaps:
            continue
        sorted_ticks = sorted(snaps.keys())
        # phase 당 최대 3개 sample (시작 / 중간 / 끝)
        picks = [sorted_ticks[0], sorted_ticks[len(sorted_ticks) // 2], sorted_ticks[-1]]
        print(f"  [{phase_id}]")
        for t in picks:
            s = snaps[t]
            if s.drive_state is None:
                print(f"    tick={t:>3}  drive=<none>")
                continue
            vals = ", ".join(f"{v:+.2f}" for v in s.drive_state.values)
            print(f"    tick={t:>3}  drive=[{vals}]")


def _print_final_summary(result) -> None:
    _print_header("Final Agent States")
    for aid, st in result.final_states.items():
        print(f"  [{aid}]")
        print(f"    fear={st.emotions.fear:.2f}  hope={st.emotions.hope:.2f}  "
              f"awe={st.emotions.awe:.2f}")
        print(f"    slow: moral_injury={st.slow_state.moral_injury:.2f}  "
              f"event_trauma={st.slow_state.event_trauma:.2f}")
        if hasattr(st.domain_state, "obedience_maturity"):
            print(f"    obedience_maturity={st.domain_state.obedience_maturity:.2f}")
        if hasattr(st.domain_state, "jesus_understanding"):
            print(f"    jesus_understanding={st.domain_state.jesus_understanding}")
        if hasattr(st.domain_state, "disillusionment"):
            print(f"    disillusionment={st.domain_state.disillusionment:.2f}")


def main() -> None:
    _wrap_stdout_utf8()
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--with-recovery", action="store_true",
                        help="Activate SlowStateFieldRecoveryRule (opt-in).")
    parser.add_argument("--full-passion", action="store_true",
                        help="Append Phase 5 (full 500-tick passion) + Caiaphas/Crowd agents.")
    parser.add_argument("--show-drive", action="store_true",
                        help="Inject drive encoder + print latent drive trajectory (v1.0 Stage 2 bridge).")
    parser.add_argument("--drive-dim", type=int, default=5,
                        help="Latent drive dimensionality (3~8, default 5).")
    parser.add_argument("--encoder", choices=["identity", "fixed", "learned"],
                        default="fixed",
                        help=(
                            "Drive encoder (with --show-drive): "
                            "identity (pass-through of 5 fields), "
                            "fixed (seeded random projection, default), "
                            "learned (sklearn LDA on pilot Peter passion run)."
                        ))
    args = parser.parse_args()

    register_domain_type("faith_journey", FaithJourneyState)
    register_domain_type("betrayal_psychology", BetrayalPsychologyState)
    if args.full_passion:
        register_domain_type("political_calculation", PoliticalCalculationState)
        register_domain_type("crowd_dynamics", CrowdDynamicsState)

    drive_model = None
    drive_label = "off"
    if args.show_drive:
        from engine.core.latent_drive import (
            FixedProjectionEncoder,
            IdentityEncoder,
            LatentDriveModel,
        )
        if args.encoder == "identity":
            enc = IdentityEncoder(dim=args.drive_dim)
            drive_label = f"Identity dim={args.drive_dim}"
        elif args.encoder == "learned":
            # pilot learning: Peter 수난 3-seed로 LDA fit.
            enc = _fit_lda_on_peter_pilot(dim=args.drive_dim)
            drive_label = f"LearnedLinear (LDA) dim={args.drive_dim}"
        else:  # fixed
            enc = FixedProjectionEncoder(dim=args.drive_dim, seed=args.seed)
            drive_label = f"FixedProjection dim={args.drive_dim}"
        drive_model = LatentDriveModel(encoder=enc, dim=args.drive_dim)

    config = _build_config(with_passion=args.full_passion)
    world = PhasedSimulationWorld(
        config, _rules(args.with_recovery), drive_model=drive_model,
    )
    result = world.run(seed=args.seed)

    _print_header(f"Witness v1.2 demo — Peter 공생애 (seed={args.seed})")
    print(f"  Phases: {len(result.phase_boundaries)}")
    print(f"  Recovery rule active: {args.with_recovery}")
    print(f"  Drive model: {drive_label}")

    _print_phase_boundaries(result)
    _print_peter_trajectory(result, "emotions.awe", "awe")
    _print_peter_trajectory(
        result, "domain_state.obedience_maturity", "obedience",
    )
    if args.show_drive:
        _print_drive_trajectory(result, args.drive_dim)
    _print_final_summary(result)
    print()


if __name__ == "__main__":
    main()
