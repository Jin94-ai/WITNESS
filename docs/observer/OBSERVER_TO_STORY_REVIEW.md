# Observer → Story Pipeline — Review Summary

**Date**: 2026-04-30
**Source**: `OBSERVER_TO_STORY_VALIDATION.md` 검증 결과
**Verdict**: **Case A — 성공** (Pipeline freeze 검토)

---

## Keep (강점, 유지)

### K1. 4-category extractor가 다양한 lens 후보 생성
- `extract_story_candidates` (mixed top 5)
- `extract_world_candidates` (world-heavy top 3)
- `extract_person_candidates` (person-arc top 3)
- `extract_event_candidates` (event-ripple top 3)
- → 14 candidates total in canonical run, 각 category가 *다른 angle* 제공

### K2. Packet 6 fields 완전 자동화
- A. Basic / B. Why / C. Lens summaries / D. Story potential / E. Render link / F. Human check
- 시스템은 *fill*만, *판정*은 placeholder (☐ keep / ☐ interesting / ☐ revise / ☐ skip)
- Lee directive §7 verbatim 준수

### K3. Multi-lens 차이가 명확
- Person lens = 개인 감정 변화
- Event lens = 사건 ripple (active span + agents present)
- World lens = world-level dynamics (mood + metrics)
- 같은 tick 142 = 3 lens가 *완전히 다른 측면* 표현

### K4. Render Recommendation의 lens 매핑
- candidate_type → lens 자동:
  - person → person
  - event → event
  - world → world
  - mixed → world (cohort overview)
- salience_score >= 2 시 render_recommended=True

### K5. "관찰기 ≠ 평가기" 원칙 보존
- Candidate = *추천*만
- Quality verdict 자동화 없음
- Demo 출력 마지막 disclaimer ("Candidate = 추천만, 판정 아님")
- format_packet_text Human check section = ☐ checkbox (caller fills)

### K6. Existing Observer Layer 무수정
- ABSOLUTE Rule #6 (engine API preservation) 준수
- Candidate Extractor는 *Observer 위 layer* (additive)
- engine/observer/core.py / salience.py / replay.py 모두 무수정

### K7. Demo entry 단일 entry point
- `python examples/demo_observer_story.py` (default = list)
- `--packet <id>` / `--render-story <id>` / `--compare-lenses <id>`
- 4 modes 모두 자동 캐싱 (Observer 200 ticks 1회 빌드 후 재사용)

---

## Weak (약점, 국소 patch 가능)

### W1. Person arc narration이 짧은 window에서 약함
- tick_range = (tick±2) 기본 5 ticks → "세 감정 모두 큰 변화 없이 안정적으로 흘렀다" 자주
- net delta 0인 agent에서 정보 부족 (real-run validation L40 §8.1과 동일 한계)
- *intermediate peak* 강조 narrator 추가 후보 (Cycle 8+ 영역, forbidden_now)

### W2. Pressure inference이 heuristic
- active_events keyword 매칭 + world metric threshold
- 정확하지만 *anchor metadata*에서 직접 가져오기 더 깔끔
- 작업 단가 작음, 별도 directive 시 처리 가능

### W3. Late-run tick cluster 후보 (142, 146, 147)
- 인접 tick 중복 후보 (top 5 salient에서 4개가 142-147 cluster)
- *temporal diversity*를 위해 *min tick gap* 옵션 추가 가능
- 현재는 *unique tick guarantee*만 (set-based dedup)

---

## Missing (없는 기능 — Lee directive 외)

### M1. Full IR + render_story_ko 연결
- 현재 render link = light narrative (narrate_*) + detail view
- *Probe-shaped IR* 변환은 Phase P6+ 영역
- forbidden_now: "renderer 재시작" — 별도 directive 필요

### M2. Anchor 자동 변경 옵션
- Demo는 peter_scarcity_baseline 고정
- 다른 anchor (peter_scarcity_double / triple / vangogh_sacred 등) 시도 시 코드 수정 필요
- *demo CLI에 --anchor flag 추가* 후보 (작은 단가)

---

## Not Useful (제거 후보, 현재 없음)

### NU. (없음 — 모든 함수가 의미 있게 사용됨)

---

## 다음 단계 분기 (Lee directive §13)

### Case A (성공) — 이번 결과
- ✅ **Observer → Story Pipeline freeze 검토**
- (옵션 1) Story Explorer / Browser 방향 검토 (forbidden_now §14 — public UI 금지)
- (옵션 2) Curated observation pack — Branch C asset pack v1과 결합 (작은 단가)
- (옵션 3) full IR + render_story_ko 연결 (Phase P6, *별도 directive 필요*)

### Case B / Case C — 적용 안 됨

---

## Lee directive §11 success criteria 재점검

| # | 기준 | 결과 |
|---|---|:---:|
| 1 | candidate 3-5개 story-worthy | ✅ 14 candidates (5+3+3+3) |
| 2 | multi-lens 차이 느껴짐 | ✅ |
| 3 | packet만 읽어도 이해 | ✅ |
| 4 | 최소 2 candidate render 연결 | ✅ (모든 14 candidate에 lens 매핑) |
| 5 | observer가 story selection 앞단으로 유용 | ✅ |
| 6 | quality verdict 안 하면서 탐색 효율 향상 | ✅ |

**6/6 충족** = **Case A**.

---

## 결론

> **Observer → Story Candidate Pipeline (Phase P1-P5) 구축 + 검증 완료. Lee directive §11 success criteria 6/6 모두 충족 → Case A (성공). 별도 directive 시까지 *Pipeline freeze* 권고. 다음 단계 옵션 = Story Explorer 방향 검토 또는 curated observation pack 결합.**

**Observer Layer 진화 단계 누적**:
- Phase O1-O7: snapshot / lens / replay / compare / narrative
- Real-run validation: 6/6 충족
- **Phase P1-P5 (Observer → Story): 6/6 충족**

→ Observer Layer는 이제 *단순 관찰 도구*가 아니라 *story selection 앞단*으로 작동.

**Versioning**: v1 (이 doc) — 2026-04-30 review summary.
