"""Population-level Rubric Critic — Axis L4.

Phase 7 B direction extension. Evaluates multi-agent population behavior:
- motif_diversity_index: Shannon entropy of motif distribution across agents
- role_archetype_distinctness: within-role variance of motif distributions
- pressure_response_variance: how varied agents' pressure reactions are
- emergent_event_fraction: emergent vs scripted events

Input: list of agent trajectories + population metadata.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import log


@dataclass
class PopulationReport:
    n_agents: int
    motif_diversity_index: float          # 0-1 (Shannon entropy normalized)
    role_archetype_distinctness: float    # 0-1 (higher = role differences visible)
    pressure_response_variance: float     # 0-1 (higher = agents react diversely)
    emergent_event_fraction: float        # 0-1 (emergent / total events)
    role_motif_correlation: float         # 0-1 (role predicts motif)
    notes: list[str] = field(default_factory=list)

    @property
    def composite(self) -> float:
        """Simple mean of 4 axes (not used for ranking, just a summary)."""
        return (
            self.motif_diversity_index
            + self.role_archetype_distinctness
            + self.pressure_response_variance
            + self.emergent_event_fraction
        ) / 4.0


class PopulationCritic:
    """Evaluate multi-agent population dynamics.

    Typically called on output of MicroWorld run:
        critic.evaluate(
            per_agent_trajectories={agent_id: [tick_records]},
            agent_role_map={agent_id: role_id},
            event_log=[{tick, event_id, by?}, ...],
        )
    """

    def __init__(
        self,
        *,
        min_diversity: float = 0.3,
        min_distinctness: float = 0.25,
        emergent_target: tuple[float, float] = (0.3, 0.9),
    ) -> None:
        self._min_div = min_diversity
        self._min_dist = min_distinctness
        self._emergent_target = emergent_target

    # -----------------------------------------------------------------
    # Motif diversity (across all agents × all ticks)
    # -----------------------------------------------------------------

    def _shannon(self, counts: Counter) -> float:
        """Normalized Shannon entropy. 1.0 = uniform, 0.0 = single bucket."""
        n = sum(counts.values())
        if n <= 1 or len(counts) <= 1:
            return 0.0
        entropy = -sum((c / n) * log(c / n) for c in counts.values() if c > 0)
        max_ent = log(len(counts))
        return entropy / max_ent if max_ent > 0 else 0.0

    def _motif_diversity(
        self, trajectories: dict[str, list[dict]],
    ) -> tuple[float, str]:
        all_motifs: Counter = Counter()
        for records in trajectories.values():
            for rec in records:
                motif = rec.get("selected_motif") or rec.get("motif")
                if motif:
                    all_motifs[motif] += 1
        if not all_motifs:
            return 0.0, "no motif data"
        div = self._shannon(all_motifs)
        return div, f"entropy={div:.3f} over {len(all_motifs)} motifs"

    # -----------------------------------------------------------------
    # Role-archetype distinctness
    # -----------------------------------------------------------------

    def _role_archetype_distinctness(
        self,
        trajectories: dict[str, list[dict]],
        role_map: dict[str, str],
    ) -> tuple[float, str]:
        """Within-role motif variance. Higher = archetype diversity visible
        inside same role."""
        by_role: dict[str, list[Counter]] = {}
        for agent_id, records in trajectories.items():
            role = role_map.get(agent_id, "unknown")
            motifs = Counter()
            for rec in records:
                m = rec.get("selected_motif") or rec.get("motif")
                if m:
                    motifs[m] += 1
            by_role.setdefault(role, []).append(motifs)

        scores = []
        for role, distributions in by_role.items():
            if len(distributions) < 2:
                continue
            # Compare pairwise: Jaccard-inspired distance between motif distributions
            pair_divs = []
            for i in range(len(distributions)):
                for j in range(i + 1, len(distributions)):
                    a = distributions[i]
                    b = distributions[j]
                    all_keys = set(a) | set(b)
                    if not all_keys:
                        continue
                    na, nb = sum(a.values()), sum(b.values())
                    if na == 0 or nb == 0:
                        continue
                    # L1 distance in normalized distributions
                    dist = 0.5 * sum(
                        abs(a.get(k, 0)/na - b.get(k, 0)/nb)
                        for k in all_keys
                    )
                    pair_divs.append(dist)
            if pair_divs:
                scores.append(sum(pair_divs) / len(pair_divs))
        if not scores:
            return 0.0, "no within-role pairs"
        distinctness = sum(scores) / len(scores)
        return distinctness, f"mean within-role L1 dist={distinctness:.3f}"

    # -----------------------------------------------------------------
    # Pressure response variance (proxy: action entropy)
    # -----------------------------------------------------------------

    def _pressure_response_variance(
        self, trajectories: dict[str, list[dict]],
    ) -> tuple[float, str]:
        """Variance of action distributions across agents. Higher = more
        varied reactions."""
        agent_actions: list[Counter] = []
        for records in trajectories.values():
            a = Counter()
            for rec in records:
                act = rec.get("action_id") or rec.get("action")
                if act:
                    a[act] += 1
            if a:
                agent_actions.append(a)
        if len(agent_actions) < 2:
            return 0.0, "need ≥2 agents"
        # Pairwise L1 mean
        ds = []
        for i in range(len(agent_actions)):
            for j in range(i + 1, len(agent_actions)):
                a, b = agent_actions[i], agent_actions[j]
                na, nb = sum(a.values()), sum(b.values())
                all_keys = set(a) | set(b)
                d = 0.5 * sum(
                    abs(a.get(k, 0)/na - b.get(k, 0)/nb) for k in all_keys
                )
                ds.append(d)
        mean_d = sum(ds) / len(ds)
        return mean_d, f"mean pairwise action L1={mean_d:.3f}"

    # -----------------------------------------------------------------
    # Emergent event fraction
    # -----------------------------------------------------------------

    def _emergent_fraction(
        self, event_log: list[dict],
    ) -> tuple[float, str]:
        total = len(event_log)
        if total == 0:
            return 0.0, "no events"
        emergent = sum(1 for ev in event_log if ev.get("by") is not None)
        frac = emergent / total
        return frac, f"emergent={emergent}/{total}"

    # -----------------------------------------------------------------
    # Role → motif correlation
    # -----------------------------------------------------------------

    def _role_motif_correlation(
        self,
        trajectories: dict[str, list[dict]],
        role_map: dict[str, str],
    ) -> tuple[float, str]:
        """Correlation: does role predict motif? Computed via entropy
        reduction — if knowing role reduces motif entropy, role is predictive."""
        # Global motif entropy
        all_motifs = Counter()
        for records in trajectories.values():
            for rec in records:
                m = rec.get("selected_motif") or rec.get("motif")
                if m:
                    all_motifs[m] += 1
        if not all_motifs:
            return 0.0, "no motif data"
        H_motif = self._shannon(all_motifs)

        # Conditional: for each role, compute motif distribution, then
        # average entropy weighted by role size
        by_role: dict[str, Counter] = {}
        role_sizes: dict[str, int] = {}
        for agent_id, records in trajectories.items():
            role = role_map.get(agent_id, "unknown")
            by_role.setdefault(role, Counter())
            for rec in records:
                m = rec.get("selected_motif") or rec.get("motif")
                if m:
                    by_role[role][m] += 1
                    role_sizes[role] = role_sizes.get(role, 0) + 1

        total = sum(role_sizes.values()) or 1
        conditional_H = sum(
            (role_sizes[role] / total) * self._shannon(counter)
            for role, counter in by_role.items()
        )
        # Reduction: H(motif) - H(motif | role). 0 = no predictive. 1 = perfect.
        reduction = max(0.0, H_motif - conditional_H)
        # Normalize by H_motif (when H_motif = 0, reduction is also 0)
        norm = reduction / H_motif if H_motif > 0 else 0.0
        return norm, f"H_motif={H_motif:.3f} H_motif|role={conditional_H:.3f}"

    # -----------------------------------------------------------------
    # Top-level
    # -----------------------------------------------------------------

    def evaluate(
        self,
        per_agent_trajectories: dict[str, list[dict]],
        agent_role_map: dict[str, str],
        event_log: list[dict],
    ) -> PopulationReport:
        div, div_note = self._motif_diversity(per_agent_trajectories)
        dist, dist_note = self._role_archetype_distinctness(
            per_agent_trajectories, agent_role_map,
        )
        var, var_note = self._pressure_response_variance(per_agent_trajectories)
        frac, frac_note = self._emergent_fraction(event_log)
        corr, corr_note = self._role_motif_correlation(
            per_agent_trajectories, agent_role_map,
        )

        notes = [
            div_note, dist_note, var_note, frac_note, corr_note,
            f"diversity≥{self._min_div}: {'OK' if div >= self._min_div else 'low'}",
            f"distinctness≥{self._min_dist}: {'OK' if dist >= self._min_dist else 'low'}",
        ]

        return PopulationReport(
            n_agents=len(per_agent_trajectories),
            motif_diversity_index=div,
            role_archetype_distinctness=dist,
            pressure_response_variance=var,
            emergent_event_fraction=frac,
            role_motif_correlation=corr,
            notes=notes,
        )


def world_history_to_trajectories(
    world_history: list,
) -> tuple[dict[str, list[dict]], dict[str, str], list[dict]]:
    """Helper: convert MicroWorld.history → rubric inputs.

    Returns (per_agent_trajectories, agent_role_map, event_log).
    Requires caller to pass agent_role_map separately since MicroWorld
    stores role on AgentHandle.
    """
    per_agent: dict[str, list[dict]] = {}
    events: list[dict] = []
    for step in world_history:
        for agent_id, action in step.agent_actions.items():
            per_agent.setdefault(agent_id, []).append({
                "tick": step.tick,
                "action_id": action,
                "selected_motif": step.agent_motifs.get(agent_id),
            })
        for ev in step.spawned_events:
            events.append({
                "tick": step.tick,
                "event_id": ev.get("event_id"),
                "by": ev.get("by"),  # None for seed, agent_id for emergent
            })
    return per_agent, {}, events
