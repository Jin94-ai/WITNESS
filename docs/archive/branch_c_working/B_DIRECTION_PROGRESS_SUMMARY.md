# B 방향 진행 정리 (로드맵 전체 매핑)

**작성:** 2026-04-24
**범위:** WITNESS_B_DIRECTION_ROADMAP.md Phase 1-7 전체 진행 상태.

---

## 0. 최종 비전 확인

> 특정 인물 재현 시뮬레이터 X. **가능성 지형이 계속 바뀌는 world process system** O.

---

## 1. Phase별 완료 매트릭스

### Phase 1 — Prototype 정리 (Step 1 완료)

| 산출물 | 위치 | 상태 |
|---|---|---|
| PETER_SPECIFIC_VS_GENERIC | `docs/persona_engine/` | ✓ (이전 세션) |
| **JUDAS_SPECIFIC_VS_GENERIC** | `docs/b_direction/` | ✓ **이번 세션** |
| **GENERIC_CORE_CANDIDATES** | `docs/b_direction/` | ✓ **이번 세션** |

**Phase 1 완료 기준:** ✓ Generic core 설명 가능 / Peter/Judas 차이 profile 관점으로 재서술.

---

### Phase 2 — Persona Engine 고정 (완료, 이전 세션들)

| 산출물 | 위치 | 상태 |
|---|---|---|
| RESPONSE_MOTIFS | `docs/persona_engine/` | ✓ |
| PERSONA_PROFILE_SCHEMA | `docs/persona_engine/` | ✓ |
| TARGET_ROLE_ONTOLOGY | `docs/persona_engine/` | ✓ |
| TRACE_PROVENANCE_EXTENSION | `docs/persona_engine/` | ✓ |
| POLICY_REFACTOR_PLAN | `docs/persona_engine/` | ✓ |
| Engine 구현 | `engine/persona/` | ✓ (13 tests) |
| Peter/Judas/VG profile | `content/*/v3/profile.json` | ✓ |

**Phase 2 완료 기준:** ✓ Direct boost → motif mediation / 같은 schema / generic role / 새 인물 = profile + binding.

---

### Phase 3 — World Process Engine (부분 완료)

| 산출물 | 위치 | 상태 |
|---|---|---|
| WORLD_ENGINE_REFRAMED_6_LAYER (= WORLD_LAYER_REDEFINITION) | `docs/world_engine/` | ✓ (이전 세션) |
| **CROWD_DYNAMICS** | `docs/b_direction/` | ✓ **이번 세션** |
| **RUMOR_PROPAGATION** | `docs/b_direction/` | ✓ **이번 세션** |
| **SPACE_AS_AFFORDANCE** | `docs/b_direction/` | ✓ **이번 세션** |
| TEMPORAL_RHYTHMS | `docs/b_direction/` | ⏳ 후속 |
| CROSS_LAYER_COUPLINGS | `docs/world_engine/` | ✓ (이전 세션) |
| WORLD_PROCESSES | - | ⏳ 통합 문서 (후속) |

**Phase 3 완료 기준:**
- ✓ 레이어 process 설계 (4/6 + 3 특화)
- ⏳ 구현 (`engine/world/crowd/`, `engine/world/information/`, `engine/world/space/` 미완)
- ⏳ 3개 독립 process 작동 (구현 후 검증)

---

### Phase 4 — Population Grammar (완료)

| 산출물 | 위치 | 상태 |
|---|---|---|
| **ROLE_ONTOLOGY** | `docs/b_direction/` | ✓ **이번 세션** (12 roles 확정) |
| **ARCHETYPE_LIBRARY** | `docs/b_direction/` | ✓ **이번 세션** (12 archetypes) |
| POPULATION_GRAMMAR (= POPULATION_GENERATION_GRAMMAR) | `docs/world_engine/` | ✓ (이전 세션) |
| AGENT_INITIALIZATION_RECIPE | `docs/world_engine/` | ✓ (이전 세션) |
| Engine 구현 | `engine/population/` | ✓ (18 tests) |

**Phase 4 완료 기준:** ✓ 새 agent = config / 8-12명 auto-init 가능 / role + archetype 로 차이.

---

### Phase 5 — Micro-world (문서 완료, 구현 미)

| 산출물 | 위치 | 상태 |
|---|---|---|
| **MICRO_WORLD_SPECS** | `docs/b_direction/` | ✓ **이번 세션** (3 scenarios) |
| Scenario specs 구현 | `content/worlds/` | ⏳ 후속 |
| Trajectory logs | - | ⏳ 구현 후 |

**Phase 5 완료 기준:** ⏳ (구현 후 판정)

---

### Phase 6 — Story Probe Loop (문서 완료)

| 산출물 | 위치 | 상태 |
|---|---|---|
| **STORY_PROBE_PROTOCOL** | `docs/b_direction/` | ✓ **이번 세션** |
| Probe batch examples | - | ⏳ 구현 후 |
| Evaluation checklist | `STORY_PROBE_PROTOCOL §5` | ✓ |

---

### Phase 7 — Rubric 재설계 (문서 완료)

| 산출물 | 위치 | 상태 |
|---|---|---|
| **RUBRIC_REDESIGN** | `docs/b_direction/` | ✓ **이번 세션** (Level 1-5 + Reference policy) |
| REFERENCE_SET_POLICY (= RUBRIC_REDESIGN §3) | 통합 | ✓ |
| WORLD_LEVEL_EVALUATION_SKETCH (= RUBRIC_REDESIGN §4) | 통합 | ✓ |
| RUBRIC_PHASE_H_REDIRECTION | `docs/rubric/` | ✓ (이전 세션) |

