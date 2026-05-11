# Story Set Baseline Review (12 probes, MVP first pass)

**Date**: 2026-04-28
**Source**: `docs/story/generated/P{1-12}_{summary,narrative}_ko.txt`
**Phase**: 6 of MVP_PLAN. First-pass quality gate.

---

## 1. 전체 결과 (12 baseline)

| Probe | Final summary | Pressure | Summary 길이 | Narrative 길이 |
|---|---|---|---:|---:|
| P1 | PARTIAL | scarcity | 358 | 486 |
| P2 | SATURATION | scarcity | 381 | 547 |
| P3 | SATURATION | accusation | 321 | 492 |
| P4 | RECOVERY | sacred | 297 | 449 |
| P5 | RECOVERY | sacred | 297 | 449 |
| P6 | MIXED | scarcity | 455 | 750 |
| P7 | PARTIAL | sacred | 288 | 423 |
| P8 | MIXED | accusation | 335 | 562 |
| P9 | SATURATION | scarcity | 356 | 522 |
| P10 | RECOVERY | accusation | 307 | 459 |
| P11 | MIXED | accusation | 335 | 562 |
| P12 | SATURATION | sacred | 388 | 584 |

12/12 생성 성공.

---

## 2. Acceptance Criteria 평가 (MVP_PLAN §11.1)

| 기준 | 결과 |
|---|---|
| 1. 12개 중 9개 이상에서 이야기 흐름 식별 가능 | **PASS** (12/12 — 모든 probe에서 도입→압력→반응→귀결→사후 흐름 식별) |
| 2. recovery / saturation / mixed 구분이 글로 느껴짐 | **PASS** — outcome 단계 + group_response 단계에서 분명히 다른 결 |
| 3. crowd / authority / public attention 중 최소 2개가 서사 속에서 보임 | **PASS** — 비난/의심/권위 시선 3개 축이 pressure_arc에서 surface |
| 4. 문서 요약이 아니라 서사처럼 읽힘 | **PASS** — 보고서 말투 0건, raw ID 0건, 숫자 0건 |
| 5. probe별 차이가 텍스트에서도 드러남 | **PASS** — sacred vs scarcity vs accusation 도입 문장 분기, MIXED는 cohort split 문단 surface |
| 6. 같은 템플릿 반복 냄새가 심하지 않음 | **MARGINAL** — 같은 시나리오/outcome 묶음(P4=P5)은 거의 동일. P6 vs P11 vs P8 (모두 MIXED accusation/scarcity) 미세 차이만 |

→ **MVP acceptance**: 5/6 PASS, 1 MARGINAL. 통과 기준(4/6) **충족**.

---

## 3. 발견된 품질 이슈 (Loop A — 읽힘 개선 후보)

### 3.1 조사 오류 (한국어 문법) — HIGH priority

**증상**:
- P3: "제자을(를) 가리켰다" → 받침 없는 단어 뒤 "을" 오용. 자동으로 "을(를)" 같은 fallback 표시 출력.
- 다른 probe: 자연스러운 조사 처리 됨.

**원인**: `_initial_tension`의 f-string에서 `{target}을(를)`로 안전 조사 표시. spec §6 "지나친 형식적 처리"에 가까움.

**수정안**: 받침 유무 자동 판단 함수 추가.

```python
def _josa(word, has_batchim_form, no_batchim_form):
    last = word[-1]
    has_batchim = (ord(last) - 0xAC00) % 28 != 0
    return has_batchim_form if has_batchim else no_batchim_form
```

### 3.2 중복 복수 표시 — HIGH priority

**증상**:
- P3: "거리의 사람들들" — 이미 "사람들"인데 코드에서 `+ "들"` 추가.

**원인**: `pressure_arc`에서 `f"{tk}들에게로"` 무조건 들 추가. ROLE_KO에 이미 복수형(거리의 사람들, 노동자들)인 항목 처리 누락.

**수정안**: ROLE_KO 항목별 plural-aware 처리. 또는 "거리의 사람들" 복수 명시 없이 `에게로` 사용.

