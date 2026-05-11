# Witness v3.0 Rubric Design -- 4-Axis Discovery *Candidate* Classifier

> **Spec**: [WITNESS_V3_REDESIGN.md](../WITNESS_V3_REDESIGN.md) §6
> **Review**: [WITNESS_V3_RUBRIC_DESIGN_REVIEW.md](WITNESS_V3_RUBRIC_DESIGN_REVIEW.md) (Phase 3.05)
> **Code**: [engine/rubric/](../engine/rubric/)

## Non-Claims (review §3)

이 evaluator는 신학적 정답을 증명하지 않는다.
이 evaluator는 문학적 완성도를 증명하지 않는다.
이 evaluator는 의미를 스스로 발견하지 않는다.

이 evaluator가 하는 일은 생성된 trajectory가 다음 조건을 만족하는지 *분류*하는 것이다:

1. 정경 hard constraint를 위반하지 않는가
2. 상태 변화와 행동이 인과적으로 설명 가능한가
3. 사전 정의한 character trait signature와 맞는가
4. 단순 복사도 아니고 무작위 noise도 아닌가

따라서 최종 label은 truth claim이 아니라 **discovery candidate class**로 해석해야 한다.

## 1. 4축 개요 (spec §6.2)

| 축 | Critic | 측정 대상 |
|---|---|---|
| 1 Character Consistency | `character_critic.py` | 인물 고유성 (impulsivity, relationship response, fear-courage oscillation) |
| 2 Canon Compatibility | `canon_critic.py` | 정경 모순 여부 (hard + soft constraints) |
| 3 Causal Coherence | `causal_critic.py` | 상태 변화의 인과 설명 가능성 |
| 4 Novelty under Constraint | `novelty_critic.py` | 정경 복사 vs 의미 있는 다름 vs noise |

## 2. 통합 — RubricEvaluator (Phase 3.05 review §2.2 P0 적용)

`rubric_evaluator.py::RubricEvaluator.evaluate(records, is_all_hardcoded)` flowchart:

```
Step 1: is_all_hardcoded?                  → NOT_DISCOVERY_HARDCODED
Step 2: hard canon violation?              → INVALID_CANON_VIOLATION
Step 3: causal smoothness < min_gate?      → NOT_DISCOVERY_INCOHERENT  ◀ P0 신규 (review §2.2)
Step 4: context-break rate ≥ threshold?    → NOT_DISCOVERY_NOISE
Step 5: novelty.band == "noise"?           → NOT_DISCOVERY_NOISE
Step 6: drift ≤ reproduction_threshold?    → CANONICAL_REPRODUCTION
Step 7: novelty=meaningful + char ≥ min + scene_fit ≥ min
                                           → CHARACTER_CONSISTENT_NOVEL_CANDIDATE  ◀ P0 (review §2.1)
Step 8: else canon-compatible              → CANON_COMPATIBLE_CHARACTER_DRIFT      ◀ P0 (review §2.1)
```

**P0 변경 요약** (Phase 3.05 cycle, 2026-05-11):
- INVALID → **INVALID_CANON_VIOLATION** (review §2.1 정식 명칭)
- Step 3에 **causal gate 추가** (review §2.2 — "인과 설명 불가능한 trajectory는 discovery 후보 자격 박탈")
- CHARACTER_CONSISTENT_NOVEL → **CHARACTER_CONSISTENT_NOVEL_CANDIDATE** (review §2.1 — truth claim 아닌 candidate class)
- CANON_COMPATIBLE_ALTERNATIVE → **CANON_COMPATIBLE_CHARACTER_DRIFT** (review §2.1 — 너무 긍정적인 명칭 회피)
- legacy enum values는 backwards compat alias로 유지
- `calibration_status = "uncalibrated_phase3_placeholder"` 명시 (review §2.7)

## 3. Rule #14 준수

Spec §6.6 verbatim:
> *"Rubric을 학습 loss로 사용 금지 (Rule #14 위반)"*

구현 확인:
- 모든 critic의 반환 타입은 `*Report` dataclass (scalar/list). `torch.Tensor` 없음.
- 어디에도 `.backward()` / `loss.` 없음.
- 학습 loop (`engine/policies/neural/trainer.py`) 가 rubric import 안 함.

