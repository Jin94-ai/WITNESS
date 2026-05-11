# Candidate Curation Plan — Phase Q1-Q4

**Date**: 2026-04-30
**Source**: `docs/WITNESS_CANDIDATE_CURATION_AND_NEXT_STEPS.md` (Lee directive)
**Status**: Phase Q1-Q4 진행
**용도**: Observer-to-Story Pipeline의 candidate browsing 품질 정리 — *정리 단계*, 기능 추가 아님.

---

## 0. 핵심 목표 (Lee §0 verbatim)

> **candidate를 더 많이 뽑는 것이 아니라, 이야기로 이어질 가능성이 있는 후보를 더 잘 남기고 비슷한 후보·약한 후보·탐색용 후보를 분리하는 것.**

---

## 1. 원칙 (Lee §2)

| # | 원칙 |
|---|---|
| 1 | 새 scoring system 크게 만들지 않음. *얇은 2차 필터*만. |
| 2 | 관찰 후보 ≠ 이야기 후보 — 3 bucket으로 분리 |
| 3 | temporal diversity 우선 보정 |

**금지**:
- massive weighted ranking
- "best story" 자동 판정
- creative value score

**허용**:
- 얇은 2차 필터
- 중복/군집 정리
- 탐색 bucket 분리

---

## 2. 3 Bucket 정의 (Lee §2 원칙 2)

| Bucket | 의미 | 조건 (heuristic) |
|---|---|---|
| **A. story_ready** | 바로 render로 넘겨볼 만한 후보 | 강한 신호 + strongest lens 실체 있음 |
| **B. observation_only** | 읽을 가치는 있지만 바로 story로 가면 약한 후보 | 신호 있음 but lens 실체 부족 |
| **C. low_activity_hold** | 지금은 약하지만 tension seed가 있는 후보 | dominant_mode == low_activity AND salience_score <= 1 |

**원칙**: 후보를 버리지 않음. *무엇으로 쓸지* 분리.

---

## 3. Phase 구현 계획

### Phase Q1 — Candidate curation rules
**산출물**: `engine/observer/candidate_curation.py`

**기능**:
- `assign_use_mode(candidate, observer) -> "story_ready" | "observation_only" | "low_activity_hold"`
- `pick_strongest_lens(candidate, observer) -> "person" | "event" | "world"`
- `temporal_diversity_filter(candidates, min_gap=5) -> list[Candidate]`
- `near_duplicate_reduce(candidates, window=3, signal_overlap=0.5) -> list[(rep, related_ids)]`
- `curate_candidates(candidates, observer) -> CuratedSet`

**CuratedSet** dataclass:
- `story_ready: list[CuratedCandidate]`
- `observation_only: list[CuratedCandidate]`
- `low_activity_hold: list[CuratedCandidate]`

**CuratedCandidate** dataclass (래퍼):
- `candidate: StoryCandidate` (원본 보존)
- `use_mode: str` (3 bucket label)
- `strongest_lens: str`
- `related_candidate_ids: list[str]` (near-duplicate로 접힌 ID들)

### Phase Q2 — Recommendation refinement
**대상**: `engine/observer/candidate.py` (no API change) + packet builder

**변경**: `Recommended: yes/no` → `Use mode: story_ready/observation_only/low_activity_hold`

### Phase Q3 — Packet schema v2
**산출물**: `scripts/observer/candidate_packet.py` 업데이트

**신규 필드**:
- `use_mode: str | None`
- `strongest_lens: str | None`
- `related_candidate_ids: list[str]`

**Packet 출력 변경**:
```
[Use mode]
  story_ready / observation_only / low_activity_hold
[Strongest lens]
  person / event / world
[Related candidates] (있을 때만)
  C02_t146, C03_t147 (near-duplicate, 접힘)
```

### Phase Q4 — Validation rerun
**산출물**: `docs/observer/CANDIDATE_CURATION_VALIDATION.md`

**검증 질문** (Lee §3.4):
1. candidate 상위 목록의 temporal diversity가 좋아졌는가
2. story-ready 후보가 실제로 더 그럴듯해졌는가
3. observation-only 후보가 분리되어 browsing이 쉬워졌는가
4. low-activity 후보가 일반 리스트를 덜 오염시키는가
5. packet만 읽어도 strongest lens와 use mode가 이해되는가
6. near-duplicate 후보가 줄어드는가

---

## 4. 스코프 명시

### 포함 (Lee §4)
- temporal diversity rule
- render recommendation 보강
- low-activity bucket 분리
- packet wording 정리
- near-duplicate candidate 정리
- validation 문서 갱신

### 제외 (Lee §4)
- story quality scoring
- public browser UI
- 새 lens 추가
- observer summary 대확장
- renderer 재시작
- anchor 대규모 확장
- Branch C 추가 실험

---

## 5. 성공 기준 (Lee §7) — 4/6 이상 충족 시 성공

1. top candidate 목록의 시간적 다양성이 눈에 띄게 좋아진다
2. story-ready 후보가 실제로 더 이야기 후보처럼 보인다
3. observation-only 후보가 별도 구획으로 분리되어 읽기 쉬워진다
4. low-activity 후보가 메인 후보 목록을 덜 오염시킨다
5. packet만 읽어도 strongest lens와 use mode가 이해된다
6. near-duplicate 후보가 줄어든다

## 6. 실패 기준 (Lee §8) — 2/5 이상 시 재조정

1. temporal diversity rule 넣었는데도 cluster가 그대로다
2. story-ready 후보가 여전히 약한 person arc 중심이다
3. packet wording이 여전히 보고서 같다
4. bucket 분리했는데 실제 browsing 경험이 별 차이 없다
5. candidate curation이 또 다른 rubric처럼 비대해진다

---

## 7. ABSOLUTE 원칙

### Rule #1 (engine/ no person hardcoding)
- `engine/observer/candidate_curation.py`에 person name 없음
- 기존 candidate.py / Observer API 호환성 유지

### Rule #6 (engine API preservation)
- 기존 `extract_*_candidates` API 무수정 — *raw candidates*는 그대로
- Curation은 *추가 layer* (additive)
- 기존 `build_packet` 시그니처 보존, 새 필드는 default None

### 관찰기 ≠ 평가기 원칙
- bucket은 *분류*만, *quality verdict* 아님
- "best" / "worst" 명명 금지 — `story_ready` (사용 가능 상태) / `observation_only` (다른 용도) / `low_activity_hold` (보류)
- Human check placeholder 보존

---

## 8. 다음 단계 분기 (Lee §6)

Phase Q1-Q4 완료 후 success criteria 4+ 만족 시:
- **Step 1**: anchor 2개째 확장 (`accusation` canonical run 추천) — `ANCHOR_2_EXPANSION_PLAN.md`
- **Step 2**: Observer-based browsing pack (curated text pack)
- **Step 3**: Story Explorer 방향 검토 (anchor 2 끝난 후만)

---

**Versioning**: v1 (this plan) — 2026-04-30 Phase Q1-Q4 시작.
