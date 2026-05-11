# Observer Layer Real-Run Review Summary

**Date**: 2026-04-30
**Source**: `REAL_RUN_VALIDATION.md` 검증 결과
**Verdict**: **Case A — 좋음 (Observer MVP freeze 검토)**

---

## Keep (강점, 유지)

### K1. Salience detector가 event-driven turning point 자동 식별
- Real run: tick 15 = `guard_approaches` event 직후 `authority_vigilance_spike` + `cohort_split` 동시 detect
- Top 5 salient moments가 *narrative-relevant tick*과 일치
- Auto-bookmarks (`first_cohort_split` tick 4, `first_saturation_lock` tick 24)이 *navigation 도구*로 작동

### K2. Compare view가 variation 차이를 명확히 표시
- 3 seeds (peter_scarcity_baseline) — final mood split (seed_0/2: tense, seed_1: calm)
- peak_blame 0.37~0.47 분포 — single-seed sensitivity (Branch C claim)와 직접 일치

### K3. World View + narrate_world_arc combination
- 30-tick trace + 1-line prose summary가 *quick scan*에 효과적
- Lee의 "판독 효율 향상" (spec §11.3) 직접 매핑

### K4. Cohort group view의 dominant_mode + tension
- 3 groups (L1/L2/L3) 동시 추적 — 어느 cohort가 saturation/recovery/low_activity인지 즉시 visible
- Lee directive §4.3 group view 검증 충족

### K5. Replay/Jump infrastructure
- ReplayCursor + auto_bookmark_turning_points + window helpers 모두 정상 작동
- Lee가 *특정 tick / event start / bookmark*로 즉시 navigate 가능

### K6. 관찰기 ≠ 평가기 원칙 일관성
- Salience tags = *attention pointer* (no quality verdict)
- Narrative summary = *현황 묘사* (evaluative 단어 회피)
- Compare disclaimer ("어느 stream이 더 낫다는 평가 아님")

---

## Weak (약점, 국소 patch 가능)

### W1. Salience tie-break이 tick 순서에 의존
- 200 ticks 동안 top 5 salient 모두 score=3 동률 → tick 순서로 결정
- 더 fine-grained scoring (e.g., metric magnitude weight) 후보
- **단**, 현재 tie-break도 정상 작동 (earliest tick 우선) — 즉시 fix 필요는 아님

### W2. Person Arc narration이 net delta = 0인 agent에서 정보 부족
- merchant agent: fear 2.4 → 2.4 (시작=끝), narrate text "두려움은 거의 변화 없다"
- *intermediate peak* (10-15 tick에 짧은 dip) 정보가 narrate에서 손실
- *intermediate peak narrator* 후보

### W3. World narrative가 200 ticks oscillation 데이터 손실
- "비난은 최고 0.46까지 올랐고, 이 구간에서 오르고 있다" — net direction만, *waves* 안 보임
- *phase-aware narration* (calm/agitated/recovery 구간 분리) 후보

---

## Missing (없는 기능 — Lee directive 외)

### M1. MicroWorld 전용 adapter 미구현
- 현재 `demo_observer.py`에 `build_real_stream_from_anchor()` 형태로 manual mapping
- 정식 `engine/observer/microworld_adapter.py` 모듈 미생성
- 영향: 다른 anchor 사용 시 동일 mapping 코드 복제 필요
- **fix 단가**: 작음 (~100 lines), but 별도 directive 필요 (현재 forbidden_now §11 violation 안 함)

### M2. Real-time callback hook
- 현재 *post-hoc 변환만* (200 ticks run 후 history → Snapshot stream)
- *live observation* (run 중 tick마다 callback)은 미구현
- Lee directive §10 forbidden_now ("새 기능 추가보다 검증 우선")

---

## Not Useful (제거 후보, 현재 없음)

### NU. (없음 — 모든 기능이 real run에서 의미 있음 검증됨)

---

## Next Action 분기 (Lee directive §8)

### Case A (좋음) — 이번 결과
- ✅ **Observer MVP freeze 검토**
- (분기 옵션 1) Story + Observer 통합 활용
- (분기 옵션 2) Curated observation pack — Branch C asset pack v1과 결합

### Case B (일부 약함) — 적용 안 됨
- W1-W3 weakness가 *core blocker*면 적용. 현재 *모두 fine-tunable* 수준 → Case A 적용

### Case C (전반적 약함) — 적용 안 됨

---

## Lee Directive §6 Success Criteria 점검

| # | 기준 | 결과 |
|---|---|:---:|
| 1 | World View가 세계 전체 흐름을 이해하게 해 준다 | ✅ |
| 2 | Person View에서 인물 arc가 납득 가능하게 보인다 | ✅ |
| 3 | Event View에서 사건 ripple이 읽힌다 | ✅ |
| 4 | Compare View가 variation 차이를 보여준다 | ✅ |
| 5 | Salience top moments가 의미 있다 | ✅ |
| 6 | Replay / Jump가 실제 탐색 도구로 쓸 만하다 | ✅ |

**6/6 충족** = Case A.

---

## 결론

> **Observer Layer는 Phase O1-O7 + real-run validation까지 통과했다. Lee directive §6 성공 기준 6/6 모두 충족하며, 별도 directive 시까지 *MVP freeze* 권고. 다음 단계 옵션 = Story 통합 또는 Curated observation pack.**

**Versioning**: v1 (이 doc) — 2026-04-30 real-run review summary.
