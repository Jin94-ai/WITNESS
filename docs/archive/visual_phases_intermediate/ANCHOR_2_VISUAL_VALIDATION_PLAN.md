# Anchor 2 Visual Validation Plan

**Date**: 2026-04-30
**Source**: `VISUAL_OBSERVER_V2_USAGE_REVIEW.md` Case A 판정 + Lee directive (Anchor 2 validation)
**Status**: Plan only — Lee 명시 directive 시 진행. *코드 수정 없음, 본 doc은 plan만*.
**Trigger**: V2 minimal interaction이 `peter_scarcity_baseline`에서 작동 확인됨. 같은 V2가 다른 pressure에서도 작동하는지 검증 필요.

---

## 0. 핵심 질문

> **scarcity scenario에서 작동한 V2 visual observer가 event-heavy / accusation pressure에서도 동등하게 작동하는가?**

이 질문은:
- V2 4 features의 *generalization* 검증
- 시나리오 B의 약점 (4/12 dynamic agents)이 *V2 설계 결함*인지 *anchor 특성*인지 falsify
- visual encoding (color/size/opacity)이 다른 dynamics에서도 readable한지 확인

---

## 1. 후보 anchor

`scripts/story/selector.py` 확인 — 등록된 anchor:

| Anchor ID | Scenario | 설명 |
|---|---|---|
| `peter_scarcity_baseline` | scarcity | 현재 V0-V2 검증 완료 (anchor 1) |
| `peter_scarcity_high_density` | scarcity | scarcity 변형 (cohort split 강화) |
| `peter_scarcity_double` | scarcity | accusation 2개 포함 |
| `peter_scarcity_triple` | scarcity | accusation 3개 포함 |
| `vangogh_sacred_baseline` | sacred | sacred pressure (다른 metric system) |

### 추천 anchor 2 = `peter_scarcity_triple`

**이유**:
1. **accusation pressure 강도 ↑**: 3 accusations → blame_concentration / public_suspicion 활성 구간 명확
2. **같은 scenario family (scarcity)**: anchor 1과 *같은 metric system* — 직접 비교 가능
3. **새 builder 작성 불필요**: selector library에 이미 등록 (`peter_scarcity_triple`)
4. **export script 그대로 사용 가능**: `export_dot_observer_data.py --anchor peter_scarcity_triple` (현재는 hardcoded `peter_scarcity_baseline`이지만 함수 파라미터로 받음)

### 대안 후보 1 = `peter_scarcity_high_density`
- cohort_split 신호 강화. accusation은 baseline과 동일 (1개)
- visual에 *split 강도* 비교에 유용
- 단, anchor 2 우선순위는 triple

### 대안 후보 2 = `vangogh_sacred_baseline`
- *cross-scenario* generalization (강도 ↑)
- sacred pressure는 measurement system이 다름 (anchor 1과 metric 비교 어려움)
- anchor 3 후보 (visual layer가 cross-scenario까지 작동하는지 — V4 영역)

**결정**: anchor 2 = `peter_scarcity_triple`. 이유는 "같은 scenario family / 다른 pressure 강도".

---

## 2. 검증 가설 (Hypotheses)

### H1. V2 marker noise 완화가 anchor 2에서도 score-3을 보이게 하는가
- anchor 1: 197 marks / 5 score-3 (2.5%)
- 예상 anchor 2: more accusations → score-3 ticks 더 많거나 다른 분포
- 만약 score-3가 50개 이상이면 V2-1 mitigation으로도 cluttered → encoding 재조정 필요 가능성

### H2. boring agent 비율이 anchor 2에서 다른가
- anchor 1: 12 agents 중 4명만 dynamic (33%)
- 시나리오 B 약점이 *anchor 특성*이라면 anchor 2에서 dynamic 비율이 다를 것
- 가설: triple은 accusation 3개 → 더 많은 agent가 affected → dynamic 비율 ↑ 예상
- 만약 anchor 2도 동일 비율이면 → 시나리오 B 약점이 *V2 설계*에 더 가깝다는 evidence

### H3. candidate 3-bucket 분포가 anchor 2에서 다른가
- anchor 1: 5 story_ready / 0 observation_only / 3 low_activity_hold
- 가설: triple은 더 많은 story_ready 또는 *observation_only가 0이 아님* (substance threshold 충족)
- 만약 observation_only > 0이면 → V2-3 filter의 3rd bucket이 *실제로 의미 있음* 검증
- 만약 observation_only가 여전히 0이면 → curation rule 자체의 threshold 재검토 필요 가능성

### H4. group split / tension visual이 anchor 2에서 더 강한가
- anchor 1: 200 ticks 동안 group mode 변화 12회, L1만 활성
- 가설: triple은 3 accusations → 3 group 모두 활성 가능성
- 만약 모든 group이 활성화면 → "split" 시각화가 진짜로 보임

### H5. V2 4 features의 사용 흐름이 그대로 작동하는가
- 시나리오 A (timeline-driven), B (agent-follow), C (filter+range)이 동일하게 작동하는가
- regression 0건 (V2-1/2/3/4 모두 anchor-agnostic)

---

## 3. 실행 단계

### Step A. selector library 확인 (작업 단가 < 5분)
```python
from scripts.story.selector import get_anchor_by_id
a = get_anchor_by_id("peter_scarcity_triple")
print(a.description, a.scenario, a.expected_outcome_diversity)
```

