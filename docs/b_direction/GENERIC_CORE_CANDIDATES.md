# Generic Core Candidates (Phase 1 B 방향)

**작성:** 2026-04-24
**목적:** Peter / Judas / Van Gogh 3 prototype에서 공통적으로 작동한 구조를 식별해 "generic core"로 고정.

---

## 0. 판정 기준

"Generic core" 자격:
1. **3 scenario 모두 사용** (person-agnostic 실증)
2. **Rule #1 준수** (grep 통과)
3. **scenario content 수정 없이 작동** (engine 수정만)

---

## 1. Tier 1: Generic Core (확정)

### 1.1 State ontology

- **ActiveState 19 변수** (scalar 13 + target-aware 6)
- 3 scenario 모두 같은 19 사용
- default_targets 는 generic role ontology (Step D migration 완료)
- **상태:** confirmed generic core

### 1.2 Pipeline

- `PersonV3Loop` 의 event → primitive update → pressure → motif → action → event feedback 루프
- 3 scenario 모두 같은 loop 실행
- **상태:** confirmed

### 1.3 Pressure computation

- 8 pressure (social_threat, physical_threat, shame_exposure, loyalty_pull, uncertainty, urgency, isolation_pressure, sacred_salience)
- 가중합 + clip 공식
- EventMemory (half-life 5)
- 3 scenario 공통 사용
- **상태:** confirmed

### 1.4 Motif layer (8 motif)

- conceal / confess / withdraw / remain_present / confront / grieve / seek_repair / observe_wait
- 3 scenario 모두 **같은 motif 활성 공식** 사용
- profile.motif_tendency 로 인물 차이
- **상태:** confirmed (단 Judas에서 scheme 부재 한계)

### 1.5 State transitions

- 27 direct edges (Cat A-E 20 + Cat F recovery 7)
- 3 scenario 공통 적용
- **상태:** confirmed

### 1.6 Availability gate

- 15 action gate 구조
- STRICT/MEDIUM/LOOSE 분류
- 3 scenario 공통
- **상태:** confirmed

### 1.7 Recovery profile

- 변수별 half-life + floor
- 3 scenario 공통
- **상태:** confirmed

### 1.8 Persona profile schema

- 4 section (pressure_sensitivity / motif_tendency / recovery_bias / relation_bias)
- motif_action_priors
- 3 scenario가 **같은 schema 위에 parameter만 다르게** 배치됨
- **상태:** confirmed

### 1.9 4-axis rubric

- Character / Scene response / Context break / Novelty
- rubric_evaluator flowchart
- **상태:** confirmed (단 alternative 분리 약함)

---

## 2. Tier 2: Generic Core Candidate (검증 중)

### 2.1 Event registry

- 24+ generic event (이번 iteration 에서 VG 3개 추가 → 27)
- 각 event가 `primitive_updates` 로 generic world effect
- **상태:** 3 scenario 모두 작동하나 event vocabulary 일부 Peter/VG 편향 (sacred_meal 특히)
- **추가 검증 필요:** 전혀 다른 장르 scenario에서 재사용 가능한지

### 2.2 Population generator

- `instantiate_agent(config)` — 7-field 최소 입력
- `generate_population(distribution, total_agents)` — bulk
- **상태:** 이번 세션 완성. 3 scenario 에는 아직 미적용.
- **추가 검증 필요:** Peter/Judas/VG 를 RoleCluster + profile_overrides 로 재구성 가능한지

### 2.3 Role Cluster (10 clusters)

- fisher_laborer, disciple_follower, authority_priest, merchant, outsider, family_anchor, crowd_participant, soldier_enforcer, elite_strategist, spiritual_wanderer
- **상태:** 정의됨, 사용 미검증
- **추가 검증:** Peter = fisher_laborer → disciple_follower 전환 / Judas = disciple → elite_strategist / VG = spiritual_wanderer 로 실제 profile 부분 재현 가능한지

---

## 3. Tier 3: Scenario-specific (content로만)

Engine 안에 넣으면 안 되는 것:

- Canonical sequence (`CANONICAL_SEQUENCE` tuple) — scenario content
- 인물 이름 / 장소 이름 / 집단 이름 (jesus, peter, jerusalem, 제자 등)
- faith_stage_tag 의 구체 단계 이름 (shepherd / foundation) — 후속 content-provided function 이전 중
- 각 rubric critic의 DEFAULT_SCENE_RESPONSE_FAMILIES 의 Peter 편향 (e.g., eye_contact → weep/withdraw/confess — 범용 인간 반응이긴 하지만 Peter story에서 유래)

---

## 4. Tier 4: 제거 후보 (leakage)

Lee 로드맵 §3.3C "leakage 제거":

### 4.1 `faith_stage_tag`
- **현재:** state_derived.py 에서 Christian narrative stage 계산 (shepherd / foundation / restored / ...)
- **문제:** narrative compression variable (Lee 지적). Rule #1 에 반 — 이름이 특정 종교 서사 함축.
- **조치 제안:** Phase 1 B 방향 §3.3C 에 따라 **제거** 또는 generic role_trajectory_tag 로 대체.
- **영향:** restoration_readiness derived 가 faith_stage_numeric 사용 → 재작성 필요.

### 4.2 canonical tick-specific action references
- run_peter_v3.py 의 `CANONICAL_SEQUENCE = [(5, "discuss"), (10, "stay_awake"), ..., (17, "deny"), ...]`
- 엔진 코드 아님 (scenario script) 이므로 Rule #1 위반 아니나, rubric 에서 직접 참조하면 문제 가능.
- **상태:** 허용. 단 engine 안에 절대 금지.

### 4.3 특정 event 이름 하드코딩
- scene_response_critic.DEFAULT_SCENE_RESPONSE_FAMILIES 의 event id 나열 (eye_contact, restoration_moment 등)
- **상태:** generic event id 이지만 Peter 내러티브 유래.
- **조치 제안:** scenario content 에서 scene_semantics.json 주입 가능하게 확장 (이미 critic ctor 에 override 허용).

---

## 5. 요약 (Phase 1 완료 체크)

### 5.1 Lee §3.5 완료 기준

| 기준 | 상태 |
|---|---|
| 현재 시스템의 generic core 설명 가능 | ✓ (Tier 1 9개 구조) |
| Peter/Judas 차이를 profile/binding 관점으로 재서술 | ✓ (JUDAS_SPECIFIC_VS_GENERIC §1.4 table) |

### 5.2 총 분류

- Tier 1 Generic Core (확정): **9 구조**
- Tier 2 Candidate (검증 중): **3 구조**
- Tier 3 Scenario-specific: 3+ (content 전용)
- Tier 4 Leakage (제거 후보): **3** (faith_stage_tag 등)

---

## 6. 다음 단계 (Phase 2 전환 시 중점)

1. Tier 4 leakage 3개 제거 / 강등
2. Tier 2 candidate 3개를 실제 scenario에 적용 실증
3. Engine 수정 최소화 — content + profile 만으로 새 scenario 수용

---

**End of generic core candidates.**
