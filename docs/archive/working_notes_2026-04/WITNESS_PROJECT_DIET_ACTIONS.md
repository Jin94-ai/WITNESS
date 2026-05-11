# WITNESS 프로젝트 다이어트 실행 지시서

**Status (2026-04-28):** **COMPLETE / REFERENCE** — Phase 1+2 모두 실행 완료 (2026-04-27). Companion `WITNESS_PROJECT_DIET_POSTCHECK_AND_NEXT.md`로 후속 진행. doc은 historical record로 보존.

## 목적

이 문서는 `PROJECT_DIET_ANALYSIS.md`를 바탕으로,  
WITNESS 프로젝트 폴더를 **안전하게 슬림화**하기 위한 실행 지시서다.

원칙은 다음과 같다.

- 핵심 코드, 테스트, 스펙, 현재 canonical 문서는 보존
- 캐시/임시 산출물은 즉시 정리
- 구버전 데이터/legacy iter 문서/probe 결과는 삭제보다 **archive 이동** 우선
- `world/` 같은 활성 가능성이 있는 레거시 영역은 **보류**
- 모든 작업은 **Phase 단위**로 나눠서 진행
- 각 Phase 후 반드시 확인 절차를 둔다

---

## 1. 최종 권장 전략

권장 순서는 아래와 같다.

### Phase 1 — 즉시 가능, 위험 0
- 캐시/임시 파일 삭제
- 재생성 가능한 로컬 산출물 삭제

### Phase 2 — archive 이동, 중간 위험
- 구버전 trajectory, reference, pipeline outputs 이동
- pre-PYHASH / superseded B-direction 문서와 probe 산출물 이동
- archive 후 링크/인덱스 정리

### Phase 3 — 보류
- `world/`
- `docs/world/`
- `pipeline_v2`
- 기타 의존성 가능성이 있는 것

즉, **지금 당장 해야 할 건 Phase 1 + 2**이고, Phase 3은 Lee 명시 승인 전까지 건드리지 않는다.

---

## 2. 절대 보존 대상 (KEEP_CORE)

아래는 다이어트 대상이 아니다.

- `engine/`
- `content/`
- `tests/`
- `examples/`
- `benchmarks/bench_simulation.py`
- `scripts/data_pipeline/`
- `scripts/v3_measurement/`
- 논문/figure 생성 스크립트
- `docs/HARNESS.md`
- `docs/ODD_PROTOCOL.md`
- `docs/REPORT_TEMPLATE.md`
- `docs/specs/`
- `docs/research/`
- `docs/persona_engine/`
- `docs/world_engine/`
- 루트 핵심 문서 (`README.md`, `DESIGN.md`, `CLAUDE.md`, `lessons.md`, `progress.md`)
- 설정 파일 / `.gitignore`

---

## 3. Phase 1 — 즉시 삭제 (위험 거의 0)

### 목표
캐시와 재생성 가능한 임시 산출물을 먼저 정리해서  
약 **54 MB**를 바로 줄인다.

### 삭제 대상
- `.mypy_cache/`
- 모든 `__pycache__/`
- 모든 stray `*.pyc`
- `.pytest_cache/`
- `.ruff_cache/`
- `output/trace_demo.jsonl`
- `docs/b_direction/P_ANNOTATED_DEMO.txt`

### 실행 전 체크
1. `git status` 확인
2. 실수 방지를 위해 현재 브랜치와 작업 상태 기록
3. 가능하면 한 번 zip 또는 tar 백업

### 실행 명령
```bash
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -rf .mypy_cache .pytest_cache .ruff_cache
rm -f output/trace_demo.jsonl
rm -f docs/b_direction/P_ANNOTATED_DEMO.txt
```

### 실행 후 확인
```bash
du -sh .
du -sh .mypy_cache 2>/dev/null || true
find . -name "__pycache__" | head
find . -name "*.pyc" | head
```

### 기대 효과
- 약 **54 MB 절감**
- 리스크 거의 없음
- 필요 시 `pytest`, `mypy`, `ruff`, demo 재실행으로 복구 가능

---

## 4. Phase 2 — archive 이동 (권장)

### 목표
구버전 데이터와 legacy 문서/산출물을 작업 영역에서 빼서  
실제 프로젝트 폴더를 훨씬 가볍게 만든다.

### 예상 추가 절감
약 **46 MB**
- 총합 약 **100 MB 절감**
- 전체 146 MB → 약 46 MB 수준 가능

