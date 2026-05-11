# Witness Archive Policy

**Date:** 2026-04-27
**Source:** `docs/WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md` §4.2 / §5(4순위)
**Purpose:** 한 번 다이어트 잘 했지만, 다음부터 다시 살찌지 않도록 운영 규칙 고정

---

## 0. 한 줄 원칙

**"working area는 현재 진행에 필요한 것만. 역사적 자산은 archive로."**

archive는 삭제가 아니다. 작업 영역에서 **빼는** 것이다.

---

## 1. 4가지 영역 + 각각의 규칙

### 1.1 Iter 문서 (`docs/b_direction/ITER_*.md` + `LOOP_ITER_*.md`)

**규칙**: Iter cycle이 자연 종료되거나 consolidation 문서가 작성된 시점부터
**N+50** Iter 후 archive 후보.

| 시점 | 처리 |
|---|---|
| Iter 작성 직후 | 작업 영역에 KEEP |
| Cycle 종료 + consolidation 문서 작성 | KEEP (직접 reference 가능) |
| 다음 50 Iter 경과 | 직접 reference 없으면 archive 후보 |
| Canonical 문서에서 file-link로 인용됨 | archive 시 **link 갱신 필수** |

**예시** (이번 다이어트 기준):
- Iter 91-119 → 현재 Iter 184. 65 iter 경과. canonical link 갱신 + archive 완료.
- Iter 1-88 LOOP_ITER → FINDINGS_SUMMARY로 흡수됨. archive 완료.
- Iter 120-160 → 25-65 iter 경과. canonical 인용 있는 것은 KEEP, 나머지는 다음 round에서 검토.
- Iter 161-184 (current cycle) → KEEP.

**Archive 위치**:
```
archive/b_direction_legacy/
├── iter_91_to_119/
├── probe_runs_1_88/
├── findings_summaries_partial/
└── (future) iter_120_to_159/  ← 다음 round 후보
```

### 1.2 Probe raw outputs (`docs/b_direction/probe_runs/*.json`)

**규칙**: canonical 문서에 결과가 흡수되면 archive 후보.

| 시점 | 처리 |
|---|---|
| Iter 진행 중 | working area |
| Iter 완료 + 회고 docs 작성 | KEEP (재분석 가능성) |
| Canonical findings에 흡수됨 (FINDINGS_SUMMARY 또는 CONSOLIDATION) | archive 후보 |
| 마지막 grep / re-analysis 후 12개월 경과 | archive 강력 후보 |

**현재 상태**: 122 JSON files, ~1.5 MB. 다음 round 후보 (이번에는 보류).

**LOCKED 2026-04-28**: 보류 결정 유지 (Lee decision). 별도 directive 없으면 archive 안 함.

**Archive 위치**:
```
archive/b_direction_legacy/probe_outputs_iter_X_to_Y/
```

### 1.3 Datasets (`data/person/*.jsonl`, `data/reference/*.json`)

**규칙**: **latest + 1 previous milestone**만 working area. 그 이전은 archive.

| 항목 | KEEP | ARCHIVE |
|---|---|---|
| trajectory | latest (v4_final) + 직전 milestone | 더 이전 모든 버전 |
| reference | latest (_v2) | _v1 + _v0 |
| pipeline | latest pipeline | 이전 pipelines |
| ABC snapshots | active calibration only | 이전 calibrations |

**현재 상태** (이번 다이어트 후):
- trajectory v4_final → KEEP
- v1, v2, v3 → archive 완료
- reference v2 → KEEP
- reference v1 → archive 완료
- pipeline_v1 → archive 완료
- pipeline_v2 → 보류 (Lee 결정 대기)

**Archive 위치**:
```
archive/data_legacy/
├── trajectory_1000.jsonl
├── trajectory_1000_v2.jsonl
├── trajectory_1000_v3_varied.jsonl
├── witness_trajectories_45.json
└── pipeline_v1/
```

### 1.4 Summaries / Consolidations / Findings docs

**규칙**: Subset이 Superset에 포함되는 chain은 latest만 KEEP.

| Chain example | 처리 |
|---|---|
| FINDINGS_SUMMARY_ITER_1_32 ⊂ _1_43 ⊂ _1_48 ⊂ _1_63 | _1_63만 KEEP, 나머지 archive |
| WORLD_BUILDING_PROGRESS.md → _v2.md | v2만 KEEP |
| READABILITY_BLIND_PROTOCOL.md → _V2.md | V2 KEEP, V1은 reference로 KEEP (deprecation 명시 시) |

이미 처리됨 (이번 다이어트):
- FINDINGS_SUMMARY 1_{32,43,48} → archive
- WORLD_BUILDING_PROGRESS.md (v1) → archive
- READABILITY V1은 reference KEEP (V2가 V1을 explicit supersede)

---

## 2. Scripts (`scripts/b_direction/`) 운영 규칙

