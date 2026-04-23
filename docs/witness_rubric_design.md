# Witness v3.0 Rubric Design -- 4-Axis Discovery Evaluator

> **Spec**: [WITNESS_V3_REDESIGN.md](../WITNESS_V3_REDESIGN.md) §6
> **Code**: [engine/rubric/](../engine/rubric/)

## 1. 4축 개요 (spec §6.2)

| 축 | Critic | 측정 대상 |
|---|---|---|
| 1 Character Consistency | `character_critic.py` | 인물 고유성 (impulsivity, relationship response, fear-courage oscillation) |
| 2 Canon Compatibility | `canon_critic.py` | 정경 모순 여부 (hard + soft constraints) |
| 3 Causal Coherence | `causal_critic.py` | 상태 변화의 인과 설명 가능성 |
| 4 Novelty under Constraint | `novelty_critic.py` | 정경 복사 vs 의미 있는 다름 vs noise |

## 2. 통합 — RubricEvaluator

`rubric_evaluator.py::RubricEvaluator.evaluate(records, is_all_hardcoded)` 는 discovery_definitions §5 flowchart 를 구현:

```
Step 1: is_all_hardcoded?        → NOT_DISCOVERY_HARDCODED
Step 2: hard violation?          → INVALID
Step 3: drift ≤ reproduction_threshold? → CANONICAL_REPRODUCTION
Step 4: drift > noise_threshold? → NOT_DISCOVERY_NOISE
Step 5: drift in meaningful band + character < threshold → CANON_COMPATIBLE_ALTERNATIVE
Step 6: drift in meaningful band + character ≥ threshold → CHARACTER_CONSISTENT_NOVEL
```

## 3. Rule #14 준수

Spec §6.6 verbatim:
> *"Rubric을 학습 loss로 사용 금지 (Rule #14 위반)"*

구현 확인:
- 모든 critic의 반환 타입은 `*Report` dataclass (scalar/list). `torch.Tensor` 없음.
- 어디에도 `.backward()` / `loss.` 없음.
- 학습 loop (`engine/policies/neural/trainer.py`) 가 rubric import 안 함.

## 4. 단일 scalar 합산 금지 (spec §6.6)

`RubricReport` 는 4개 독립 sub-report (`character`, `canon`, `causal`, `novelty`) 를 별도 필드로 보존. `discovery_class` 레이블이 있지만 **scalar 합산 없음**. 축별 점수를 따로 해석 가능.

## 5. Character Critic 세부 -- "베드로다움" 측정의 한계

`CharacterCritic` 은 3 요소의 단순 평균으로 composite 계산:

1. **Impulsivity** -- 연속 tick의 action_kind 변동률
2. **Relationship coherence** -- event_category와 action_kind의 예상 매핑 비율
3. **Oscillation** -- fear_like 변수의 sign change 빈도

**솔직한 한계** (discovery_definitions §Alternate interpretation 2에서 이미 명시):
- 이 3 요소가 특정 인물(Peter 등)의 고유성을 충분히 정의하는지 미검증
- 다른 "즉각반응형" 인물 (예: 욥?)도 동일 점수 받을 수 있음 → 약한 critic
- Lee 신학적·문학적 검토로 상수 조정 필요

## 6. Novelty Critic 두 threshold

| Threshold | 의미 | 의의 |
|---|---|---|
| `copy_threshold` (기본 1.5) | drift 이하면 canon-copy (novel 아님) | §1 CANONICAL_REPRODUCTION 판정 보조 |
| `noise_threshold` (기본 15.0) | drift 초과면 random deviation | §4.2 NOT_DISCOVERY_NOISE 판정 |

**threshold 값은 잠정**. Phase 5+에서 실측 trajectory로 보정 필요. discovery_definitions §What-could-still-be-wrong 항목.

## 7. 한 줄 요약

**"4축 독립 critic + flowchart 분류 = spec §6.2 + Rule #13 구현. 학습 loss 사용 금지 (Rule #14), scalar 합산 금지. 각 critic threshold는 Phase 5+에서 실측 보정 필요."**