### archive 기본 위치
```text
archive/
├── data_legacy/
└── b_direction_legacy/
```

---

### 4.1 archive로 이동할 데이터

#### 이동 대상
- `data/person/trajectory_1000.jsonl`
- `data/person/trajectory_1000_v2.jsonl`
- `data/person/trajectory_1000_v3_varied.jsonl`
- `data/reference/witness_trajectories_45.json`
- `data/person/pipeline_v1/`

#### 유지 대상
- `data/person/trajectory_1000_v4_final.jsonl`
- `data/reference/witness_trajectories_45_v2.json`
- calibration / distribution baseline
- 최신 reference 결과물

#### 실행 명령
```bash
mkdir -p archive/data_legacy

mv data/person/trajectory_1000.jsonl archive/data_legacy/
mv data/person/trajectory_1000_v2.jsonl archive/data_legacy/
mv data/person/trajectory_1000_v3_varied.jsonl archive/data_legacy/
mv data/reference/witness_trajectories_45.json archive/data_legacy/
mv data/person/pipeline_v1 archive/data_legacy/
```

---

### 4.2 archive로 이동할 B-direction legacy 문서 / 결과물

#### 이동 대상
- `docs/b_direction/probe_runs/LOOP_ITER_*.md` (Iter 1-88)
- `docs/b_direction/probe_runs/BATCH_*_REPORT.md`
- `docs/b_direction/FINDINGS_SUMMARY_ITER_1_32.md`
- `docs/b_direction/FINDINGS_SUMMARY_ITER_1_43.md`
- `docs/b_direction/FINDINGS_SUMMARY_ITER_1_48.md`
- `docs/b_direction/WORLD_BUILDING_PROGRESS.md`
- `ITER_91-119` 상세 문서들 (pre-cleanup / partially retracted era)
- 필요 시 probe json raw 결과 일부

#### 남길 canonical 문서
- `COMPONENT_LEDGER.md`
- `STATE_FIELD_STATUS.md`
- `KERNEL_GAPS.md`
- `SACRED_STATUS_NOTE.md`
- `WITNESS_INTERNAL_BRANCH_CYCLE_COMPLETE.md`
- `READABILITY_BLIND_PROTOCOL_V2.md`
- `READABILITY_BLIND_RESULTS_V2.md`
- `READABILITY_PILOT_4.md`
- `ANNOTATED_PROBE_FORMAT.md`
- `PROBE_STATS_CHARACTERIZATION.md`
- 현재 cycle 문서 (Iter 176-184)
- `ITER_INDEX.md`

#### 실행 명령 예시
```bash
mkdir -p archive/b_direction_legacy/probe_runs_1_88
mkdir -p archive/b_direction_legacy/findings_summaries_partial
mkdir -p archive/b_direction_legacy/iter_91_to_119

mv docs/b_direction/probe_runs/LOOP_ITER_*.md archive/b_direction_legacy/probe_runs_1_88/
mv docs/b_direction/probe_runs/BATCH_*_REPORT.md archive/b_direction_legacy/probe_runs_1_88/

mv docs/b_direction/FINDINGS_SUMMARY_ITER_1_32.md archive/b_direction_legacy/findings_summaries_partial/
mv docs/b_direction/FINDINGS_SUMMARY_ITER_1_43.md archive/b_direction_legacy/findings_summaries_partial/
mv docs/b_direction/FINDINGS_SUMMARY_ITER_1_48.md archive/b_direction_legacy/findings_summaries_partial/

mv docs/b_direction/WORLD_BUILDING_PROGRESS.md archive/b_direction_legacy/

# Iter 91-119 문서는 실제 파일명 확인 후 선별 이동
# mv docs/b_direction/ITER_9*.md archive/b_direction_legacy/iter_91_to_119/
# mv docs/b_direction/ITER_10*.md archive/b_direction_legacy/iter_91_to_119/
# mv docs/b_direction/ITER_11*.md archive/b_direction_legacy/iter_91_to_119/
```

---

### 4.3 scripts/b_direction 정리 원칙

#### KEEP
- 현재 cycle / active probe generation
- `_pyhash_guard.py`
- readability / annotated probe 생성 스크립트
- 현재 활용되는 autonomy / coupling / audit 스크립트