`docs/b_direction/SCRIPT_STATUS.md` 참조.

**규칙**:

1. **ACTIVE_BUILDING_BLOCK** (다른 script가 import) → 절대 archive 금지
2. **ACTIVE_CURRENT_CYCLE** (현재 진행 cycle) → KEEP
3. **LEGACY_KEEP** (Iter 120-160, 직접 reference 있음) → KEEP
4. **ARCHIVE_CANDIDATE** (one-off, leaf, no imports) → 일괄 archive 가능
5. **UNSURE** → Lee 검토 후 분류
6. **KEEP_CANDIDATE** (canonical doc reference 있음, 약/강) → KEEP (Phase C에서 7개 식별)

**Archive 시 검증 단계**:

```bash
# Step 1: 후보 script가 다른 곳에서 import되는지 grep
grep -rln "from scripts.b_direction.{name}" --include="*.py" .

# Step 2: canonical docs에서 reference하는지 grep
grep -rln "{script_name}" docs/

# Step 3: 0건이면 archive 안전 (Phase A/B/C 검증 패턴)
# Step 4: import 0 + canonical reference 있으면 KEEP_CANDIDATE
# Step 5: 양쪽 모두 1건 이상이면 LEGACY_KEEP 또는 BUILDING_BLOCK
```

**Phase A/B/C 실행 결과 (2026-04-27 ~ 2026-04-28)**:

| Phase | Date | Scripts moved | Target |
|---|---|---:|---|
| A | 2026-04-27 | 55 | `scripts_iter_1_88/` (Iter 1-88 leaf loop_iters; 5 building blocks preserved) |
| B | 2026-04-28 | 19 | `scripts_iter_91_119/` (§6.2; UNSURE 3 preserved) |
| C | 2026-04-28 | 14 | `scripts_phase_c_oneoffs/` (§6.3.1; 7 KEEP_CANDIDATE preserved) |
| **Total** | | **88** | **scripts/b_direction count: 125 → 37** |

**검증 통과 기록**: 모든 Phase 후 building-block import 통과 + pytest 1647 tests collection 변동 없음.

---

## 3. Archive 위치 + 운영

### 3.1 위치
모든 archive는 `archive/` (legacy data) + `docs/archive/` (legacy docs) 하위:

**`archive/`** (data + scripts, gitignored):
```
archive/
├── README.md                  ← git tracked
├── data_legacy/               ← gitignored
└── b_direction_legacy/        ← gitignored
    ├── iter_91_to_119/
    ├── probe_runs_1_88/
    ├── findings_summaries_partial/
    ├── scripts_iter_1_88/        ← Phase A executed v1.2 (55 scripts)
    ├── scripts_iter_91_119/      ← Phase B executed v1.3 (19 scripts)
    └── scripts_phase_c_oneoffs/  ← Phase C executed v1.4 (14 scripts)
```

**`docs/archive/`** (legacy docs, git tracked):
```
docs/archive/
├── REVIEW_RESPONSE_V1_2.md
├── TECHNICAL_SUMMARY_FOR_REVIEW.md
├── root_2026-04/                 ← 6 root WITNESS_*.md (cleanup 2026-04-28)
├── iter_logs/                    ← 43 ITER_*.md + FINDINGS_SUMMARY (Branch C cleanup)
├── branch_c_working/             ← 18 S2/S3/S4/S5 results + design plans
├── readability_blind/            ← 9 이전 round blind eval
├── full_eval_n12/                ← 3 N=12 GPT-5.5 working
├── working_notes_2026-04/        ← 13 docs/ 루트 working notes
└── story_progressive_2026-04/    ← 6 Story MVP progressive (FAILURE_MODES, REVISION_1, etc.)
```

→ Total active reduction: 226 → ~133 visible files (41% 감소). 자세한 경로 매핑은 `progress.md` cleanup pass 섹션 참조.

### 3.2 Git 처리
`.gitignore`에:
```gitignore
archive/*
!archive/README.md
!archive/.gitkeep
```

archive 내용은 **로컬 only**. 다른 환경에서 필요하면 외부 백업 (tar.gz)에서 복원.

### 3.3 외부 백업 권장 시점
- archive/ 가 100 MB 이상이 됐을 때
- 다른 컴퓨터/팀에 프로젝트 공유 직전
- 디스크 압박 시

방법:
```bash
tar -czf Witness_archive_$(date +%Y-%m-%d).tar.gz archive/
# upload to external storage, then optionally:
rm -rf archive/
```

### 3.4 복구 방법
archive/README.md §4 참조. 일반:
```bash
mv archive/{path}/{file} {original_location}/
```

---

## 4. 문서 상태 표시 운영 규칙

새로 작성하는 모든 b_direction 문서 상단에 명시:

```markdown
**Date:** YYYY-MM-DD
**Status:** CURRENT | LEGACY | ARCHIVE_CANDIDATE | DEPRECATED
**Supersedes:** (있으면 — 어떤 문서를 대체하는지)
**Superseded by:** (있으면 — 어떤 문서가 대체했는지)
```

`Status` 값:
- **CURRENT**: 현재 활용. archive 금지.
- **LEGACY**: 역사적 가치 있음. archive 후보지만 직접 reference 있을 수 있음.
- **ARCHIVE_CANDIDATE**: 다음 round archive 후보.
- **DEPRECATED**: superseded 됐지만 reference로 보존.

---

## 5. 정기 archive round 권장 cadence

### 5.1 Trigger 조건

**조건 A — Iter 진행 기반**:
- 매 50 iter 완료 시 archive round 실행 검토
- 단순 trigger: "직전 archive 이후 50 iter 경과"

**조건 B — 용량 기반**:
- working area (archive 제외) > 80 MB 시
- `docs/b_direction/` > 5 MB 시
- `scripts/b_direction/` > 2 MB 시

**조건 C — 가독성 기반**:
- `ls docs/b_direction/*.md` 60+ 파일일 때
- `ls scripts/b_direction/*.py` 100+ 파일일 때

### 5.2 Archive round 절차

```
1. Pre-flight
   - git status 확인
   - 현재 다이어트 분석 doc 작성 (PROJECT_DIET_ANALYSIS.md style)

2. Classification
   - canonical / legacy / archive 분류
   - SCRIPT_STATUS / 새 manifest 갱신

3. Reference grep
   - 후보 파일들이 canonical에 인용되는지 확인
   - 있으면 link/path 갱신 필수

4. Archive 이동
   - mkdir + mv
   - canonical 문서 link 갱신

5. Verification
   - import OK
   - test collection OK
   - canonical doc 링크 자동 검증 (link checker)

6. Documentation
   - archive/README.md 업데이트 (versioning)
   - CANONICAL_MANIFEST.md 갱신 (필요 시)
   - 회고 doc 작성

7. (선택) 외부 백업
```

### 5.3 자동화 가능한 부분

미래 작업 후보:

```python
# scripts/maintenance/archive_check.py (가상)
# - working area 용량 측정
# - SCRIPT_STATUS canonical 분류 vs 실제 import 그래프 비교
# - dead link 탐지
# - archive round trigger 조건 체크
```

지금은 미작성. 다음 round 자동화 후보.

---

## 6. 보류 항목 정책

다음은 **별도 평가 + Lee 명시 승인** 전 archive 금지:

- `world/` (top-level legacy)
- `docs/world/`
- `data/person/pipeline_v2/`
- `data/person/abc_snapshots/`
- 활성 dependency 가능성 있는 모든 영역

평가 시 점검:
1. 의존성 그래프 (import + runtime)
2. canonical reference 유무
3. 역사적 비교 가치
4. 재생성 비용

---

## 7. Anti-pattern (피해야 할 것)

### 7.1 한 번에 많이 옮기기
**문제**: 의존성 깨짐 + 복구 어려움.
**해결**: phase 단위로 분할. 각 phase 후 검증.

### 7.2 분류 없이 mass archive
**문제**: ACTIVE/LEGACY/ARCHIVE 뭉개짐.
**해결**: SCRIPT_STATUS / CANONICAL_MANIFEST 먼저 갱신 후 이동.

### 7.3 link 갱신 누락
**문제**: dead link → 사람이 confusing.
**해결**: archive 직전 grep으로 링크 추적, archive 직후 갱신.

### 7.4 archive 위치 분산
**문제**: 어디에 무엇이 있는지 헷갈림.
**해결**: 모든 archive는 `archive/` 하위 + README 갱신.

### 7.5 README 미갱신
**문제**: archive에 뭐가 있는지 모름.
**해결**: 매 round 끝에 archive/README.md versioning 업데이트.

---

## 8. 최종 한 줄

**"매번 이전 round의 README + CANONICAL_MANIFEST + SCRIPT_STATUS 부터 갱신.
그러면 다이어트는 mechanical work로 전락하고, 중요한 결정에 시간을 쓸 수 있다."**

---

## 9. Versioning

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-27 | 초기 정책 — 이번 다이어트 (Iter 184) 후 |
| v1.1 | 2026-04-28 | autonomous-mode LOOP 12: §2 Phase A/B/C 실행 결과 표 추가, KEEP_CANDIDATE 분류 #6 추가, archive 시 검증 단계에 doc reference grep 추가, §3.1 archive tree에 Phase A/B/C 폴더 명시. |
| **v1.2 (this)** | **2026-04-28** | **autonomous-mode LOOP fire 16: §3.1에 docs/archive/ 6 subdir 추가 (root_2026-04, iter_logs, branch_c_working, readability_blind, full_eval_n12, working_notes_2026-04, story_progressive_2026-04). 226→133 visible files (-41%) 명시.** |
