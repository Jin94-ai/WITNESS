# WITNESS 프로젝트 다이어트 후 점검 및 다음 진행 지시서

**Status (2026-04-28):** **PARTIAL COMPLETE / REFERENCE** — §3 next steps 중 §3.1 (ITER_91-119 docs), §3.2 (script status), 그리고 추가 자율 진행 항목 (Phase A/B/C scripts, KEEP_CANDIDATE 분리, archive/README v1.4) 실행 완료. §3.3 (probe_runs json) 보류 (ARCHIVE_POLICY §1.2). 자율 진행 결과는 progress.md autonomous-mode entry + archive/README.md v1.4 + CANONICAL_MANIFEST v1.2 참조.

**Progress map**:
- ✓ §3.1 ITER_91-119 docs archive (Phase 2 + v1.1)
- ✓ §3.2 SCRIPT_STATUS 분류 + Phase A 실행 (v1.2) + Phase B 실행 (v1.3 autonomous LOOP 1) + Phase C 실행 (v1.3 autonomous LOOP 9)
- ⏸ §3.3 probe_runs/*.json archive — 보류 (ARCHIVE_POLICY §1.2 명시)
- ✓ §4.1 CANONICAL_MANIFEST 작성 (v1.0) + 갱신 (v1.1, v1.2 autonomous)
- ✓ §4.2 ARCHIVE_POLICY 작성 (v1.0) + v1.1 autonomous
- ⏸ §5 (3 순위) 추가 정리 일부 보류 (Lee 검토)

## 0. 문서 목적

이 문서는 최근 완료된 프로젝트 폴더 다이어트 실행 결과를 점검하고,  
추가로 해도 되는 정리 작업과 지금부터의 다음 진행사항을 정리하기 위해 작성한다.

핵심 목표는 세 가지다.

1. 이번 다이어트가 안전하게 잘 끝났는지 확인
2. 추가로 줄일 수 있는 항목과 보류해야 할 항목 구분
3. 프로젝트 운영 관점에서 다음 단계 정리

---

## 1. 전체 평가

이번 다이어트는 **잘 진행됐다**고 판단한다.

### 좋은 점
- Working area 기준 **146 MB → 50 MB (-96 MB, 약 -66%)**까지 줄였음
- 핵심 코드/테스트/현재 canonical 문서는 건드리지 않았음
- `archive/`로 구버전 데이터와 legacy 문서를 빼서 “삭제”가 아니라 “가시성 정리” 방식으로 진행했음
- import와 pytest collection 확인까지 해서 안전성 검증을 했음
- `ITER_INDEX.md` broken link가 없는지까지 확인했음

### 한 줄 평가
이번 작업은 “위험한 대청소”가 아니라  
**현재 작업 영역을 가볍게 만들고, 역사적 자산은 archive로 격리한 성공적인 정리**에 가깝다.

---

## 2. 이번 다이어트에서 특히 잘한 점

### 2.1 캐시를 먼저 턴 것
이건 제일 안전하고 절감폭도 컸다.

정리된 항목:
- `.mypy_cache/`
- `__pycache__/`
- stray `*.pyc`
- `.pytest_cache/`
- `.ruff_cache/`

이 부분은 위험이 거의 없고 절감폭이 커서, 가장 올바른 1순위였다.

---

### 2.2 v1-v3 dataset을 바로 지우지 않고 archive로 보낸 것
이 판단이 좋다.

왜냐하면:
- 현재 작업에는 필요 없지만
- 나중에 baseline 비교나 역사 추적에는 다시 꺼낼 수 있기 때문이다

즉:
- working area는 가벼워지고
- 프로젝트 기억은 유지된다

이 균형이 좋다.

---

### 2.3 B-direction legacy docs를 canonical 영역 밖으로 뺀 것
이것도 중요하다.

`LOOP_ITER_*.md`, `BATCH_*`, 초기 partial summary 들은  
현재 canonical understanding을 직접 돕기보다 과거 흔적에 가깝다.

이걸 archive로 뺀 건:
- 현재 docs 가독성을 높이고
- 현재 canonical 문서의 위계를 더 명확하게 만든다

즉 이건 단순 용량 절감보다 **문서 구조 정리** 효과가 크다.

---

## 3. 아직 남은 정리 포인트

이번 다이어트가 잘 끝났지만, 추가로 손볼 수 있는 지점은 남아 있다.

---

### 3.1 ITER_91-119 상세 docs
현재 가장 현실적인 다음 후보다.

#### 이유
- pre-cleanup / partially retracted era 문서가 포함돼 있고
- 지금 canonical understanding은 이미 consolidation 문서들에 흡수돼 있음
- working area에서 계속 보일 필요는 약함

#### 내 판단
이건 **archive 이동 1순위 추가 후보**다.

#### 다만 주의
- `ITER_INDEX.md`
- 다른 canonical 문서의 직접 참조
- handoff / summary 문서에서의 링크
를 한 번 더 grep으로 점검한 뒤 옮기는 게 좋다.

---

### 3.2 scripts/b_direction legacy
이건 두 번째 현실적인 후보다.

#### 이유
- Iter 1-119 관련 one-off experimental script가 많고
- 현재 실제로 쓰는 건 일부 current cycle / readability / pyhash guard / active probes 쪽일 가능성이 큼

#### 내 판단
이건 **바로 삭제가 아니라 archive 이동용 분류 작업**이 필요하다.

#### 추천 방식
다음 세 그룹으로 먼저 나누기:
- ACTIVE
- LEGACY_ARCHIVE
- UNSURE

이건 한 번에 옮기지 말고, 리스트를 먼저 만든 뒤 이동하는 게 안전하다.

---

### 3.3 probe_runs JSON 122개
이건 당장 급하지 않지만 언젠가 정리해야 한다.

#### 이유
- raw outputs는 쌓이기 시작하면 계속 살찜
- canonical insight는 문서에 흡수된 경우가 많음
- 하지만 JSON은 재분석이나 grep에는 아직 쓸 수 있음

#### 내 판단
지금은 보류해도 되지만, **다음 다이어트 라운드 후보**로 적절하다.

추천은:
- Iter 1-88 관련 JSON만 우선 archive
- Iter 91+는 current audit/history 참조 가능성 때문에 잠시 보류

---

### 3.4 `world/`, `docs/world/`, `pipeline_v2`, `abc_snapshots`
이건 지금 건드리지 않는 게 맞다.

#### 이유
- 용량 절감 이득이 상대적으로 작고
- 의존성/역사성/비교 가능성 리스크가 있다

#### 내 판단
이건 지금도 **보류 유지**가 맞다.

---

## 4. 추가로 하면 좋은 것

용량 절감만이 아니라 운영 측면에서 도움이 되는 후속 작업들이다.

---

### 4.1 canonical manifest 만들기
지금 archive를 만든 이상,  
“현재 프로젝트를 이해하는 데 꼭 봐야 하는 문서/데이터/스크립트”를 따로 적어두는 게 좋다.

#### 추천 산출물
`docs/CANONICAL_MANIFEST.md`

포함하면 좋은 것:
- 현재 canonical docs
- 최신 dataset
- 최신 reference files
- active scripts
- active probes
- archive에 있지만 필요 시 보는 문서

이게 있으면 다이어트 후에도 길을 안 잃는다.

---

### 4.2 archive policy를 루틴으로 만들기
지금 한 번 잘했는데,  
다음부터는 ad-hoc로 하면 다시 살찐다.

#### 추천 규칙
- Iter docs는 일정 주기마다 consolidation 후 archive
- probe raw outputs는 n회 이상 지난 것은 archive 후보로 자동 분류
- dataset은 latest + previous milestone만 working area 유지
- superseded summaries는 바로 archive

#### 추천 산출물
`docs/ARCHIVE_POLICY.md`

---

### 4.3 scripts/b_direction 분류표 만들기
이건 실제로 도움이 된다.

#### 추천 산출물
`docs/b_direction/SCRIPT_STATUS.md`

분류:
- ACTIVE
- LEGACY_KEEP
- ARCHIVE_CANDIDATE
- UNSURE

이 작업이 끝나면 scripts archive를 훨씬 안전하게 할 수 있다.

---

### 4.4 archive 무결성 체크
지금 archive를 잘 만들었지만,  
한 번은 확인해두는 게 좋다.

#### 체크할 것
- archive/README.md와 실제 파일 구조 일치 여부
- canonical 문서에서 archive 파일 직접 참조 여부
- README / index / handoff에서 dead link 없는지

#### Status (2026-04-28 autonomous-mode LOOP 24)

✓ **완료**:
- README §2.2 claims ↔ 실제 파일 구조: **100% 일치** (55+19+14+27+90+3 = 208 files + data_legacy 4+1)
- canonical 문서 archive 파일 참조: LOOP 2 + LOOP 11에서 broken-ref 0건 확인
- ITER_INDEX archive note 갱신 (autonomous LOOP 11)

✓ **자율-mode 결과 적용 영역**: archive 무결성은 *주기적으로* (Phase별 후) 재검증 필요. SCRIPT_STATUS §11/§12 + archive/README versioning이 audit trail 제공.

---

## 5. 지금 다음 진행사항

우선순위를 명확히 적는다.

---

### 1순위 — ITER_91-119 docs archive 가능성 점검
해야 할 일:
- 참조 grep
- `ITER_INDEX.md`와 summary docs에서 링크 확인
- direct dependency 없으면 archive 이동

이건 지금 바로 이어서 하기 가장 좋은 추가 작업이다.

---

### 2순위 — scripts/b_direction 분류표 작성
해야 할 일:
- active / legacy / unsure 나누기
- current cycle에 필요한 것과 과거 실험 스크립트 분리
- archive 가능 후보 리스트 만들기

이건 나중에 scripts 정리할 때 꼭 필요하다.

---

### 3순위 — CANONICAL_MANIFEST.md 작성
해야 할 일:
- 지금 기준 canonical 문서/데이터/스크립트 목록 고정
- “현재 이 프로젝트를 읽을 때 무엇을 먼저 봐야 하는지” 명시

이건 다이어트 후 프로젝트 길찾기 문서 역할을 한다.

---

### 4순위 — archive policy 문서화
해야 할 일:
- 다음부터 어떤 기준으로 archive할지 기록
- Iter docs / probe outputs / datasets / summaries 각각 규칙 정리

이걸 해두면 다시 살찌는 속도를 줄일 수 있다.

---

## 6. 지금 굳이 안 해도 되는 것

- `world/` 계열 정리
- `docs/world/` 정리
- `pipeline_v2` 정리
- `abc_snapshots` 정리
- probe_runs JSON 전체 정리
- active docs 추가 통합

즉 지금은 **중간 위험군 중 핵심만 건드리고**, 보류 항목은 그대로 두는 게 맞다.

---

## 7. 최종 판단

### 현재 상태
- 다이어트는 성공
- 핵심 working area는 충분히 가벼워짐
- archive 구조도 무난하게 잡힘
- 안전성 검증도 통과함

### 남은 최적 추가 작업
1. ITER_91-119 docs archive 점검
2. scripts/b_direction status 분류
3. canonical manifest 작성
4. archive policy 고정

### 한 줄 결론
**이번 다이어트는 거의 잘 끝났고, 지금부터는 “더 지울 것 찾기”보다  
canonical / legacy / archive 구조를 굳혀서 다시 살찌지 않게 만드는 운영 정리가 더 중요하다.**
