"""Causal Critic -- Axis 3 of 4-axis rubric.

Spec §6.2 verbatim:
    축 3: Causal Coherence
    - 상태 변화와 행동의 인과 설명 가능 여부
    측정: 상태 전이가 이유를 가지는가 / 뜬금없는 점프 / 시간 경과 자연스러움

Phase 3.05 rubric review §2.5 P1 보강:
    - explained_transition_ratio (0-1, 1 - unexplained_rate)
    - passed_causal_gate (boolean, gate decision)
    - calibration_status (uncalibrated_phase3_placeholder)

Phase 3.05 rubric review §2.5 P1 extended (cycle 16):
    - pressure_action_alignment (0-1, action이 상태 압력에 정렬되는지)
      review §2.5 권고 *"pressure와 action 방향이 정렬되는가"* 직접 측정.
      data-driven: optional `action_pressure_map` 인자만 받음 — 비어 있으면 1.0 default + gate에서 제외 (engine person-agnostic 유지).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalReport:
    unexplained_jumps: int       # count of unexplained state discontinuities
    mean_jump_size: float        # avg |Δstate| per tick (proxy)
    smoothness_score: float      # 0-1, 1 = no jumps
    notes: list[str]
    # Phase 3.05 rubric review §2.5 P1 — 보강 필드 (backwards compat: default values)
    explained_transition_ratio: float = 1.0   # (total - unexplained) / total
    total_transitions: int = 0
    passed_causal_gate: bool = True           # gate 통과 여부 (rubric_evaluator Step 3 이용 가능)
    calibration_status: str = "uncalibrated_phase3_placeholder"
    # Phase 3.05 rubric review §2.5 P1 extended (cycle 16) — pressure-action alignment
    pressure_action_alignment: float = 1.0    # 0-1, action이 상태 압력과 정렬된 비율
    alignment_evaluated: bool = False         # True iff action_pressure_map 제공됨
    aligned_actions: int = 0
    misaligned_actions: int = 0
    unmapped_actions: int = 0
    misaligned_examples: list[str] = field(default_factory=list)  # ["tick=N action_id pressure=X val=Y"]


class CausalCritic:
    """Measure causal coherence of state transitions.

    Heuristic: for each consecutive tick, compute the L1 norm of state
    changes. If a tick has a change > jump_threshold without a triggering
    event, flag as unexplained jump.

    Phase 3.05 review §2.5 P1: explained_transition_ratio + passed_causal_gate
    필드 추가. gate threshold는 uncalibrated placeholder.
    """

    def __init__(
        self,
        *,
        jump_threshold: float = 5.0,
        state_fields: list[str] | None = None,
        # Phase 3.05 review §2.5 P1 — gate thresholds (uncalibrated placeholder)
        explained_transition_min: float = 0.7,
        smoothness_min: float = 0.4,
        # Phase 3.05 review §2.5 P1 extended (cycle 16) — alignment 측정
        action_pressure_map: dict[str, list[str]] | None = None,
        pressure_action_alignment_min: float = 0.6,
        pressure_min_value: float = 3.0,
    ) -> None:
        self._jump_t = jump_threshold
        self._fields = state_fields or [
            "fear", "hope", "grief", "confusion", "love",
            "fatigue", "exhaustion_emotional",
        ]
        self._explained_min = explained_transition_min
        self._smoothness_min = smoothness_min
        # action_pressure_map: {action_id: [pressure_field, ...]}
        # 비어 있으면 alignment 측정 안 함 (gate에서 제외)
        self._action_pressure_map = dict(action_pressure_map or {})
        self._alignment_min = pressure_action_alignment_min
        self._pressure_min_value = pressure_min_value

    def evaluate(self, records: list[dict[str, Any]]) -> CausalReport:
        if len(records) < 2:
            return CausalReport(
                unexplained_jumps=0, mean_jump_size=0.0, smoothness_score=1.0,
                notes=["trajectory too short"],
                explained_transition_ratio=1.0,
                total_transitions=0,
                passed_causal_gate=True,
                alignment_evaluated=False,
            )

        jumps: list[float] = []
        unexplained = 0
        for i in range(len(records) - 1):
            prev = records[i].get("state", {})
            curr = records[i + 1].get("state", {})
            event = records[i + 1].get("event_triggered", False)
            size = 0.0
            for f in self._fields:
                size += abs(float(curr.get(f, 0.0)) - float(prev.get(f, 0.0)))
            jumps.append(size)
            if size > self._jump_t and not event:
                unexplained += 1

        total = len(jumps)
        mean_size = sum(jumps) / max(1, total)
        # Smoothness: 1 at mean_size=0, 0 at mean_size>=2*threshold
        smoothness = max(0.0, min(1.0, 1.0 - mean_size / (2.0 * self._jump_t)))
        # Phase 3.05 review §2.5: explained ratio = (total - unexplained) / total
        explained_ratio = (total - unexplained) / total if total > 0 else 1.0

        # Phase 3.05 review §2.5 extended (cycle 16) — pressure-action alignment
        # action_pressure_map: action_id → 정렬되어야 할 압력 field들.
        # 각 tick에서 action의 *현재 state* 압력 값이 임계 이상이면 aligned.
        # map 비어 있으면 alignment_evaluated=False + alignment=1.0 (gate 영향 없음).
        alignment_evaluated = bool(self._action_pressure_map)
        aligned, misaligned, unmapped = 0, 0, 0
        misaligned_examples: list[str] = []
        if alignment_evaluated:
            for rec in records:
                action_id = rec.get("action_id")
                if action_id is None:
                    continue
                expected_fields = self._action_pressure_map.get(action_id)
                if expected_fields is None:
                    unmapped += 1
                    continue
                state = rec.get("state", {})
                # action에 등록된 expected pressure field 중 *하나라도* 임계 이상이면 aligned
                pressure_satisfied = any(
                    float(state.get(f, 0.0)) >= self._pressure_min_value
                    for f in expected_fields
                )
                if pressure_satisfied:
                    aligned += 1
                else:
                    misaligned += 1
                    if len(misaligned_examples) < 5:
                        tick = rec.get("tick", "?")
                        vals = {f: float(state.get(f, 0.0)) for f in expected_fields}
                        misaligned_examples.append(
                            f"tick={tick} action={action_id} expected={expected_fields} "
                            f"values={vals}",
                        )
        evaluated_count = aligned + misaligned
        alignment_ratio = (aligned / evaluated_count) if evaluated_count > 0 else 1.0

        # passed_causal_gate: explained_ratio + smoothness + (optionally) alignment
        passed = (
            explained_ratio >= self._explained_min
            and smoothness >= self._smoothness_min
        )
        if alignment_evaluated and evaluated_count > 0:
            passed = passed and (alignment_ratio >= self._alignment_min)

        notes = [
            f"total_ticks={len(records)}",
            f"unexplained_jumps={unexplained}",
            f"explained_ratio={explained_ratio:.3f}",
            f"passed_causal_gate={passed}",
        ]
        if alignment_evaluated:
            notes.append(
                f"pressure_action_alignment={alignment_ratio:.3f} "
                f"(aligned={aligned}, misaligned={misaligned}, unmapped={unmapped})",
            )
        return CausalReport(
            unexplained_jumps=unexplained,
            mean_jump_size=mean_size,
            smoothness_score=smoothness,
            notes=notes,
            explained_transition_ratio=explained_ratio,
            total_transitions=total,
            passed_causal_gate=passed,
            pressure_action_alignment=alignment_ratio,
            alignment_evaluated=alignment_evaluated,
            aligned_actions=aligned,
            misaligned_actions=misaligned,
            unmapped_actions=unmapped,
            misaligned_examples=misaligned_examples,
        )
