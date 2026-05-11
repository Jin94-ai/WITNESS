# Persona Engine 전환 Step A — Generic vs Peter-specific 분리

**작성:** 2026-04-23
**목적:** 현재 v3 구현에서 공통 엔진(Generic)과 Peter 전용 patch를 식별하여 교체 우선순위를 설정.

---

## 0. 분리 기준

- **Generic**: 인물 독립. Rule #1 준수. 다른 scenario에서도 바로 재사용 가능.
- **Peter-specific patch**: canonical fit 향상 목적 / 특정 event ID에 직결 / 특정 action boost. 교체 대상.
- **Ambiguous**: 의미상 generic이지만 naming/default/weight가 Peter 기울어짐. 수정 대상.

---

## 1. 공통 엔진으로 남길 것 (Generic)

### 1.1 Core pipeline (유지)

| 모듈 | 분류 | 비고 |
|---|---|---|
| `engine/person/state_v3.py` — ActiveState 19 scalar/target-aware | **Generic** | Rule #15-18. 필드 이름 generic. |
| `engine/person/state_candidates.py` — Candidate registry | Generic | promotion blockers 메커니즘 |
| `engine/person/state_derived.py` — 8 derived + faith_stage_tag | Generic (단 faith_stage_tag 내부 임계값은 Peter 친화) |
| `engine/person/recovery_profile.py` — 변수별 half-life/floor | Generic | 수치는 튜닝 대상이나 구조는 공통 |
| `engine/world/primitives.py` — 19 primitives + decay_transients | Generic | |
| `engine/world/events.py` — 24 events | Generic | 이름 모두 generic (sacred_meal, public_accusation, ...) |
| `engine/world/pressure.py` — 8 pressures 가중합+clip + EventMemory | Generic | 공식 자체는 universal |
| `engine/action/availability_gate.py` — 2-stage structure | Generic | 구조는 유지, gate 내용 점검 필요 |
| `engine/action/action_event_mapper.py` — action→event mapping | Generic | 21 매핑 |
| `engine/constraint/hard_constraints.py` — anachronism / canon_contradiction / sacred_text | Generic | |
| `engine/constraint/soft_constraints.py` — edit-distance scorer | Generic | canonical_sequence는 scenario content |
| `engine/person/state_transitions.py` — 27 direct edges (Cat A-F) | **Generic** | v2 §6 각 edge 모두 generic (accusation_visibility, proximity_of_suffering 등 primitive 이름) |

### 1.2 Rubric (Phase H 재설계 후 Generic)

| 모듈 | 분류 | 비고 |
|---|---|---|
| `engine/rubric/character_critic.py` (H.1 재작성) | Generic | relation_stability / identity_retention / recovery_plausibility |
| `engine/rubric/scene_response_critic.py` | **Ambiguous** | DEFAULT_SCENE_RESPONSE_FAMILIES 에 Peter 친화 event IDs 포함 — scenario binding으로 분리 필요 |
| `engine/rubric/context_break_critic.py` | **Ambiguous** | DEFAULT_AFFORDANCES / MOTIVE_REQUIREMENTS — 동일 문제 |
| `engine/rubric/novelty_critic.py` (H.5 재작성) | Generic | structured_deviation |
| `engine/rubric/rubric_evaluator.py` | Generic | flowchart |

---

## 2. Peter-specific patch (교체 대상)

### 2.1 engine/person/loop.py `_decide_action` — **최우선 교체**

B2 retune (2026-04-23) 에서 추가된 direct action boost 전부:

| 라인 근처 | 내용 | 분류 | 교체 방식 |
|---|---|---|---|
| `accusation_fresh → deny +8.0` | 직접 boost | **Peter patch** | motif `conceal` 경유 |
| `accusation_fresh → all other × 0.25` | 대안 attenuate | **Peter patch** | motif 경쟁 구조로 |
| `eye_contact_fresh → weep +6.0` | 직접 boost | **Peter patch** | motif `grieve` 경유 |
| `eye_contact_fresh → deny × 0.15` | deny 억제 | **Peter patch** | motif `grieve` 활성 시 `conceal` 자연 감쇄 |
| `forgiveness_fresh → confess +2.0` | 직접 boost | **Peter patch** | motif `seek_repair` 경유 |
| `restoration_fresh → confess +6.0` | 직접 boost | **Peter patch** | motif `seek_repair` 경유 |
| `restoration_attenuate` / `eye_contact_attenuate` scale | 대안 attenuate | **Peter patch** | motif 경쟁으로 |
| Base weights (`follow_closely=2.0+0.2*love`, `pray=0.8+0.15*grief`, etc.) | | **Ambiguous** | base weight 자체는 generic 할 수 있으나 현재 Peter canonical 재현 위해 튜닝됨 |

**교체 방향 (Step C):**
```
scene → pressure → motif activation → motif-to-action distribution
(Persona profile 이 motif tendency / action mapping bias 결정)
```

### 2.2 Content / Reference naming (Peter-친화)

