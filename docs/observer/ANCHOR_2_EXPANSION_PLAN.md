# Anchor 2 Expansion Plan — Curation pipeline 일반화 검증

**Date**: 2026-04-30
**Source**: Lee directive `WITNESS_CANDIDATE_CURATION_AND_NEXT_STEPS.md` §6 Step 1
**Status**: Plan only — 별도 directive 없을 시 *대기*
**Trigger**: Phase Q1-Q4 검증 (`CANDIDATE_CURATION_VALIDATION.md`) Case A 성공 후속

---

## 0. 목적 (Lee §6 Step 1)

> 지금은 `peter_scarcity_baseline` 하나로만 증명했다.
> candidate 품질 정리가 끝나면, 그때 2번째 anchor를 붙인다.
>
> 추천: accusation canonical run
>
> 목적:
> - observer-to-story pipeline이 한 anchor 전용인지 확인
> - 같은 규칙이 다른 pressure에서도 먹히는지 확인

---

## 1. 후보 Anchor

현재 selector library (`scripts/story/selector.py`)에 있는 anchor:

| Anchor ID | Scenario | 설명 |
|---|---|---|
| `peter_scarcity_baseline` | scarcity | 현재 검증 끝 (anchor 1) |
| `vangogh_sacred_baseline` | sacred | sacred 전용 — pressure 다양성 확보 |
| `peter_scarcity_high_density` | scarcity | scarcity 변형 — diversity 부족 |
| `peter_scarcity_double` | scarcity | accusation 2개 포함 |
| `peter_scarcity_triple` | scarcity | accusation 3개 포함 |

### 1.1 추천 anchor 2 = `peter_scarcity_triple`
**이유**:
- accusation 3개 → blame_concentration / public_suspicion 활성 구간 명확
- 같은 scenario (scarcity) 안에서 다른 dynamics → curation rules의 *generalization* 검증
- 새 builder 작성 불필요 (이미 selector에 등록됨)
- Phase Q1-Q4 결과와 직접 비교 가능 (anchor 1과 같은 scenario family)

### 1.2 대안 후보
- `vangogh_sacred_baseline` — *cross-scenario* generalization 강도 높음. 다만 sacred pressure는 measurement system이 다름 (anchor 1의 scarcity와 다른 metric 강도)
- 별도 *pure accusation* canonical run 신규 작성 — 작업 단가 큼, 본 scope 초과

**권장**: anchor 2 = `peter_scarcity_triple` (작업 단가 낮음 + 직접 비교 가능).

---

## 2. 검증 가설

### H1. Curation rules가 anchor-agnostic하게 작동하는가
- `min_tick_gap=5`, `tick_window=3`, `signal_overlap=0.5` 기본값으로 같은 결과 품질
- 만약 anchor 2에서 cluster가 그대로 남으면 → threshold 재조정 필요

### H2. Bucket 분포가 anchor마다 다른가
- Anchor 1 (baseline): story_ready 5 / observation_only 0 / low_activity_hold 3
- Anchor 2 (triple): 예상 — accusation 신호 더 강해서 saturation/agitated mode 후보 증가 → story_ready ↑, low_activity_hold ↓
- *bucket 분포 차이 자체*가 anchor마다 다른 generative dynamics의 reflection

### H3. observation_only가 anchor 2에서 0 아닌 값으로 나타나는가
- Anchor 1에서 0개였지만 dynamic threshold 자체는 작동
- Anchor 2에서 *signal 있지만 lens 실체 부족* 후보가 나타날 가능성

---

## 3. 실행 단계

### Step A. selector library 확인
```python
from scripts.story.selector import get_anchor_by_id
anchor = get_anchor_by_id("peter_scarcity_triple")
```

### Step B. examples/demo_observer_story.py에 `--anchor` flag 추가
```python
python examples/demo_observer_story.py --curated --anchor peter_scarcity_triple
```

기존 default = `peter_scarcity_baseline`, flag로 override 가능.

### Step C. Same curation rules로 anchor 2 실행
- temporal_diversity_filter 기본값 (min_gap=5)
- near_duplicate_reduce 기본값 (window=3, overlap=0.5)
- *threshold 변경 없이* 결과 측정

### Step D. 비교 doc 작성
- `docs/observer/ANCHOR_2_VALIDATION.md`
- Anchor 1 vs Anchor 2 bucket 분포 비교
- near-dup reduction rate 비교
- Lee §7 성공 기준 6개 anchor 2 단독 점검

### Step E. 일반화 verdict
- **A. 일반화 성공**: anchor 2도 4+ 성공 기준 충족 → Step 2 (Observer-based browsing pack) 진행
- **B. Threshold 재조정 필요**: 일부 기준 미충족 → curation params 노출 + per-anchor config
- **C. Curation 자체 재설계**: 2/5 이상 실패 기준 발동 → 별도 directive 필요

---

## 4. 스코프

### 포함
- `--anchor <id>` flag (small)
- anchor 2 1회 실행 + ANCHOR_2_VALIDATION.md
- bucket 분포 비교
- near-dup reduction rate 비교

### 제외 (Lee §4 일관)
- 새 anchor 작성 (selector library 안의 것만 사용)
- pure accusation canonical run 신규 빌드
- curation params 자동 튜닝
- per-anchor adaptive threshold (manual override만)
- 새 lens 추가
- new bucket 추가

---

## 5. 작업 단가 견적

| Step | 단가 |
|---|---|
| A. selector 확인 | < 1 min |
| B. --anchor flag | ~10 min (CLI parsing + cache key 변경) |
| C. anchor 2 실행 | < 1 min (캐싱) |
| D. ANCHOR_2_VALIDATION.md | ~30 min |
| E. verdict | ~10 min |

**총합: 약 50분** (Phase Q1-Q4 후속).

---

## 6. ABSOLUTE 원칙

- Rule #1: anchor 2도 person hardcoding 없음 (`scripts/story/selector.py`는 builder 모음, generic)
- Rule #6: 기존 API 무수정 (Anchor expansion = additive flag only)
- 관찰기 ≠ 평가기: bucket 분류는 *분류*만, *quality verdict* 안 함

---

## 7. 다음 단계 분기 (Lee §6)

ANCHOR_2 검증 결과:

### Case A (anchor 2도 성공)
→ **Step 2** (Lee §6): Observer-based browsing pack
- top 3 story-ready + top 3 observation-only + top 3 low-activity hold
- same candidate 3-lens compare 2세트
- *해석기 없는 curated text pack*

### Case B (Threshold 재조정 필요)
→ Curation params 노출 + per-anchor override 추가
→ Step 2 진행 후에도 threshold 재점검

### Case C (Curation 자체 재설계)
→ 본 plan은 폐기, 새 directive 필요

---

## 8. 한 줄 요약

> **Phase Q1-Q4 curation rules가 anchor 1 (peter_scarcity_baseline)에서 작동했다. 다음은 같은 rules가 anchor 2 (peter_scarcity_triple, accusation 3개 포함)에서 동등하게 작동하는지 검증. 작업 단가 ~50분. Case A 성공 시 Step 2 (browsing pack) 진행.**

---

**Versioning**: v1 (this plan) — 2026-04-30 Phase Q5 (anchor 2 expansion) 대기.