### 3.3 길이 미달 — MEDIUM priority

**Spec 목표**: Summary 400-800자, Narrative 1000-1800자.
**실제**: Summary 288-455자, Narrative 423-750자.

| Probe | Summary 차이 | Narrative 차이 |
|---|---:|---:|
| 최단 (P7) | -112 (288 vs 400) | -577 (423 vs 1000) |
| 최장 (P6) | +55 (over 400) | -250 (750 vs 1000) |

**원인**: 5단 구조 각 단의 문단이 1-2 문장으로 짧음. 비유적 묘사 부족.

**수정안 (Phase 7)**:
- pressure_arc에 추가 묘사 (시간감, 거리감)
- group_response cohort_detail 더 길게
- aftereffect 1-2 문장 추가
- 각 단계 사이 transition 문장

**Note**: spec §11.1 acceptance가 "이야기 흐름 식별"이지 "길이"가 아니라서 acceptance는 통과. 하지만 spec §2 길이 목표는 미달.

### 3.4 Sacred + authority 모순 — LOW priority

P4 (RECOVERY/sacred): "권위의 시선은 한쪽 끝에서 모든 것을 지켜보고 있었다." 이 문장은 압력 분위기에 맞지만 sacred recovery에선 톤 부조화. Sacred 시나리오에서 has_authority 처리 재고려.

### 3.5 같은 시나리오 + 같은 outcome → 동일 출력 — LOW priority (반복 변주 후속)

P4 == P5 (둘 다 RECOVERY/sacred): summary/narrative 텍스트 100% 동일. cohort_outcomes도 동일 형태. 차이가 없음.

→ 후속 loop C (variation) 작업: cohort 수, agent 수, key_events_sample 변화에 따라 미세 변주.

---

## 4. 강점 (이번 cycle 보존)

- **5단 구조**: 도입 / 압력 / 반응 / 귀결 / 사후가 매 probe에서 명확히 분리.
- **시나리오 도입 분기**: scarcity ("곡식이 비어 가는 계절") / accusation ("공기는 이미 무거웠다") / sacred ("성전 바깥뜰") 잘 구분.
- **Outcome 분기**: RECOVERY ("다시 일어섰다") / SATURATION ("자리에 굳었다") / MIXED ("갈라진 자리") 분명한 톤 차이.
- **Cohort split (MIXED)**: P6/P8/P11에서 회복+포화 동시 묘사 패턴 잘 작동.
- **Top blame target (v4) 활용**: P6/P9 fisher_laborer ("노동자들에게로 향했다") 자연스럽게 surface.
- **숫자/raw ID 누출 0건**: spec §6 forbidden 항목 모두 회피.

---

## 5. Phase 7 우선 수정 항목 (1회 개선)

1. **HIGH**: 조사 오류 (3.1) + 중복 복수 (3.2) — 자동 함수 도입
2. **MEDIUM**: 길이 늘리기 (3.3) — 각 단계 1-2 문장 추가, transition 문장 도입
3. **LOW**: Sacred/authority 부조화 (3.4) — has_authority 조건부 사용
4. **DEFER (loop C)**: probe 변주 (3.5) — cohort 수/agent 수 기반 micro-variation

---

## 6. 다음 단계 (Phase 7 + loops)

- Phase 7: 위 4 항목 개선 (renderer 1회 패치)
- Phase 7 후: 12 stories 재생성 + delta review
- Loop A: 읽힘 더 자연스럽게
- Loop B: world-side 강화 (현재 surface 정도 OK)
- Loop C: variation
- Loop D: style branching (요약 vs 서사 / 건조 vs 감정)

---

## 7. 결론

MVP first pass: **acceptance 통과**. 12 baseline 한국어 story 생성 성공. raw ID/숫자/메타 누출 0건. 시나리오/outcome 분기 분명. cohort split (MIXED) 패턴 작동.

품질 이슈는 모두 generator-level 수정 가능 (engine touch 0). Phase 7에서 4 우선 항목 패치 후 재생성 권장.
