# Iter 179 -- Step B1: Component Ledger RESERVE Formalization

**Date:** 2026-04-26
**Iteration:** Iter 179 (Step 4/7 of new directive)
**Severity:** LOW -- documentation only
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step B1

---

## 0. Lee의 원래 지시 (verbatim, H5)

> "B1. Reserve / dormant 공식 표기
> 현재 남은 reserve / remove 후보를 component ledger에 공식 반영한다.
> 해야 할 일:
> - 5 reserve 항목 확정 표기
> - 각 항목의 현재 상태, 제거 여부 아님, future reactivation 조건 한 줄씩 기록
> - unwired / doc-only / decorative 여부 표시
> 산출물:
> - docs/b_direction/COMPONENT_LEDGER.md 업데이트
> - docs/b_direction/STATE_FIELD_STATUS.md"

---

## 1. What I did

### 1.1 STATE_FIELD_STATUS.md (NEW, 230 lines)
Per-field canonical reference. 5 RESERVE state fields formally classified:
1. `moral_injury` (RESERVE, unwired/latent-infra/doc-only)
2. `identity_shift` (RESERVE, unwired/latent-infra/doc-only)
3. `trust_scar` (RESERVE, unwired/latent-infra/slow-recovery-infra)
4. `event_trauma` (RESERVE, unwired/latent-infra/slow-recovery-infra)
5. `breach_count` (RESERVE lowest priority, unwired/doc-only)

Each field has:
- Status (RESERVE / ACTIVE / etc.)
- Tags (unwired / doc-only / decorative / latent-infra / slow-recovery-infra)
- MicroWorld empirical (Iter 162 Δ shame measurement)
- Cross-pipeline reads (which other pipelines depend on it)
- Future reactivation condition
- Removal blocker (why DO NOT REMOVE)

Plus:
- §3 awe reclassification (RESERVE → ACTIVE conditional)
- §4 profile fields (recovery_bias, relation_bias) cross-pipeline RESERVE
- §5 SlowStateFieldRecoveryRule (unwired rule, RESERVE)
- §6 dormant events (prayer_invitation, miracle_witnessed REMOVE_CANDIDATE)
- §7 summary table (12 items total)

### 1.2 COMPONENT_LEDGER.md update (+87 lines)
Appended §11 "State field RESERVE formalization (Iter 179, Step B1)":
- §11.1 awe reclassification note
- §11.2 SlowStateFieldRecoveryRule status
- §11.3 Removal policy (DO NOT REMOVE)
- §11.4 Profile fields cross-reference
- §11.5 Updated summary count table

Versioning: v1 (Iter 52) → v1.1 (Iter 179)

---

## 2. Lee가 원한 것 / 내가 한 것 대비 (H5)

| Lee 요구 | 내가 한 것 | Status |
|---|---|---|
| 5 reserve 항목 확정 표기 | moral_injury, identity_shift, trust_scar, event_trauma, breach_count | DONE |
| 현재 상태 한 줄 | STATUS column + 8 tags vocabulary | DONE |
| 제거 여부 아님 | "Removal blocker" + §8 "DO NOT REMOVE" 명시 | DONE |
| future reactivation 조건 한 줄 | 각 필드 §2.1-2.5에 "Future reactivation condition" line | DONE |
| unwired / doc-only / decorative 여부 표시 | tags 시스템 (unwired, doc-only, decorative, latent-infra, slow-recovery-infra) | DONE |
| COMPONENT_LEDGER.md 업데이트 | §11 신규 섹션 추가 | DONE |
| STATE_FIELD_STATUS.md | 신규 작성 (230 lines) | DONE |

**축소 해석한 부분 없음**. Lee 요구를 full coverage로 처리.

---

## 3. 핵심 발견 (재확인)

### 3.1 5 RESERVE 필드 확정
Iter 89 (grep 정적 분석) + Iter 162 (PYHASH N=15 ablation) 두 evidence 일치.
모든 5 필드 모두 cross-pipeline 의존성 있어 **DO NOT REMOVE**.

### 3.2 awe 재분류 (RESERVE → ACTIVE conditional)
Iter 89 audit는 awe를 "INERT/RESERVE"로 분류했으나 Iter 162 PYHASH 측정 결과
**Δ shame = +1.73** (non-zero). Iter 123은 sacred 컨텍스트에서 load-bearing
mechanism 확인. 따라서 awe는 5 RESERVE 목록에서 제외.

### 3.3 breach_count 우선순위 강등
Iter 89 audit는 breach_count를 "REMOVE_CANDIDATE"로 분류 (lowest dependency).
Iter 162 promote to RESERVE 했으나 v1.2에서 claim하지 않으면 다시 REMOVE_CANDIDATE
가능. STATE_FIELD_STATUS §2.5에 "lowest priority RESERVE" 명시.