---

### Phase 8 — Neural (미개시, 후순위)

Lee §10 금지 유지: motif layer + profile schema 완성 후에만.

---

## 2. 이번 세션 신규 문서 (7개, docs/b_direction/)

1. JUDAS_SPECIFIC_VS_GENERIC.md
2. GENERIC_CORE_CANDIDATES.md
3. CROWD_DYNAMICS.md
4. RUMOR_PROPAGATION.md
5. SPACE_AS_AFFORDANCE.md
6. ROLE_ONTOLOGY.md
7. ARCHETYPE_LIBRARY.md
8. MICRO_WORLD_SPECS.md
9. STORY_PROBE_PROTOCOL.md
10. RUBRIC_REDESIGN.md
11. B_DIRECTION_PROGRESS_SUMMARY.md (본 문서)

---

## 3. 전체 완료 조건 (Lee §14)

| 조건 | 상태 |
|---|---|
| 1. 인물 하나 새 규칙 없이 생성 | ✓ (Phase 4 완료, role + archetype + profile overrides) |
| 2. 세계 사람 없이 굴러가기 | **부분** (문서 완, 구현 미) |
| 3. crowd/rumor/institution/space/time 중 4개 독립 동학 | **부분** (문서 3개 + 6 layer reframe, 구현 미) |
| 4. Story probe 에서 story-like flow 반복 | ⏳ 구현 + probe batch 후 |
| 5. 특정 인물 없는 micro-world 유의미 dynamics | ⏳ 구현 후 |
| 6. Peter/Judas 검증 기준으로만 사용 | **부분** (Peter/Judas 있지만 아직 검증 기준 역할 미정 — rubric 재설계 완료 후) |
| 7. Evaluation character → world-level 확장 | **부분** (문서 완료, 구현 미) |

**문서 완료: 7/7. 구현: 2/7.**

---

## 4. 구현 로드맵 (자율 진행 제안)

Lee "자체판단 계속 진행" 기조 유지.

### 우선순위 Q1 (다음 iteration)
1. `engine/world/crowd/state.py` — CrowdState + phase transition logic
2. `engine/world/information/rumor_registry.py` — RumorRegistry
3. `engine/world/space/spatial_registry.py` — SpatialRegistry (12 locations)

### 우선순위 Q2
4. Micro-World 1 (accusation_scene) 실제 run
5. Story Probe Batch 1 (5 probes)
6. Population-level rubric Level 4

### 우선순위 Q3
7. Role + Archetype generator 통합 (Peter/Judas/VG 재생성 실증)
8. Micro-world 2, 3 추가
9. World-level rubric Level 5
10. Lee sanity check

### 우선순위 Q4 (Phase 8)
11. Neural motif arbitration (단 rule-based fallback 유지)

---

## 5. 정직 고지 (HARNESS H4)

### 5.1 완료 아닌 것
- **구현 없음**: 이번 세션 모든 Phase 3/4/5 신규 docs는 설계. engine/world/crowd/ 등 아직 없음.
- **검증 없음**: Micro-world 3개 중 0개 실제 run.
- **Probe batch 없음**: Story probe 프로토콜 완, 실제 probe 수행 0.

### 5.2 낮은 추상 수준
- 각 layer의 process / coupling / affordance 공식이 pseudocode 수준. 실제 구현 시 세부 공식 조정 필요.
- Location schema, Rumor schema, CrowdState schema 등 dataclass 예시는 1차 초안.

### 5.3 가능 리스크
- 문서 완결성이 **"구현으로 다 가능"** 을 의미하지 않음
- Role-archetype 조합으로 Peter/Judas/VG 재현 가능성은 가설
- Micro-world emergent dynamics 가 실제로 story-like 일지 불확실

---

## 6. HARNESS 자가감사

### H1 null hypothesis
"10 문서 완성 = 프로젝트 성숙" 이 아님. Trivial explanation:
- 문서는 문서일 뿐. 구현과 실행이 없으면 가설에 불과.
- 기각하지 못함. 따라서 "structural blueprint 완료" 수준의 주장만.

### H4 What could still be wrong
- Crowd phase transition이 현실 관찰 가능한지 불명
- Role + Archetype 조합이 실제로 Peter-level 서사 나오는지 불명
- 12 motif 부족 가능성 (Lee Phase 2 §4.2 "추가 후보 protect/exploit/attach/detach" 미결정)
- Reference set 재생성 경로 불명확

### H6 Next direction (equal-weight)
- **A**: 구현 Q1 (crowd/rumor/space dataclasses) — 문서를 코드로
- **B**: Peter/Judas/VG 재구성 실증 (role + archetype 조합으로 기존 profile 근사)
- **C**: 기존 371+18=389 tests green 유지하며 engine 안정화
- **D**: Phase 2 motif 12개 확정 (Lee 검토 대기 항목)

**내 bias:** A (구현으로 이동). 문서 누적 효용 감소. 다음 iteration에서 crowd/rumor/space dataclass 착수.

### H7 금지어
- "완료", "성공" 단독 사용 X → "문서 완료 / 구현 미" 조건부
- "검증됨" X → "가설 수립"
- "정직 고지" 섹션 §5 포함

---

## 7. 한 줄 요약

**B 방향 로드맵 문서 7 Phase 완료 (이번 세션 10 문서 신규). 구현은 Phase 2/4만 완료. 다음 iteration 부터 Phase 3 (crowd/rumor/space) 구현 착수.**

---

**End of B direction progress summary.**