#### ARCHIVE 후보
- `run_loop_iter1-88_*.py`
- `run_iter91-119_*.py`
- 활용도 낮은 one-off scripts

#### 실행 방식
바로 삭제하지 말고:
```text
archive/b_direction_legacy/scripts_iter_1_119/
```
로 먼저 이동

---

## 5. Phase 2 이후 반드시 해야 할 후처리

### 5.1 ITER_INDEX.md 수정
archive 이동 후 깨지는 링크를 고쳐야 한다.

#### 해야 할 일
- archived 문서에 `ARCHIVED` 표시
- 새 경로 반영
- 필요하면 `INDEX_CURRENT.md` / `INDEX_ARCHIVE.md`로 분리

### 5.2 archive 정책 문서화
`archive/README.md` 하나 만들 것.

포함 내용:
- 왜 archive했는지
- 무엇이 들어있는지
- 현재 canonical 문서가 무엇인지
- 복구 방법

### 5.3 canonical vs legacy 표시
`docs/b_direction/` 안에서  
현재 기준 문서와 legacy 문서가 헷갈리지 않도록 해야 한다.

추천:
- canonical 문서 상단에 `Status: CURRENT`
- archive README에 `Status: LEGACY`

---

## 6. Phase 3 — 보류 항목 (지금 건드리지 말 것)

아래는 지금 삭제/이동하지 않는다.

### 보류 대상
- `world/` (top-level legacy)
- `docs/world/`
- `data/person/pipeline_v2/`
- `data/person/abc_snapshots/`
- top-level legacy world 관련 스크립트
- active 여부가 애매한 demo world 계열

### 이유
- 테스트/데모 의존성 가능성 있음
- `world/`는 top-level legacy지만 아직 import 흔적이 있음
- 지금 정리 이득은 작고, 깨질 위험은 상대적으로 큼

### 규칙
이 영역은 **Lee가 별도 승인하기 전까지 손대지 않는다.**

---

## 7. .gitignore / 운영 규칙 추가 제안

### `.gitignore` 보강 (선택)
이미 대부분 ignored이지만, 의도를 명시하기 위해 아래를 추가 가능:

```gitignore
# pipeline outputs
data/person/pipeline_v*/

# calibration snapshots
data/person/abc_snapshots/

# superseded reference/data variants
data/reference/witness_trajectories_45.json
data/reference/evaluation_results_calibrated.json
data/reference/evaluation_results_v2.json
```

### 운영 규칙
앞으로는 아래를 기본 원칙으로 둔다.

1. `docs/b_direction/probe_runs/`는 무한히 쌓지 않는다
2. Iter 문서는 정기적으로 consolidation 후 archive
3. 구버전 dataset은 latest + 1개 정도만 남기고 나머지는 archive
4. demo output은 커밋/보존하지 않는다
5. current / archive / reserve 구분을 문서 상단에 표시한다

---

## 8. 권장 실행 순서

### Phase 1
즉시 실행
- 캐시 삭제
- 임시 출력 삭제

### Phase 2
archive 이동
- 구버전 trajectory / reference / pipeline_v1
- B-direction legacy docs / probe runs
- legacy scripts 일부

### Phase 3
후처리
- `ITER_INDEX.md` 수정
- `archive/README.md` 작성
- canonical / legacy 표시 정리

### Phase 4
보류 항목 재검토
- `world/`
- `docs/world/`
- `pipeline_v2`
- `abc_snapshots`

---

## 9. 실행 승인 기준

### 바로 실행 가능
- Phase 1 전체
- Phase 2의 data_legacy 이동
- Phase 2의 명백한 superseded summary / probe_runs 이동

### 추가 확인 후 실행
- Iter 91-119 상세 문서 일괄 이동
- scripts/b_direction legacy 일괄 이동

### 별도 승인 필요
- `world/` 관련
- `docs/world/` 관련
- `pipeline_v2`
- `abc_snapshots`
- active tests / imports에 영향 줄 수 있는 모든 것

---

## 10. 최종 한 줄 요약

**지금 다이어트는 “삭제”보다 “캐시 즉시 정리 + legacy 산출물 archive 이동”이 핵심이다.  
먼저 54 MB를 안전하게 줄이고, 그다음 구버전 데이터와 B-direction legacy 문서를 archive로 빼서 총 100 MB 수준까지 줄이는 것이 가장 현실적이다.  
`world/`와 관련 레거시는 지금 건드리지 말고 보류한다.**