---

## 4. What could still be wrong (H4)

### 4.1 Pydantic injection caveat (재반복)
Iter 89 + Iter 162 ablation은 `agent.state[path]` injection 사용. slow_state는
Pydantic AgentState.slow_state에 위치. 따라서 Δ=0.00 결과는 **truly INERT 또는
no-op injection** 두 가지 모두 가능. Static grep evidence는 독립적이고 더 강함.

### 4.2 Cross-scenario coverage
두 audit 모두 accusation scenario 위주. Scarcity / sacred 경험적 confirmation
부분적. Static analysis는 모든 scenario 커버.

### 4.3 awe direction-of-effect 미해결
Iter 162 측정: 주입 시 shame INCREASE (+1.73). Iter 92-95 mechanism 예측: DECREASE.
미테스트 설명:
- awe_decay (0.05/tick) 빠른 thresholds 하강
- crowd state 초기화 interaction
- aux pathway 조건부 fire

awe ACTIVE conditional 분류했지만 mechanism validation 불완전.

### 4.4 RESERVE 등급 차등화 부족
5 필드 모두 "RESERVE"로 평등 처리. 실제로는:
- trust_scar / event_trauma: SlowStateFieldRecoveryRule 이미 정의됨 (가장 강한 reactivation candidate)
- moral_injury / identity_shift: latent_drive infra만 (medium)
- breach_count: 어느 candidate rule도 없음 (weakest)

이 차등을 STATE_FIELD_STATUS §7 summary table에 노출했으나, 별도 등급 시스템
미정립.

---

## 5. What I did NOT try (H2)

- **Pydantic AgentState 통한 proper injection** — no-op caveat 해소 가능
- **Cross-scenario empirical confirmation** (scarcity + sacred 추가)
- **awe mechanism 직접 probe** (decay interaction, crowd state interaction)
- **RESERVE 우선순위 등급 시스템** 정립 (high / medium / low)
- **prayer_invitation / miracle_witnessed REMOVE 결정** (Lee gate)
- **v1.2 SlowStateFieldRecoveryRule prototype 와이어링**

이유:
- Step B1은 "표기" (documentation)이지 새 ablation 아님
- 디렉티브 §6: 새 메커니즘 drilling 금지
- Removal 결정은 Lee gate

---

## 6. Alternate interpretations (H4)

- **"5 reserve 항목"이 awe 포함**: 그러면 awe 재분류 잘못. 하지만 Iter 162에서
  Δ +1.73 측정했으므로 evidence 우선. awe → ACTIVE conditional.
- **"공식 표기"가 engine 코드에 annotation 의미**: 그러면 state.py에 docstring
  추가 필요. 현재 docs/만 작성. Lee 재확인 가능.
- **"5 reserve"가 state field만 아니라 모든 RESERVE 포함**: profile fields,
  rule 등 더 많을 수 있음. STATE_FIELD_STATUS §7 summary는 12 항목 모두 커버
  하므로 super-set.

---

## 7. 진행 상황

| Step | 상태 |
|---|---|
| A1: annotated probe 포맷 표준화 | DONE (Iter 176) |
| A2: readability pilot 4 세트 준비 | DONE (Iter 177) |
| A3: Readability Blind Protocol V2 + Results V2 | DONE (Iter 178) |
| **B1: component ledger 업데이트 (5 RESERVE)** | **DONE (이번 iter)** |
| B2: breach_count + unwired field 문서화 | NEXT (Iter 180) |
| B3: SACRED_STATUS_NOTE.md | PENDING |
| B4: KERNEL_GAPS.md | PENDING |

Track A 완료 + Track B 1/4 진행.

---

## 8. 결론

**산출물**:
- `docs/b_direction/STATE_FIELD_STATUS.md` (230 lines, new)
- `docs/b_direction/COMPONENT_LEDGER.md` (+87 lines, §11 new section)

**5 RESERVE state fields 공식 표기 완료**. 각 필드:
- 한 줄 status + tags
- empirical evidence (Iter 162)
- cross-pipeline 의존성
- future reactivation condition
- removal blocker

**awe 재분류 (Iter 162 evidence 반영)**. **breach_count 우선순위 강등** (lowest
RESERVE candidate).

**No engine changes**. 순수 문서화 + 분류 표시.

다음 iter (Step B2)에서 breach_count + unwired field 추가 문서화. SlowState
FieldRecoveryRule docstring 업데이트, narrative-field 상태 기록 등.
