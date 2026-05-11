# Phase 3.0 §18 — Pre-Pilot Acceptance Baseline Snapshot

> **Snapshot type**: pre-pilot baseline (사용자 승인 5+2건 *전* / Phase 3.0 운영 *시작 전*)
> **Generated**: 2026-05-11T07:58:20 (cycle 12)
> **Tool**: `scripts/data/verify_phase3_0_acceptance.py --md-report` (Phase 3.05 cycle 11)
> **Purpose**: Phase 3 prep cycles 종결 시점의 acceptance status — Phase 3.0 운영 시작 *전*
> 기준선. 향후 사용자 승인 + 운영 진행 시 *progress*를 이 baseline에 대비할 수 있음.

이 snapshot은 *외부 의존 0 / 학습 0 / 사용자 승인 0건* 상태에서의 자동 검증 결과다.
- AUTO `[~] PENDING` (§18.1-2) — `PHASE_3_0_APPROVAL_CHECKLIST.md` 체크박스 0/7 (사용자 승인 대기)
- AUTO `[X] FAIL` (§18.3-10 중 7개) — Phase 3.0 pilot 미운영 (산출물 없음)
- AUTO `[O] PASS` (§18.4) — `.gitignore` preempt 보호 (cycle 2)
- HEURISTIC `[X] FAIL` (§18.11-12) — Data Card / Pilot Report template 미작성

## 사용자가 다음에 할 일 (작업 진행에 따라 status 변경)

```
1. 사용자 승인 5+2건 — PHASE_3_0_APPROVAL_CHECKLIST.md ☐ → ☑
   → §18.1/2 [~] PENDING → [O] PASS (AUTO 자동 감지, cycle 7)
2. Phase 3.0 Mode A 운영 (Operating Guide Step 1-9)
   → §18.3 (10 episodes) / §18.5-6 (annotation_inputs/outputs) / §18.7 (validation)
   → §18.8 (hallucination < 5%) / §18.9 (≥4 KEEP) / §18.10 (verdict) 모두 [X] → [O]
3. Phase 3.1 baseline 산출 (Operating Guide Step 10-13)
   → seed × profile / episode × profile baseline + demo HTML
4. Data Card + Pilot Report 작성
   → §18.11-12 HEURISTIC FAIL → PASS
5. 재 audit: `verify_phase3_0_acceptance.py --md-report` 다시 실행
   → 새 snapshot 생성, 이 baseline과 diff 가능
```

---

## 원본 acceptance verification report

> Generated: 2026-05-11T07:58:20  
> Tool: `scripts/data/verify_phase3_0_acceptance.py` (Phase 3.05)

---

## Summary

- **AUTO** (10 항목): 1 PASS / 7 FAIL / 2 PENDING
- **HEURISTIC** (2 항목): 0 PASS / 2 FAIL
- **MANUAL** (0 항목): 사용자 외부 확인 필요

✗ **AUTO FAIL 존재** — 아래 미충족 항목 확인 필요.

---

## 12 Acceptance 항목별 결과

| § | 항목 | Category | Status | 상세 |
|---|---|---|---|---|
| 18.1 | 사용자 승인 5+2건 완료 | `AUTO` | **~ PENDING** | 체크리스트 0/7 체크됨. 미체크: 실제 줄거리 데이터 fetch 승인, 출처별 ToS / robots.txt 검토 승인, LLM API 사용 승인 외 4건 |
| 18.2 | source 후보 ToS / robots.txt 검토 완료 | `AUTO` | **~ PENDING** | approval checklist #2 ☐: 출처별 ToS / robots.txt 검토 승인 — 사용자 승인 대기 |
| 18.3 | 10+ episode synopsis 확보 | `AUTO` | **✗ FAIL** | raw_private_dir 미지정 또는 미존재: C:\Users\이진석\Desktop\Witness\data\external_private\synopsis_raw |
| 18.4 | raw synopsis가 공개 repo 밖 또는 gitignore 보호 | `AUTO` | **✓ PASS** | data/external_private/synopsis_raw matched in .gitignore |
| 18.5 | annotation_inputs/*.json 생성 | `AUTO` | **✗ FAIL** | 디렉토리 미존재: data\annotation\phase3_pilot\annotation_inputs |
| 18.6 | annotation_outputs/*.json 확보 | `AUTO` | **✗ FAIL** | 디렉토리 미존재: data\annotation\phase3_pilot\annotation_outputs |
| 18.7 | annotation output schema validation 통과 | `AUTO` | **✗ FAIL** | hallucination_report.json 미존재: data\annotation\phase3_pilot\reports\hallucination_report.json |
| 18.8 | evidence quote hallucination rate < 5% | `AUTO` | **✗ FAIL** | hallucination_report.json 미존재: data\annotation\phase3_pilot\reports\hallucination_report.json |
| 18.9 | 최소 4 feature inter-annotator r ≥ 0.7 | `AUTO` | **✗ FAIL** | reliability.json 미존재: data\annotation\phase3_pilot\reports\reliability.json |
| 18.10 | feature KEEP / REVISE / DROP 판정 완료 | `AUTO` | **✗ FAIL** | reliability.json 미존재: data\annotation\phase3_pilot\reports\reliability.json |
| 18.11 | Data Card 작성 | `HEURISTIC` | **✗ FAIL** | template marker (TODO/TBD/{{...}}) 다수 발견 — 작성 미완료 추정 |
| 18.12 | Phase 3.1 Go / No-Go 판정 작성 | `HEURISTIC` | **✗ FAIL** | template marker 다수 발견 — 작성 미완료 추정 |

---

## 분류 의미

- **AUTO**: 코드로 자동 검증. exit code에 반영.
- **HEURISTIC**: Data Card / Pilot Report 작성 추정 (template marker 검사). exit code에 영향 0.
- **MANUAL**: 외부 활동 (사용자 환경에 doc 미존재 시 fallback).

## Status 의미

- **PASS**: 모든 조건 통과.
- **FAIL**: 필수 조건 미충족 (exit 1 트리거 — AUTO인 경우만).
- **PENDING**: 사용자 승인 진행 중 (FAIL 아님, exit 0).
- **MANUAL**: 자동 검증 불가, 사용자 외부 확인 필요.

---

> Plan §18 reference: `docs/WITNESS_PHASE_3_0_3_1_PLAN_V1_1_PIPELINE_AND_LLM_LABELER.md` §18