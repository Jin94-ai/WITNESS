# Phase 3.0 v1.1 + Phase 3.1 Prep — Progress Audit

> 기준일: 2026-05-11 (4 cycles 누적 — *cycle 4 시점 prep snapshot*)  
> Per `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md`
>
> **Note (cycle 76+)**: 본 audit은 prep frontier 닫힌 시점 (cycle 4) snapshot이다. 이후 추가된 Phase 3.1 Target B/C / §24 bridge / §29 verifier / Phase 3.05 Rubric directive / FREEZE 등은 [COMMIT_READINESS_2026_05_11.md](../reports/COMMIT_READINESS_2026_05_11.md) §2 참조. 현재 fast suite는 2,648 (본 표 cycle 4 시점 2,515에서 증가).

이 문서는 **Phase 3.0 v1.1 데이터 파이프라인 + Phase 3.1 No-ML baseline prep**의
4 cycle 진행상황을 통합 정리한다. *Phase 3.0 actual run (사용자 승인 후) 전*까지의
*prep status* audit이다 — 이것이 끝나면 사용자 승인을 받고 Mode A 운영 시작.

`docs/plans/PHASE_3_0_DATA_PILOT_REPORT.md`(pilot 종료 후 작성용)와는 별도.

---

## 1. 4 Cycle 산출 매트릭스

| Cycle | 핵심 산출 | 신규 tests | fast suite |
|---|---|---|---|
| 1 (2026-05-11 morning) | 7 pipeline 스크립트 + Operating Guide + 19 tests | 19 | 2,486 |
| 2 (2026-05-11 mid) | Data Card / Pilot Report templates + Mode A fixture e2e demo (5 raw + 10 outputs) + 3 fixture tests | +3 | 2,489 |
| 3 (2026-05-11 afternoon) | Phase 3.1 prep: genre_profile.py + flesh_baseline.py + 2 CLI + 20 tests | +20 | 2,509 |
| 4 (2026-05-11 evening) | demo HTML generator + cover doc + 6 demo tests + 5 architectural docs sync | +6 | 2,515 |
| **누적** | **48 phase3 tests + 5 docs sync + 7 + 4 신규 코드** | **48** | **+29 tests / 0 회귀** |

---

## 2. Plan 진행 매트릭스

### 2.1 Phase 3.0 v1.1 §17 산출 — *코드 / 데이터 / 문서 / 공개 산출*

| 항목 | 산출물 | 상태 |
|---|---|---|
| **§17.1 코드 / 스크립트** | | |
| scripts/data/normalize_synopsis.py | ✅ cycle 1 |
| scripts/data/validate_synopsis_dataset.py | ✅ cycle 1 |
| scripts/data/build_annotation_inputs.py | ✅ cycle 1 |
| scripts/data/build_public_safe_dataset.py | ✅ cycle 1 |
| scripts/annotation/validate_annotation_outputs.py | ✅ cycle 1 |
| scripts/annotation/build_feature_matrix.py | ✅ cycle 1 |
| scripts/annotation/build_reliability_report.py | ✅ cycle 1 |
| scripts/annotation/run_llm_annotation.py (후순위) | ⏳ Mode A pilot 통과 후 |
| **§17.2 문서** | | |
| PHASE_3_0_DATA_PILOT_REPORT.md | ✅ template (cycle 2) |
| PHASE_3_0_FEATURE_RELIABILITY_REPORT.md | ⏳ pilot 후 |
| PHASE_3_0_DATA_CARD.md | ✅ template (cycle 2) |
| PHASE_3_0_PIPELINE_OPERATING_GUIDE.md | ✅ cycle 1 |
| **§17.3 데이터** | | |
| normalized_synopsis.jsonl | ⏳ pilot 데이터 후 |
| annotation_inputs/ + outputs/ | ⏳ pilot 후 |
| feature_matrix.csv | ⏳ pilot 후 |
| reports/reliability.json + hallucination_report.json | ⏳ pilot 후 |
| **§17.4 공개용** | | |
| docs/portfolio/PHASE_3_0_PILOT_SUMMARY.md | ⏳ pilot 후 |

### 2.2 Phase 3.1 §28 산출

