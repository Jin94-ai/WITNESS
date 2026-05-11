"""CrowdState + phase transition (CROWD_DYNAMICS.md implementation).

Crowd는 "개인의 합"이 아니라 independent meso-layer. 매 tick decay/drift
자동 + agent action 에 의한 update.

Phase transitions:
    idle → gathered → aligned → lynch_mode
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

CrowdPhase = Literal["idle", "gathered", "aligned", "lynch_mode"]
CROWD_PHASES: tuple[CrowdPhase, ...] = ("idle", "gathered", "aligned", "lynch_mode")


@dataclass
class CrowdState:
    """Meso-layer state for a single crowd instance.

    One world may have multiple CrowdState instances (e.g. courtyard crowd +
    street crowd). Each tracks its own density/alignment/blame.
    """
    crowd_id: str = "default"

    # Density
    density: float = 0.0                     # 0-1

    # Alignment
    dominant_emotion: str = "indifferent"     # anger|fear|awe|mourning|celebration|indifferent
    alignment_strength: float = 0.0           # 0-1
    fragmentation: float = 0.0                # 0-1

    # Dynamics
    volatility: float = 0.0                   # 0-1
    contagion_susceptibility: float = 0.5     # 0-1

    # Focus
    focus_target: str | None = None           # role_id or agent_id
    blame_concentration: dict[str, float] = field(default_factory=dict)
    # {target_role_or_agent: [0,1]}

    # Information
    rumor_intensity: float = 0.0              # 0-1
    false_belief_ratio: float = 0.0           # 0-1

    # Accusation
    accusation_amplification: float = 0.0     # 0-1

    # World memory fields (Iter 4 — persistence of post-event climate)
    shame_climate: float = 0.0                # 0-1, ACTIVE memory: → shame_exposure pressure
    # Iter 90 (WORLD_MESO_SCALE.md §1.5): public_suspicion is general
    # crowd suspicion NOT tied to a specific target. Distinct from
    # blame_concentration (which is per-target). Couples to
    # social_threat pressure for all agents at location.
    public_suspicion: float = 0.0             # 0-1, ACTIVE meso-scale memory
    # authority_vigilance status (Iter 89 freeze audit + WORLD_MEMORY.md):
    # ACCUMULATES from guard_approaches events (intensity * 0.5).
    # NEVER DECAYS (Iter 43 removed memory field decay; constant defined
    # below but unused).
    # NO DOWNSTREAM COUPLING (Iter 38 ablated pressure connection; world.py:446
    # comment confirms). Logged in trajectory + narrator only.
    # Cycle-mechanism INERT. RESERVE for future re-wiring or v1.0 latent drive.
    # See docs/b_direction/WORLD_MEMORY.md §1.2 + §5.
    authority_vigilance: float = 0.0          # 0-1, DEAD memory (logged-only)

    # ----- Decay constants (per tick) -----
    # Tuned iter 3 so accumulation can exceed decay during active events.
    density_decay: float = 0.015              # slower (was 0.02)
    alignment_decay: float = 0.05             # HL ≈ 14 (was 0.07)
    volatility_decay: float = 0.09
    blame_decay: float = 0.04                 # slower (was 0.05)
    rumor_intensity_decay: float = 0.08
    # Memory fields have slow decay — that's the point of "climate".
    shame_climate_decay: float = 0.015        # HL ≈ 45 ticks
    authority_vigilance_decay: float = 0.02   # HL ≈ 35 ticks (UNUSED post-Iter-43)
    # Iter 90: public_suspicion decay (active, applied in step_crowd).
    public_suspicion_decay: float = 0.02      # HL ≈ 35 ticks

    # ----- Tipping thresholds -----
    TIPPING_ALIGNMENT: float = 0.6
    TIPPING_BLAME: float = 0.7
    LYNCH_EMOTIONS: frozenset = field(
        default_factory=lambda: frozenset({"anger", "fear"}),
    )


# =============================================================================
# Phase classification
# =============================================================================

def compute_phase(state: CrowdState) -> CrowdPhase:
    """Classify crowd into one of 4 phases based on state."""
    if state.density < 0.3 or state.alignment_strength < 0.3:
        return "idle"

    # aligned / lynch_mode require alignment > 0.6 AND density > 0.5
    if state.alignment_strength >= state.TIPPING_ALIGNMENT and state.density > 0.5:
        # check lynch: high blame + threatening emotion
        max_blame = max(state.blame_concentration.values(), default=0.0)
        if (max_blame >= state.TIPPING_BLAME
                and state.dominant_emotion in state.LYNCH_EMOTIONS):
            return "lynch_mode"
        return "aligned"

    # density high but alignment moderate
    if state.density > 0.5 and 0.3 <= state.alignment_strength < 0.6:
        return "gathered"

    return "idle"


# =============================================================================
# Per-tick step
# =============================================================================

def step_crowd(state: CrowdState) -> None:
    """Apply per-tick decay + drift. Mutates state in place.

    Called once per world tick. Agent action effects are applied separately
    via inject_* helpers (below) before step_crowd.
    """
    # Density slow drift toward 0 (사람이 흩어짐)
    state.density = max(0.0, state.density - state.density_decay)

    # Alignment drift toward 0 (정서 희미해짐)
    state.alignment_strength = max(0.0, state.alignment_strength - state.alignment_decay)

    # Volatility decay
    state.volatility = max(0.0, state.volatility - state.volatility_decay)

    # Blame decay per target
    for target in list(state.blame_concentration.keys()):
        new_val = state.blame_concentration[target] - state.blame_decay
        if new_val <= 0.01:
            del state.blame_concentration[target]
        else:
            state.blame_concentration[target] = new_val

    # Rumor intensity decay (links to information layer)
    state.rumor_intensity = max(0.0, state.rumor_intensity - state.rumor_intensity_decay)

    # Accusation amplification decays faster (acute property)
    state.accusation_amplification = max(
        0.0, state.accusation_amplification - 0.1,
    )

    # Iter 43: memory field decay removed for shame_climate +
    # authority_vigilance. shame_climate reduction comes from forgiveness
    # rumor (Iter 30). authority_vigilance has no downstream coupling
    # (Iter 38 removed). If regression appears, rollback.

    # Iter 90: public_suspicion DOES have auto-decay. ACTIVE meso-scale
    # memory; not a "climate" persistence field.
    state.public_suspicion = max(
        0.0, state.public_suspicion - state.public_suspicion_decay,
    )

    # Dominant emotion drifts back to indifferent when alignment is low
    if state.alignment_strength < 0.2:
        state.dominant_emotion = "indifferent"

    # Contagion: if alignment is high, amplify itself (positive feedback)
    if state.alignment_strength > 0.4:
        boost = (
            state.contagion_susceptibility * state.density
            * state.alignment_strength * 0.05
        )
        state.alignment_strength = min(1.0, state.alignment_strength + boost)


# =============================================================================
# Agent action → crowd update
# =============================================================================

def inject_crowd_event(
    state: CrowdState,
    event_type: str,
    *,
    target: str | None = None,
    intensity: float = 0.5,
) -> None:
    """Apply a crowd-affecting event. Called by external layers.

    event_types:
        - "gathering": density rises
        - "rumor_spread": rumor_intensity rises
        - "public_accusation": accusation_amplification rises + blame[target]
        - "assert_loyalty_public": alignment_strength rises (pro-crowd)
        - "defiant_voice": fragmentation rises
        - "authority_suppression": alignment_strength decays faster
        - "panic_scatter": density drops sharply
    """
    if event_type == "gathering":
        state.density = min(1.0, state.density + intensity * 0.2)
    elif event_type == "rumor_spread":
        state.rumor_intensity = min(1.0, state.rumor_intensity + intensity * 0.3)
    elif event_type == "public_accusation":
        state.accusation_amplification = min(
            1.0, state.accusation_amplification + intensity * 0.4,
        )
        if target:
            state.blame_concentration[target] = min(
                1.0, state.blame_concentration.get(target, 0.0) + intensity * 0.3,
            )
        # Alignment rises as crowd agrees on target (convergent focus).
        state.alignment_strength = min(
            1.0, state.alignment_strength + intensity * 0.15,
        )
        # Density also rises — accusation pulls bystanders to watch.
        state.density = min(1.0, state.density + intensity * 0.05)
        # Dominant emotion marks as anger/fear (direction of collective energy).
        # Once a crowd is blaming someone, its emotional tone is anger.
        if state.dominant_emotion not in ("anger", "fear"):
            state.dominant_emotion = "anger"
        # World memory: accusation creates lasting shame climate.
        state.shame_climate = min(
            1.0, state.shame_climate + intensity * 0.4,
        )
        # Iter 90: accusation raises general public_suspicion.
        # Iter 91: tuning -- saturation observed (rate 0.2 ceiling-stuck
        # at 1.0 for whole simulation horizon). Lowered to 0.05 so a
        # single accusation produces transient ~0.5 spike against
        # 0.02/tick decay (HL ~35t).
        state.public_suspicion = min(
            1.0, state.public_suspicion + intensity * 0.05,
        )
    elif event_type == "assert_loyalty_public":
        state.alignment_strength = min(1.0, state.alignment_strength + 0.05)
    elif event_type == "defiant_voice":
        state.fragmentation = min(1.0, state.fragmentation + intensity * 0.15)
    elif event_type == "authority_suppression":
        state.alignment_strength = max(0.0, state.alignment_strength * 0.8)
        state.accusation_amplification = max(
            0.0, state.accusation_amplification * 0.7,
        )
        # World memory: lasting authority vigilance after a suppression.
        state.authority_vigilance = min(
            1.0, state.authority_vigilance + intensity * 0.5,
        )
        # Iter 90: authority suppression raises public_suspicion.
        # Iter 91: tuning -- lowered from 0.3 to 0.1 (saturation).
        state.public_suspicion = min(
            1.0, state.public_suspicion + intensity * 0.1,
        )
    elif event_type == "panic_scatter":
        state.density = max(0.0, state.density - intensity * 0.4)
        state.alignment_strength = max(0.0, state.alignment_strength - intensity * 0.3)


def set_dominant_emotion(
    state: CrowdState, emotion: str, strength_boost: float = 0.2,
) -> None:
    """External events can set crowd emotional tone."""
    state.dominant_emotion = emotion
    state.alignment_strength = min(1.0, state.alignment_strength + strength_boost)
