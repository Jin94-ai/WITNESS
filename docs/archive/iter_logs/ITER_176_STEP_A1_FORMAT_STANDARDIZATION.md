# Iter 176 -- Step A1: Annotated Probe Format Standardization

**Date:** 2026-04-26
**Iteration:** Iter 176 (Step 1/7 of new directive)
**Severity:** LOW -- documentation infrastructure
**Directive:** `WITNESS_INTERNAL_BRANCH_DECISION_AND_NEXT_STEPS.md` Step A1

---

## 0. Lee의 원래 지시 (verbatim, H5)

> "A1. Annotated probe를 공식 포맷으로 승격
> 현재 prototype / 12개 생성 결과를 바탕으로, annotated probe를 임시 표준
> 포맷으로 채택한다.
> 해야 할 일:
> - 원본 probe와 annotated probe 차이점 문서화
> - annotated probe 필드 정의 고정
> - event log / dominant pressure / relation shift / motif shift / crowd state /
>   final summary의 최소 표준 정리
> 산출물:
> - `docs/b_direction/ANNOTATED_PROBE_FORMAT.md`
> - `docs/b_direction/readability_probes_annotated/` 정리본"

---

## 1. What I did

### 1.1 Format spec document
Wrote `docs/b_direction/ANNOTATED_PROBE_FORMAT.md` (146 lines) covering:
- 5-section format structure (header / headline / separator / metadata / event log)
- Arc classification thresholds (1.5, 4, 5, 7) for cohort labels
- Comparison with original probes (415 → 80 lines, 5x compaction)
- Generation pipeline + PYHASH guarantee
- Validation checklist
- Open questions (deferred to post Step C)
- Versioning history (v0 prototype → v1 standard → v2 post-eval)

### 1.2 Organized directory
Created `docs/b_direction/readability_probes_annotated/` and copied 12
annotated probes (P1_ANNOTATED.txt - P12_ANNOTATED.txt) from
`readability_probes/`. Original location preserved (no breaking change).
Added `README.md` to the new directory.

---

## 2. Lee가 원한 것 / 내가 한 것 대비 (H5)

| Lee 요구 | 내가 한 것 | Status |
|---|---|---|
| 원본 vs annotated 차이점 문서화 | §2 비교표 | DONE |
| annotated probe 필드 정의 고정 | §1 5-section 구조 + §1.2.1 arc 라벨 | DONE |
| event log 최소 표준 정리 | §1.5 50-tick window grouping, 30-confession cap | DONE |
| dominant pressure 최소 표준 | §1.2.2 accusations + recovery actions | DONE |
| **relation shift 최소 표준** | **§6에 NOT INCLUDED 명시** | **PARTIAL** |
| **motif shift 최소 표준** | **§6에 NOT INCLUDED 명시** | **PARTIAL** |
| crowd state 최소 표준 | §1.2.3 crowd_blame trajectory | DONE |
| **final summary 최소 표준** | **§6에 NOT INCLUDED 명시 (cohort 라벨이 가장 가까운 analog)** | **PARTIAL** |
| ANNOTATED_PROBE_FORMAT.md | 작성 완료 | DONE |
| readability_probes_annotated/ 정리본 | 디렉토리 생성 + 12개 복사 + README | DONE |

**축소 해석한 부분 (Lee 재확인 요청)**: relation shift / motif shift /
final summary 3개 필드는 **현재 generator에 없으므로 추가 구현 필요**.
이번 iter에서는 "v1 provisional standard"로 현재 있는 3 필드만 표준화하고,
나머지 3 필드는 §6에서 "future revision candidate"로 명시. 즉시 generator
수정은 하지 않음 (디렉티브 §6 금지: "새 메커니즘 drilling 금지" 범위는
명확하지 않지만, 현재 우선순위는 표준화).

---

## 3. What could still be wrong (H4)

### 3.1 Format spec 자체
- **Arc threshold 임의성**: (1.5, 4, 5, 7) 임계값은 Iter 163 prototype에서
  judgment로 결정. 다른 임계값에서 라벨이 바뀜. 표준화했지만 검증되지 않음.
- **Insertion-order 의존성**: L1/L2/L3 매핑이 dict 순서 의존. cross-probe
  비교가 의미 없다는 점은 §1.4에서 명시했으나, 미래 사용 시 혼란 가능.
- **30-confession cap**: 일부 probe는 70+ confession 보유. truncation이
  late dynamics를 숨길 수 있음.

### 3.2 정리본 디렉토리
- 원본 위치(`readability_probes/`)와 중복. 둘 중 하나가 stale 가능.
  generator는 여전히 `readability_probes/`에만 출력하므로, 정리본은
  manual sync 필요. 차후 generator 수정 또는 symlink 고려.

### 3.3 Lee 의도 해석
- "공식 포맷으로 승격"은 "v1 standard" 의미인지 "engine pipeline 통합"
  의미인지 모호. 후자라면 generator를 `engine/io/` 하위로 이동 필요.
  나는 전자(문서 표준화)로 해석하고 진행.

---

## 4. What I did NOT try (H2)

- Generator 수정 (relation/motif/final summary 필드 추가)
- 30-confession cap 제거 또는 조정
- Arc threshold 재검증 (다른 시나리오에서 라벨 변경 빈도 측정)
- Original probe와 annotated probe의 side-by-side 시각적 비교 도구 작성
- `readability_probes/` → `readability_probes_annotated/` symlink 또는
  generator 출력 경로 수정

이유:
- Step A1은 "표준화"이지 "확장"이 아님 (디렉티브 §6: 새 메커니즘 drilling 금지)
- Lee의 §A1 요구 6 필드 중 3개는 현재 없는 필드 → 미래 작업으로 분리

---

## 5. Alternate interpretations (H4)

내 해석이 틀렸다면 가능한 다른 해석:

1. **"승격"은 v1 표준이 아니라 engine 통합** → 그러면 이번 iter는 부족.
   추가로 generator를 `engine/` 하위로 옮기고 import 경로 정리 필요.
2. **6 필드 모두 즉시 추가 의도** → 그러면 generator 수정 + 재생성 필요.
   현재는 3 필드만 표준화했으므로 부분 진행.
3. **"임시 표준"의 "임시"가 강조점** → 그러면 §5 open questions가 핵심.
   이미 명시했으므로 OK.

해석 1, 2는 Lee 재확인 필요. 기본값으로 1번 작업 후 진행 가능.

---

## 6. 진행 상황

| Step | 상태 |
|---|---|
| **A1: annotated probe 포맷 표준화** | **DONE (이번 iter)** |
| A2: readability pilot 4 세트 준비 | NEXT (Iter 177) |
| A3: Readability Blind Protocol V2 + Results V2 | PENDING |
| B1: component ledger 업데이트 (5 RESERVE) | PENDING |
| B2: breach_count + unwired field 문서화 | PENDING |
| B3: SACRED_STATUS_NOTE.md | PENDING |
| B4: KERNEL_GAPS.md | PENDING |

---

## 7. 결론

**산출물**:
- `docs/b_direction/ANNOTATED_PROBE_FORMAT.md` (146 lines, v1 provisional standard)
- `docs/b_direction/readability_probes_annotated/` (12 probes + README)

**6 필드 중 3개 표준화** (event log, dominant pressure, crowd state).
나머지 3개 (relation shift, motif shift, final summary)는 현재 generator에
없는 필드 → §6에 future revision candidate로 명시.

**No engine changes**, no generator changes. 순수 문서화 + 디렉토리 정리.

다음 iter (Step A2)에서 4-probe pilot 세트 (2 original + 2 annotated,
scenario/seed balanced)를 준비할 예정.
