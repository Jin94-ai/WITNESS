"""World-level Rubric Critic — Axis L5.

Phase 7 B direction final rubric level. Evaluates world-state evolution:
- world_coherence: cross-layer consistency (state without contradiction)
- phase_transitions: count of crowd/rumor/institutional phase shifts
- cross_layer_activations: coupling triggers per tick
- story_density: tipping points per 100 ticks
- path_dependence: world_state late diverges by early events

Input: world history (list of WorldStep from MicroWorld).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorldReport:
    n_ticks: int
    phase_transitions: dict[str, list[dict]]   # {crowd_id: [{tick, from, to}]}
    total_phase_transitions: int
    cross_layer_activations: int               # count of tick-level layer interactions
    story_density: float                       # tipping_points per 100 ticks
    world_coherence: float                     # 0-1 (no contradictions)
    path_dependence_evidence: float            # 0-1 (if divergence observed)
    notes: list[str] = field(default_factory=list)

    @property
    def is_living_world(self) -> bool:
        """Heuristic: world shows emergent dynamics."""
        return (
            self.total_phase_transitions >= 2
            and self.cross_layer_activations >= 5
            and self.story_density >= 1.0  # at least 1 tipping per 100 ticks
        )


class WorldCritic:
    """Evaluate world-state evolution dynamics.

    Typically called after a MicroWorld run:
        critic.evaluate(world_history=world.history)
    """

    def __init__(
        self,
        *,
        min_phase_transitions: int = 2,
        min_story_density: float = 1.0,  # per 100 ticks
    ) -> None:
        self._min_phases = min_phase_transitions
        self._min_density = min_story_density

    # -----------------------------------------------------------------
    # Phase transitions (from crowd_state_snapshot)
    # -----------------------------------------------------------------

    def _detect_phase_transitions(
        self, world_history: list,
    ) -> tuple[dict[str, list[dict]], int]:
        """For each crowd in history, detect phase change ticks."""
        transitions: dict[str, list[dict]] = {}
        prior_phase: dict[str, str] = {}
        for step in world_history:
            snapshot = step.crowd_state_snapshot
            for cid, c in snapshot.items():
                phase = c.get("phase", "idle")
                if cid in prior_phase and prior_phase[cid] != phase:
                    transitions.setdefault(cid, []).append({
                        "tick": step.tick,
                        "from": prior_phase[cid],
                        "to": phase,
                    })
                prior_phase[cid] = phase
        total = sum(len(v) for v in transitions.values())
        return transitions, total

    # -----------------------------------------------------------------
    # Cross-layer activations (proxy)
    # -----------------------------------------------------------------

    def _count_cross_layer_activations(self, world_history: list) -> int:
        """Count tick-events where >1 layer changes meaningfully.

        Heuristic: tick fires when (crowd state changes) AND (rumor state
        changes) AND (agent actions non-trivial).
        """
        count = 0
        for i, step in enumerate(world_history):
            crowd_active = any(
                c.get("alignment", 0) > 0.1 or len(c.get("blame", {})) > 0
                for c in step.crowd_state_snapshot.values()
            )
            rumor_active = len(step.rumor_snapshot) > 0
            if crowd_active and rumor_active:
                count += 1
        return count

    # -----------------------------------------------------------------
    # Story density
    # -----------------------------------------------------------------

    def _story_density(
        self, total_transitions: int, n_ticks: int,
    ) -> float:
        """Tipping events per 100 ticks."""
        if n_ticks == 0:
            return 0.0
        return 100.0 * total_transitions / n_ticks

    # -----------------------------------------------------------------
    # World coherence (contradiction detection)
    # -----------------------------------------------------------------

    def _world_coherence(self, world_history: list) -> float:
        """Check for contradictory states. Start with 1.0, deduct per issue.

        Issues:
            - phase = lynch_mode but alignment < 0.6 (contradictory per spec)
            - density declining while accusation rumor intensity rising
              sharply (expected: crowd pulled in by accusation)
            - blame saturated (>0.9) but dominant_emotion = indifferent
        """
        contradictions = 0
        total_checks = 0

        for step in world_history:
            for cid, c in step.crowd_state_snapshot.items():
                phase = c.get("phase")
                align = c.get("alignment", 0)
                total_checks += 1
                if phase == "lynch_mode" and align < 0.6:
                    contradictions += 1
                if phase == "aligned" and align < 0.6:
                    contradictions += 1

        if total_checks == 0:
            return 1.0
        coherence = 1.0 - (contradictions / total_checks)
        return max(0.0, coherence)

    # -----------------------------------------------------------------
    # Path dependence (proxy: does late-tick divergence trace to early)
    # -----------------------------------------------------------------

    def _path_dependence_proxy(self, world_history: list) -> float:
        """Heuristic: world exhibits path dependence if early event affects
        late phase. Proxy: look for tick where phase differs significantly
        between early (tick<N/3) and late (tick>2N/3) crowd states."""
        n = len(world_history)
        if n < 9:
            return 0.0  # too short

        early = world_history[:n // 3]
        late = world_history[2 * n // 3:]

        def _dominant_phase(steps: list) -> str:
            from collections import Counter
            phases = Counter()
            for step in steps:
                for c in step.crowd_state_snapshot.values():
                    phases[c.get("phase", "idle")] += 1
            if not phases:
                return "idle"
            return phases.most_common(1)[0][0]

        early_phase = _dominant_phase(early)
        late_phase = _dominant_phase(late)

        if early_phase == late_phase:
            return 0.0  # no divergence

        # Ordinal distance proxy
        phase_order = {"idle": 0, "gathered": 1, "aligned": 2, "lynch_mode": 3}
        distance = abs(
            phase_order.get(late_phase, 0) - phase_order.get(early_phase, 0)
        )
        return min(1.0, distance / 3.0)

    # -----------------------------------------------------------------
    # Top-level
    # -----------------------------------------------------------------

    def evaluate(self, world_history: list) -> WorldReport:
        n_ticks = len(world_history)
        transitions, total = self._detect_phase_transitions(world_history)
        cross_layer = self._count_cross_layer_activations(world_history)
        density = self._story_density(total, n_ticks)
        coherence = self._world_coherence(world_history)
        path_dep = self._path_dependence_proxy(world_history)

        notes = [
            f"n_ticks={n_ticks}",
            f"phase_transitions={total} across {len(transitions)} crowds",
            f"cross_layer_activations={cross_layer}",
            f"story_density={density:.2f} tippings/100 ticks",
            f"world_coherence={coherence:.3f}",
            f"path_dependence={path_dep:.3f}",
        ]

        return WorldReport(
            n_ticks=n_ticks,
            phase_transitions=transitions,
            total_phase_transitions=total,
            cross_layer_activations=cross_layer,
            story_density=density,
            world_coherence=coherence,
            path_dependence_evidence=path_dep,
            notes=notes,
        )