| 항목 | 현재 값 | Peter-specific? |
|---|---|---|
| `ActiveState.love / loyalty / trust` 기본 target | `primary_figure / peers / family` | **Ambiguous** — primary_figure는 generic이나 peers가 Peter disciples 연상 |
| `ActiveState.belonging` 기본 target | `twelve_disciples / broader_followers` | **Peter-specific** (Step D 대체) |
| `ActiveState.shame` 기본 target | `crowd / peers / self` | Generic-ish (crowd는 generic role) |
| `ActiveState.guilt` 기본 target | `primary_figure / self` | Generic |

**교체 방향 (Step D):**
- `twelve_disciples` → `peer_group` (또는 `in_group`)
- `broader_followers` → `public_group`
- `disciples` → `peer_group`
- 구체 인물/집단명은 content binding 으로만

### 2.3 Rubric scene families & affordances (Peter-친화)

| 위치 | Peter-specific 내용 | 교체 |
|---|---|---|
| `scene_response_critic.DEFAULT_SCENE_RESPONSE_FAMILIES` | eye_contact → weep/withdraw/confess (Luke 22:61 reference) | event id는 generic이나 family 구성이 Peter 중심 |
| `context_break_critic.DEFAULT_AFFORDANCES` | `requires_recent_restoration`, `requires_boat_or_shore` | 기독교 canonical scene에 기반 |
| `context_break_critic._STRONG_SCENE_CONFLICTS` | public_accusation vs [accept_washing, discuss_with_disciples, ...] | 가치 판단이 Peter 편향 |

**교체 방향:**
- Scene families는 **scenario content에서 주입** (`content/peter/v3/scene_response_families.json`)
- DEFAULT만 보편적 정서 profile (e.g., "threat → avoid/confront family"; "loss → grieve/withdraw family"; "sacred → reverent family") 로 축소
- Peter-특수 family는 content로 이동

### 2.4 Scripts (Peter-중심)

| 파일 | 분류 |
|---|---|
| `scripts/v3_measurement/run_peter_v3.py` | **Peter-specific entry point** — 유지 (scenario runner로 정당) |
| `scripts/v3_measurement/run_peter_v3_ensemble.py` | Peter-specific entry | 유지 |
| `scripts/v3_measurement/run_judas_v3.py` | Judas-specific entry | 유지 (Step G contrast bench) |
| `scripts/v3_measurement/calibrate_thresholds.py` | Generic (reference set 기반) | 유지 |
| `run_reference_evaluation.py` | Peter canonical_sequence 하드코딩 + ACTION_VOCAB | **Ambiguous** — `CANONICAL_SEQUENCE` / `ACTION_VOCAB`을 content에서 읽어오도록 |

---

## 3. Ambiguous (수정 대상)

### 3.1 PersonV3Loop 생성자 인자

현재:
```python
PersonV3Loop(initial_state_path, canonical_events_path, seed)
```

문제: 시나리오 이름 / role binding / motif profile 주입 경로가 없음.

**수정 방향 (Step E 준비):**
```python
PersonV3Loop(
    scenario_path,       # content/peter/v3/ 한 디렉토리 참조
    persona_profile,     # PersonaProfile (Step E)
    seed,
)
# 시나리오가 initial_state / canonical_events / targets / scene_families 모두 소유
```

### 3.2 ActiveState 기본 필드 default

`default_factory=dict` 이므로 content가 target 넣어야 함. 이 부분 generic. 단 `ACTIVE_VARIABLES_META.default_targets` 에 Peter 친화 이름 박혀 있음 → Step D에서 교체.

### 3.3 Derived `faith_stage_tag`

"shepherd / foundation / restored / failed / tested / follower / none" — 이름은 **Christian narrative**. 일부는 generic (follower, none), 일부는 Peter 아크 전용 (shepherd, foundation).

**수정 방향:** faith_stage_tag는 content-provided tag function으로 교체. 엔진은 generic "role_trajectory_tag" 만 제공, content가 scenario별 stage 이름 결정.

---

## 4. 교체 우선순위

| 순위 | 작업 | Step |
|---|---|---|
| 1 | `_decide_action` 을 3-stage motif mediation으로 교체 | Step C |
| 2 | `belonging` default targets `twelve_disciples / broader_followers` → `peer_group / public_group` | Step D |
| 3 | `scene_response` / `context_break` critic의 families/affordances 를 `content/peter/v3/scene_semantics.json` 에서 주입 | Step D, C 지원 |
| 4 | PersonaProfile 스키마 + Peter/Judas 초안 | Step E |
| 5 | `faith_stage_tag` → content-provided tag function | Step D + E |
| 6 | Provenance (selected_motif, blocked_actions, winning_action_reason) 기록 | Step F |

---

## 5. 금지 목록 (Lee §4 준수)

- **금지 1**: 새로운 accusation_fresh / eye_contact_fresh 류 direct action boost 추가 절대 금지.
- **금지 2**: Peter/Judas/VG 를 위한 변수 세트 분리 금지. 한 ActiveState 유지.
- **금지 3**: `jesus`, `disciples`, `followers`, `twelve` 같은 이름 engine/ 안에서 직접 사용 금지 (content binding 만).
- **금지 4**: "더 맞는다" (canonical fit 상승) 를 진전으로 간주 금지. Genericity 지표를 같이 봐야.
- **금지 5**: Motif layer와 profile schema 완성 전 Neural policy 도입 금지.

---

**End of Step A.**