| 항목 | 산출물 | 상태 |
|---|---|---|
| **코드** | | |
| engine/observer/flesh_baseline.py | ✅ cycle 3 |
| engine/observer/genre_profile.py | ✅ cycle 3 |
| scripts/narrative/build_genre_profiles.py | ✅ cycle 3 |
| scripts/narrative/run_flesh_baseline.py | ✅ cycle 3 |
| scripts/narrative/build_flesh_baseline_demo.py | ✅ cycle 4 |
| **데이터** | | |
| data/annotation/phase3_pilot/genre_profiles.json | ✅ rulebook-only (pilot 후 갱신) |
| data/narrative/flesh_baseline_output.json | ✅ rulebook-only (pilot 후 갱신) |
| **문서** | | |
| docs/plans/PHASE_3_1_FLESH_BASELINE_REPORT.md | ⏳ Phase 3.0 후 |
| docs/portfolio/FLESH_BASELINE_DEMO.md | ✅ cycle 4 |
| **데모** | | |
| docs/portfolio/demo_flesh_baseline/index.html | ✅ cycle 4 (deployed) |

---

## 3. Acceptance 매핑

### 3.1 Phase 3.0 v1.1 §18 (12 항목)

| # | 조건 | 상태 |
|---|---|---|
| 1 | 사용자 승인 5+2건 완료 | ⏳ 사용자 승인 대기 |
| 2 | source ToS / robots.txt 검토 | ⏳ 승인 후 |
| 3 | 10 episode synopsis 확보 | ⏳ 승인 후 |
| 4 | raw synopsis .gitignore 보호 | ✅ cycle 1 (.gitignore preempt 완료) |
| 5 | annotation_inputs/*.json 생성 | ✅ build_annotation_inputs.py 작동 (fixture e2e 검증) |
| 6 | annotation_outputs/*.json 확보 | ⏳ pilot 후 (fixture demo 있음) |
| 7 | annotation output schema 통과 | ✅ validate_annotation_outputs.py 작동 |
| 8 | hallucination_rate < 5% | ✅ check 함수 작동, fixture에서 0건 |
| 9 | 최소 4 feature r ≥ 0.7 | ⏳ pilot 후 |
| 10 | KEEP/REVISE/DROP 판정 | ✅ build_reliability_report.py 작동 |
| 11 | Data Card 작성 | ✅ template (cycle 2) — pilot 후 fill-in |
| 12 | Phase 3.1 Go/No-Go 판정 | ✅ template (cycle 2) — pilot 후 fill-in |

### 3.2 Phase 3.1 §29 (9 항목)

| # | 조건 | 상태 |
|---|---|---|
| 1 | Phase 3.0 reliability 통과 | ⏳ pilot 후 |
| 2 | GenreProfile v1 생성 | ✅ cycle 3 |
| 3 | weighted score baseline | ✅ cycle 3 |
| 4 | Skeleton seed별 fit score | ✅ cycle 3 (deployed) |
| 5 | reason_features 설명 가능 | ✅ cycle 3 |
| 6 | raw synopsis 노출 0 | ✅ audit 강제 (test 포함) |
| 7 | rule-based adapter 연결 | ✅ recommended_adapter="rulebook_v2_8" |
| 8 | demo_flesh_baseline/index.html | ✅ cycle 4 (deployed) |
| 9 | baseline report | ⏳ Phase 3.0 후 |

---

## 4. No-Go 검증 (Phase 3.0 §19 + Phase 3.1 §30)

### 4.1 Phase 3.0 No-Go (이번 prep 단계 내)

| 조건 | 발생? |
|---|---|
| ToS / robots.txt 검토 없이 fetch | ❌ (fetch 0) |
| 원문 synopsis 공개 repo 저장 | ❌ (.gitignore preempt + fixture는 fictional만) |
| 비용 상한 없이 LLM API 호출 | ❌ (API 호출 0) |
| LLM에게 데이터 정제 위임 | ❌ (Claude Code = 7 결정론적 스크립트) |
| schema 없이 수동 라벨링 | ❌ (annotate_episode_synopsis_v1 + episode_annotation_v1 정의됨) |
| hallucination rate ≥ 10% | ❌ (fixture 검증, 실 데이터는 pilot 후) |
| r ≥ 0.7 feature 3개 미만 | ❌ (fixture 검증, 실 데이터는 pilot 후) |
| feature definition 흔들림 | ❌ (Phase 2 v1.1 ANNOTATION_GUIDE 안정) |
| data card 미작성 | ❌ (template 작성됨) |

### 4.2 Phase 3.1 No-Go (이번 prep 단계 내)

| 조건 | 발생? |
|---|---|
| Phase 3.0 통과 전 학습 시작 | ❌ (학습 0, prep 코드만) |
| raw synopsis public output 노출 | ❌ (audit 강제 + test) |
| r 낮은 feature 사용 | ❌ (KEEP threshold ≥ 4 강제) |
| score reason 설명 불가능 | ❌ (reason_features + score_breakdown) |
| 데이터 ≤ 10 episodes로 ML | ❌ (No-ML baseline만) |
| neural model 도입 | ❌ |
| model card 없음 | ⏳ Phase 3.0 후 작성 |

→ **No-Go 항목 0건** (prep 단계 내).

---

## 5. 핵심 lessons (4 cycles)

| L# | 핵심 |
|---|---|
| L74 | 역할 분리 = 재현성 (Claude Code = 데이터 공장 / LLM = 라벨러 / User = 승인권자). LLM에게 데이터 정제 위임 = 같은 입력도 세션마다 다른 dataset → ML 불가능. |
| L75 | Manual Input Mode 우선 / API 후순위. Mode A는 비용 0으로 schema/prompt/feature 정의 검증. Mode A → B → C 단계화. |
| L76 | Baseline = No-ML weighted score 우선. 설명 가능성이 ML 진입 전 첫 game-keeper. ablation baseline으로 그대로 사용 가능. |

---

## 6. Cron / 자동화 상태

```text
job f0a89951:  */15 * * * * (15분 interval, recurring, 7일 자동 만료)
prompt:        /loop ... PIPELINE_AND_LLM_LABELER.md ... 자체 판단하에 개선 진행해
다음 firing:    cron이 살아있는 동안 자동
```

5 cycles 모두 cron 또는 사용자 직접 호출로 trigger됨. session-only이므로 Claude
종료 시 cron도 사라짐.

---

## 7. Phase 3.0 운영 시작을 위한 사용자 승인 5+2건

`docs/plans/PHASE_3_0_APPROVAL_CHECKLIST.md` §1 참조. 이 5+2가 모두 ☑되어야
실제 fetch / API / 저장 시작.

```text
[ ] 1. 실제 줄거리 데이터 fetch 승인 (또는 Mode A 수동 입력 승인)
[ ] 2. 출처별 ToS / robots.txt 검토 승인
[ ] 3. LLM API 사용 승인 (또는 수동 annotation 방식)
[ ] 4. 비용 상한 승인
[ ] 5. 저장 위치 / 공개 가능성 결정
[ ] 6. (보조) 공개 repo 정책 승인
[ ] 7. (보조) 10-episode mini pilot 범위 승인
```

승인 절차: §2.1 (12 step 단계별).

---

## 8. 한 줄 결론

```text
Phase 3.0 v1.1 + Phase 3.1 prep 모두 코드 / 문서 / 데모 / tests 완료.
사용자 승인 5+2건만 떨어지면 Mode A 10-episode pilot 즉시 운영 가능.
```

---

## 9. 변경 이력

| 일시 | 변경 |
|---|---|
| 2026-05-11 | 4 cycles 통합 audit (Phase 3.0 v1.1 + 3.1 prep) |
| 2026-05-11 (post-cycle 4) | Phase 3.1 Target B/C + Plan §24 bridge + §29 verifier 추가 (cycle 16-42). Phase 3.05 Rubric directive (cycle 1-29) + 124+ rubric tests. doc-currency 대량 갱신 (cycle 32-51, 53, 55, 60) + doc-reality automation (cycle 33-38, 41-42, 47). FREEZE directive (cycle 70-71) + commit readiness + actual pilot boundary. **현재 fast suite 2,648 / 0 회귀** — 본 audit은 *cycle 4 시점 prep snapshot*으로 유지하고, 종합 상태는 [COMMIT_READINESS_2026_05_11.md](../reports/COMMIT_READINESS_2026_05_11.md)를 참조 |
