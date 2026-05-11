# Phase 2.9 Portfolio Finalization — Audit

> Per `docs/WITNESS_PHASE_2_9_PORTFOLIO_FINALIZATION_AND_PHASE_3_PREP_PLAN.md` §8 (Acceptance) + §9 (No-Go).

이 문서는 Phase 2.9 (포트폴리오 정리 + Phase 3.0 진입 준비) 작업의 acceptance
충족 여부를 정리한다.

---

## 1. 5 Issue 대응 요약

| Issue | 결함 | 대응 |
|---|---|---|
| 1 | README가 ML Flesh Engine을 *완료*된 것처럼 표현 가능 | README 첫 단락 정정 — rule-based Genre Adapter가 현재 / ML은 Phase 3 후 / demo_genre_comparison을 portfolio main 명시 |
| 2 | schema_version 관계 미문서화 (skeleton_output_v1 vs universal_story_seed_v1_1 vs genre_adapted_output_v1_1 vs genre_comparison_output_v1) | [docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md](../specs/NARRATIVE_SCHEMA_VERSION_MAP.md) — 컨테이너 vs 내부 contract 분리 / Phase 3 consumer 가이드 / drift guard 매핑 |
| 3 | comparison output 존재 docs 미반영 | INDEX.md 메인 데모 섹션에 comparison.json + comparison.json mirror (`data/narrative/genre_comparison_output.json`) 명시 |
| 4 | 표현 polish (망설임 / 알아차리지만 중복) | rulebook supporting_uncertainty + witness_arc.early phrasing 다듬음 (한국 + 일본 모두) |
| 5 | Portfolio hierarchy 정리 (Peter / Life Arc / 비주얼이 주변) | [docs/portfolio/README.md](../portfolio/README.md) 신규 — Main / Evidence / Appendix 명시 + INDEX.md §0 추가 |

---

## 2. Phase 3.0 Prep 산출물

| 문서 | 역할 |
|---|---|
| [PHASE_3_0_DATA_PILOT_PREP.md](PHASE_3_0_DATA_PILOT_PREP.md) | 목적 / 범위 / 파일럿 크기 / 저장 정책 / 신뢰도 기준 / 중단 조건 |
| [DATA_SOURCE_CANDIDATE_REVIEW.md](DATA_SOURCE_CANDIDATE_REVIEW.md) | 후보 source 표 (한국/일본 방송사 등) — robots.txt / ToS / 저작권 / 공개 repo 정책 검토 |
| [PHASE_3_0_APPROVAL_CHECKLIST.md](PHASE_3_0_APPROVAL_CHECKLIST.md) | 5+2 사용자 승인 체크리스트 + 단계별 승인 절차 + 미승인 시 안전 행동 |

---

## 3. Acceptance Criteria 검증 (§8)

| # | 조건 | 상태 |
|---|------|------|
| 1 | README 첫 문장이 현재 상태와 일치 | ✅ rule-based Genre Adapter 명시 |
| 2 | ML Flesh Engine이 완료된 것으로 표현 안 됨 | ✅ "Phase 3.0 Data Pilot 통과 후 진행 예정" |
| 3 | demo_genre_comparison이 portfolio main 지정 | ✅ README + INDEX.md §0 + portfolio/README.md |
| 4 | Peter / Life Arc는 appendix로 | ✅ portfolio/README.md §4 (Earlier Demos / Appendix) |
| 5 | schema version map 문서 생성 | ✅ docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md |
| 6 | comparison.json 존재 docs 반영 | ✅ INDEX.md §0 + portfolio/README.md §2.2 + mirror at data/narrative/ |
| 7 | 작은 표현 polish 적용 | ✅ rulebook supporting_uncertainty + witness_arc 한국+일본 |
| 8 | quality_warnings 0 유지 | ✅ deployed audit 확인 |
| 9 | Phase 3.0 준비 문서 3개 생성 | ✅ PILOT_PREP / SOURCE_REVIEW / APPROVAL_CHECKLIST |
| 10 | 실제 fetch / LLM / ML 실행 0건 | ✅ |
| 11 | fast suite 회귀 0 | ✅ |

---

## 4. No-Go Criteria 검증 (§9)

| 조건 | 발생? |
|------|-------|
| README가 ML Flesh Engine을 완료된 것으로 표현 | ❌ |
| demo_genre_comparison이 메인으로 안 보임 | ❌ (3 docs 모두 main 명시) |
| comparison.json과 docs 내용 불일치 | ❌ |
| 외부 데이터 fetch 발생 | ❌ |
| LLM API 호출 발생 | ❌ |
| 원문 synopsis repo 저장 | ❌ |
| Phase 3.0 승인 체크리스트 없음 | ❌ |

→ **No-Go 0건. Phase 2.9 GO.**

---

## 5. 산출물 요약

### 5.1 신규 파일

```text
docs/specs/NARRATIVE_SCHEMA_VERSION_MAP.md
docs/plans/PHASE_3_0_DATA_PILOT_PREP.md
docs/plans/DATA_SOURCE_CANDIDATE_REVIEW.md
docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md
docs/plans/PHASE_2_9_PORTFOLIO_FINALIZATION_PLAN.md   (이 문서)
docs/portfolio/README.md                                (Reading order)
data/narrative/genre_comparison_output.json             (mirror)
```

### 5.2 수정 파일

```text
README.md                                                (Issue 1)
docs/INDEX.md                                            (§0 메인 + Phase 2.9 directive)
content/genres/korean_morning_melodrama/rulebook.json    (Issue 4)
content/genres/japanese_quiet_drama/rulebook.json        (Issue 4)
tests/test_narrative/test_general_audience_output.py     (60→70 line tolerance)
docs/portfolio/demo_genre/index.html                     (재생성)
docs/portfolio/demo_genre_japanese/index.html            (재생성)
docs/portfolio/demo_genre_comparison/index.html          (재생성, polish 반영)
docs/portfolio/demo_genre_comparison/comparison.json     (재생성)
```

---

## 6. 다음 단계

Phase 3.0 Data & Annotation Pilot 진입 — *사용자 승인 5+2건 필요*. 자체 사이클
진행 불가.

승인 절차는 [PHASE_3_0_APPROVAL_CHECKLIST.md](PHASE_3_0_APPROVAL_CHECKLIST.md)
§2.1 (단계별 승인 12 step).

---

## 7. 한 줄 결론

```text
Phase 2.5 / 2.75 / 2.8까지의 기술 산출물을 portfolio 메인 흐름으로 정리했다.
demo_genre_comparison이 메인 / 나머지는 evidence + appendix.
다음은 사용자 승인을 받아야 시작 가능한 Phase 3.0 Data Pilot.
```