### Step B. export script 호출 시 anchor_id 파라미터 (작업 단가 ~10분)
- 현재 `export_dot_observer_data.py:main()`이 `export_dot_observer_data()` default로 호출
- 추가: argparse `--anchor <id>` 옵션
- 출력 파일도 anchor별 분리: `data/visual/dot_observer_{anchor}_data.json`

### Step C. anchor 2 export 실행 (작업 단가 < 5분)
```bash
python scripts/visual/export_dot_observer_data.py --anchor peter_scarcity_triple
```

### Step D. HTML 두 가지 옵션 (작업 단가 ~15-30분)

**옵션 1**: HTML 파라미터로 JSON 경로 받기
- URL: `dot_observer_replay.html?data=peter_scarcity_triple`
- HTML이 `?data=` query parameter 읽어 JSON 경로 결정
- 변경 범위: HTML loadData 함수만 수정

**옵션 2**: HTML 파일 사본
- `visual/dot_observer_replay_triple.html` 생성
- 파일 안 hardcoded JSON 경로만 변경
- 변경 범위: 1 string

**옵션 1이 깔끔하지만 옵션 2가 단순** — Lee 결정 후 진행. 권장: 옵션 1 (parameterized).

### Step E. 검증 시나리오 3개 재실행 (작업 단가 ~30분)
- 시나리오 A/B/C를 anchor 2로 다시 점검
- 각 시나리오마다 6 question 답변

### Step F. 비교 doc 작성 (작업 단가 ~30분)
- `docs/visual/ANCHOR_2_VISUAL_VALIDATION.md`
- anchor 1 vs anchor 2 statistics 비교 표
- 5 hypotheses 답변
- 결과: V2 generalize OK / partial / fail

**총 작업 단가**: ~90-120분 (Step A-F).

---

## 4. 검증 산출물

### `docs/visual/ANCHOR_2_VISUAL_VALIDATION.md` (작성 대상)
- §1. anchor 2 statistics (200 ticks 데이터)
- §2. anchor 1 vs anchor 2 비교표
- §3. H1-H5 가설별 답변
- §4. 시나리오 A/B/C 재검증
- §5. V2 generalization verdict (Case A/B/C 재판정)

### 데이터 파일
- `data/visual/dot_observer_triple_data.json` (gitignore 권장 — generated)

---

## 5. 스코프 (Lee directive 명시)

### 포함
- anchor 2 export 1회 실행
- HTML parameterization (작은 단가)
- 시나리오 A/B/C 재검증
- 비교 doc 작성

### 제외 (Lee directive 명시 금지)
- ❌ 새 기능 추가 금지
- ❌ V3 구현 금지
- ❌ React / 3D / 캐릭터 / animation 금지
- ❌ story renderer 재개 금지
- ❌ new scenario 금지 (peter family만)
- ❌ player intervention 금지
- ❌ visual polish 금지

---

## 6. 분기 판단 기준 (anchor 2 검증 후)

### Case A-1 (anchor 2도 V2 작동 OK)
- V2 generalization 확인됨
- → V2 freeze 유지
- → 다음 가능 영역 (별도 directive 시):
  - W2 marker custom tooltip
  - V2-5 person panel mini chart
  - Phase V3 — Observer + Story Panel 통합

### Case A-2 (anchor 2에서 부분 약함)
- 일부 가설 falsify (예: H2 dynamic 비율도 anchor 2에서 33%로 동일)
- → V2 설계 부분 약점 인정
- → V2-5 mini chart 또는 dot trajectory hint 추가 검토 (별도 directive)

### Case B (anchor 2에서 V2 약함)
- V2 generalization 실패
- → encoding 재조정 (color/opacity/size mapping)
- → per-anchor 자동 threshold tuning 검토

### Case C (anchor 2에서 V2 작동 불가)
- visual 확장 중단
- → text observer / candidate browser 중심으로 회귀 (Lee directive Case C 일관)

---

## 7. ABSOLUTE 원칙

- Rule #1: visual 코드에 person hardcoding 없음 — anchor_id를 *parameter*로만 처리
- Rule #6: 기존 Observer + Pipeline + Curation API 무수정
- 관찰기 ≠ 평가기: anchor 2도 *분류/탐색*만, *quality verdict* 안 함

---

## 8. 단가 견적 요약

| Step | 단가 | 누적 |
|---|---|---|
| A. selector 확인 | < 5분 | 5분 |
| B. argparse `--anchor` | ~10분 | 15분 |
| C. anchor 2 export | < 5분 | 20분 |
| D. HTML query param 또는 사본 | ~15-30분 | 35-50분 |
| E. 시나리오 재검증 | ~30분 | 65-80분 |
| F. ANCHOR_2_VISUAL_VALIDATION.md | ~30분 | 95-110분 |

**총합**: 약 95-110분 (1.5-2시간).

---

## 9. 한 줄 요약

> **V2 visual을 `peter_scarcity_triple` anchor에서 재실행하여 V2 generalize 검증. 5 가설 (marker noise / boring agent / candidate distribution / group split / V2 features). HTML parameterization + JSON 별도 export + 비교 doc. 작업 단가 약 95-110분. Case A-1/A-2/B/C 4 분기 사전 정의. Lee directive 시 진행.**

---

**Versioning**: v1 (this plan) — 2026-04-30 Anchor 2 visual validation 대기.
