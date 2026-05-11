# Judas Specific vs Generic 분리 (Phase 1 B 방향)

**작성:** 2026-04-24
**목적:** Judas v3 prototype (D3 universality test) 에서 어떤 부분이 Judas-specific 이고 어떤 부분이 generic engine 위에 자연스럽게 얹힐 수 있는지 분리.

---

## 0. 원칙

- **Judas는 튜닝 대상 아님** (Rule #21). 본 문서도 Judas fit 개선 제안 금지.
- Judas는 **contrast benchmark** — "generic engine이 이질 인물을 수용하는가" 판정 자료.

---

## 1. Judas-specific 항목 분류

### 1.1 Generic (엔진에 공통 유지)

| 항목 | 근거 |
|---|---|
| `engine/person/loop.py` 의 3-stage motif mediation | Judas scenario도 같은 경로 |
| PersonV3Loop 의 event scheduler | canonical_events.json 구조 동일 |
| state_transitions.py Cat A-F | 같은 pressure → state 동학 |
| availability gate | 같은 action → gate 원리 |
| 4-axis rubric | 동일 critic |
| Active 19 state ontology | Judas도 19 유지 |

### 1.2 Content (Judas scenario binding)

| 항목 | 현재 값 | generic?  |
|---|---|---|
| `content/judas/v3/initial_state.json` | love_pf=6.5, loyalty=4.5, trust=4.0, doubt=6.0 | content — generic에 얹힘 |
| `content/judas/v3/canonical_events.json` | covert_bargain, identification_signal, remorse_trigger, return_token | **4 new events** — generic event registry 추가됨 |
| `content/judas/v3/profile.json` | observe_wait=1.3, seek_repair=0.4, ... | Profile parameters |
| Judas canonical sequence in `run_judas_v3.py` | 9 ticks tuple list | scenario content |

### 1.3 Ambiguous (주의 대상)

| 항목 | 우려 |
|---|---|
| 4개 event (covert_bargain, identification_signal, remorse_trigger, return_token) | Judas 특이 맥락이나 naming은 generic. 다른 시나리오에서 재사용 가능 여부 미검증 |
| Profile의 `observe_wait=1.3` + `seek_repair=0.4` | 이 조합이 "배신자" generic 이미 표현이면 OK. 아니면 scenario-specific |
| 4축 rubric에서 Judas가 거의 `not_discovery_noise` 로만 분류 | rubric이 Judas arc를 다루지 못함 (Judas-specific 실패 아님, rubric 일반화 문제) |

### 1.4 Peter와의 profile 차이 요약 (비교 재서술)

Judas 차이점은 **규칙 뭉치가 아니라 profile + binding**:

| 축 | Peter | Judas | 기능적 차이 |
|---|---|---|---|
| seek_repair | 1.4 | 0.4 | Judas 회복 경로 부재 |
| observe_wait | 0.8 | 1.3 | Judas 계산/대기 지배 |
| confront | 1.3 | 0.6 | Judas 정면 대응 없음 |
| primary_focus_attachment | 1.4 | 0.7 | Judas 이미 이탈 |
| guilt_decay_rate | 0.8 | 0.5 | Judas guilt 오래 지속 → despair 경로 |
| trust_restoration_bias | 1.2 | 0.5 | Judas 재결속 거의 불가 |

**즉 Judas 만의 "규칙"은 없다. 같은 motif engine + 다른 profile parameter 9개 조정.**

---

## 2. Judas에 없지만 필요한 것 (현재 engine 한계)

### 2.1 "계획적 배신" motif

- 현 8 motif로 cover 안 됨
- `observe_wait` 가 수동 대기 → Judas의 능동 계산과 다름
- 후보: `scheme` motif 추가 검토 (B 로드맵 Phase 2 additional motif 후보 "exploit")
- Lee 판정 필요 — 12개 제약 내 허용 가능

### 2.2 "절망/자기 파괴" 경로

- 현재는 grieve + guilt 누적으로 근사
- 명시적 despair motif 없음
- self_harm_impulse event (VG 시나리오 추가) + remorse_trigger (Judas) 가 있으나 motif mediation 부재

### 2.3 "은밀한 이탈 vs 공개적 부인" 구분

- Peter의 conceal → deny (공개)
- Judas의 conceal → withdraw/flee (은밀)
- `motif_action_priors` 의 conceal 섹션이 인물별로 다르게 표현 가능 → generic 구조 유지

---

## 3. 결론

**Judas 분류 요약:**
- **Generic 유지:** engine/ 전부 (loop.py, persona/, state_transitions.py, rubric/)
- **Content binding:** `content/judas/v3/` 전체
- **Ambiguous:** 새 event 4개 (generic naming이지만 재사용 미검증)
- **Gap:** scheme motif 부재, despair 경로 미표현

**Judas 덕에 드러난 engine 한계:**
1. observe_wait로 계획 행위 cover 한계
2. rubric이 "은밀 서사" 구분 못함
3. motif 8개가 경계 장르 (배신/회복 없는 arc) 에 부족

**진전 기록 (positive):**
- engine 수정 없이 Judas scenario 수용 ✓
- 4 new generic events 추가 (Rule #1 준수) ✓
- profile 9개 축 차이로 motif 분포 완전히 다름 ✓

---

**End of Judas分離.**