## 4. 단일 scalar 합산 금지 (spec §6.6)

`RubricReport` 는 4개 독립 sub-report (`character`, `canon`, `causal`, `novelty`) 를 별도 필드로 보존. `discovery_class` 레이블이 있지만 **scalar 합산 없음**. 축별 점수를 따로 해석 가능.

### 2.5 P1 extended (cycle 16, 2026-05-11) — Pressure-Action Alignment

review §2.5 권고 *"pressure와 action 방향이 정렬되는가"*를 직접 측정.

`CausalCritic`에 *optional* `action_pressure_map: dict[str, list[str]]` 인자:
- 비어 있으면 (default) → `alignment_evaluated=False`, gate 영향 0 (engine person-agnostic)
- map 제공 시 (orchestrator/script가 content-specific 매핑 주입) → 각 tick에서 action_id 별 expected pressure field 중 *하나라도* `pressure_min_value` (default 3.0) 이상이면 aligned

`CausalReport` 새 필드 (default 값 → legacy callers 영향 0):
- `pressure_action_alignment: float` (0-1, aligned / (aligned+misaligned))
- `alignment_evaluated: bool` (True iff map 제공)
- `aligned_actions / misaligned_actions / unmapped_actions: int`
- `misaligned_examples: list[str]` (최대 5개 example)

Gate 확장: `passed_causal_gate`는 alignment_evaluated 시 `alignment_ratio >= pressure_action_alignment_min` (default 0.6, uncalibrated) 추가 조건.

이로써 review §2.5 권고 4/5 직접 측정 (delta exist / event window / action-pressure alignment / unexplained count). 남은 1: `causal_chain_length_avg` — 단순 평균이라 추가 가치 낮음. *결과물*: critic 강도 보강 + 새 6 tests + Rule #1 (person-agnostic) 유지.

---

## 5. Character Critic 세부 -- Phase H 재설계 + discrimination 입증 (cycle 23)

### 5.1 Phase H 재설계 (Rule #22 적용, 2026-04-23 기준)

**기존 3 요소 (deprecated)** — review §5 비판 대상:
1. Impulsivity (action_kind 변동률)
2. Relationship coherence (event×action 매핑)
3. Oscillation (fear_like sign change)

→ "매끈함" / "smoothness" 기반 측정이 character 고유성과 무관하다는 Rule #22 결정에 따라 *전면 삭제*.

**현행 3 축 (Phase H + review §2.3 P1)** — `engine/rubric/character_critic.py`:
1. **`relation_stability`** — primary_figure에 대한 loyalty/love/trust의 *unexplained* drop 비율 (deny action 동반 시 explained로 분류)
2. **`identity_retention`** — trajectory 끝에서 max(loyalty_pf, love, trust_pf) ≥ `minimum_final_identity` (default 4.0)
3. **`recovery_plausibility`** — guilt/grief spike (≥ spike_threshold) 이후 `repentance_response_window` 내에 repentance-family action (weep / confess / pray / withdraw_in_fear)

각 axis는 `*_min` minimum gate를 가지며 (`relation_stability_min=0.5`, `identity_retention_min=0.5`, `recovery_plausibility_min=0.3`, 모두 `uncalibrated_phase3_placeholder`), `passed_minimum_signature`는 *모든* 축이 minimum 이상일 때 True. composite은 *display only*.

### 5.2 Discrimination 입증 (cycle 23, 2026-05-11)

review §5 핵심 우려: *"다른 충동적/관계반응형 인물도 동일 점수 받을 수 있음 → 약한 critic"*. Phase H 재설계 후 이 우려가 해소됐는지 *empirical test*로 검증:

- **Anti-signature fixture** ([`tests/fixtures/rubric_demo/peter_anti_signature.json`](../tests/fixtures/rubric_demo/peter_anti_signature.json)): loyalty_pf가 deny action 없이 9→3 unexplained drop, 최종 loyalty 1.0 (minimum 4.0 미달), guilt spike (0→5) 후 7 ticks 동안 repentance-family action 0건 (continue_routine만 반복).
- **Deploy 결과** ([`docs/portfolio/demo_rubric/character_discrimination.json`](portfolio/demo_rubric/character_discrimination.json)):
  ```
  relation_stability   = 0.500   (at threshold)
  identity_retention   = 0.250   (< 0.5 → weak)
  recovery_plausibility = 0.000  (< 0.3 → weak)
  composite            = 0.250
  passed_minimum_signature = False
  weak_axes = [identity_retention, recovery_plausibility]
  ```
- **대조** — `peter_meaningful_novel` (positive class)은 `passed_minimum_signature=True`로 통과.
- **자동 검증**: `tests/test_rubric/test_rubric.py::test_phase3_05_character_critic_rejects_anti_signature_trajectory` + `test_phase3_05_character_critic_passes_meaningful_novel`.

**결론**: Phase H 3 축은 anti-Peter 궤적을 *양방향으로 discriminate* 한다 — false-positive (anti가 통과) 없음, false-negative (positive class가 실패) 없음. review §5 우려는 *현행 critic에는 적용되지 않는다*. threshold 보정은 Phase 5+ trajectory ensemble 수집 후 필요할 수 있으나, 현재 minimum gate가 *대략적인 discrimination*은 보장.

## 6. Novelty Critic 두 threshold

| Threshold | 의미 | 의의 |
|---|---|---|
| `copy_threshold` (기본 1.5) | drift 이하면 canon-copy (novel 아님) | §1 CANONICAL_REPRODUCTION 판정 보조 |
| `noise_threshold` (기본 15.0) | drift 초과면 random deviation | §4.2 NOT_DISCOVERY_NOISE 판정 |

**threshold 값은 잠정**. Phase 5+에서 실측 trajectory로 보정 필요. discovery_definitions §What-could-still-be-wrong 항목.

## 7. Acceptance Criteria (review §5 P2 + cycle 16+20 보강)

Rubric design 정합성 acceptance:

```text
[O] Final discovery labels use CANDIDATE / CHARACTER_DRIFT (review §2.1 P0)
[O] Causal coherence gate runs before novelty classification (review §2.2 P0)
[O] Character critic uses minimum-axis gates, not only average composite (§2.3 P1)
[O] Novelty critic separates canon drift from structured difference (§2.4 P1)
[O] Threshold config includes calibration_status (§2.7 P1)
[O] Report includes weak_axes / violations / unexplained_jumps / changed_axes (§2 P1+P2)
[O] Non-Claims section is present in the design doc (§3 P2)
[O] Rubric is not imported by neural trainer (Rule #14, §1.3)
[O] No scalar total discovery score is produced (§1.2)
[O] CanonReport separates hard_violations and soft_deviations + soft_compatibility_score (§2.6 P2)
[O] All thresholds marked "uncalibrated_phase3_placeholder" (§2.7)
[O] backwards compat: legacy enum values + composite field 유지 (legacy callers 영향 0)
[O] CausalReport에 pressure_action_alignment 측정 (review §2.5 P1 extended, cycle 16)
[O] CausalCritic이 optional action_pressure_map으로 engine person-agnostic 유지 (cycle 16)
[O] Rubric CLI가 --action-pressure-map flag로 alignment 측정 사용 가능 (cycle 20)
[O] CharacterCritic이 anti-signature 궤적을 *empirically* discriminate (cycle 23, peter_anti_signature fixture로 입증)
[O] CharacterCritic의 3 axis가 *independently* discrimination을 trigger (cycle 26, axis-isolated N-case ensemble — only_relation/only_identity/only_recovery fixtures)
[O] 모든 sub-report dataclass의 @property alias가 deployed JSON에 자동 노출 (cycle 28, generic walker — review §2.4 / §2.6 alias 강제 + meta-test invariant)
```

모든 acceptance는 `tests/test_rubric/test_rubric.py::test_phase3_05_*` 들로 강제 검증.

## 8. 한 줄 요약

**"4축 독립 critic + 8-step flowchart 분류 = spec §6.2 + Rule #13 + review §2.1-§2.7 P0+P1+P2 구현. 학습 loss 사용 금지 (Rule #14), scalar 합산 금지. 각 critic threshold는 'uncalibrated_phase3_placeholder' 명시 — Phase 5+ 실측 보정 필요. Final label은 *truth claim*이 아니라 *discovery candidate class*로 해석."**
