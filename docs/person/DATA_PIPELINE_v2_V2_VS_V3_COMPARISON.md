# Pipeline v2 -- v2 vs v3 Checkpoint Fidelity Comparison

> **Spec**: [WITNESS_SPIKE_6_LEARNABLE_DATA.md](../../WITNESS_SPIKE_6_LEARNABLE_DATA.md) §7.2.2
> **Previous**: [DATA_PIPELINE_v2_FIDELITY_SPLIT.md](DATA_PIPELINE_v2_FIDELITY_SPLIT.md)
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py ...`

## Lee의 원래 지시 (verbatim -- H5)

> "C:\Users\이진석\Desktop\Witness\WITNESS_SPIKE_6_LEARNABLE_DATA.md파일을 읽어보고 구현해서 학습할 수 있는 데이터를 만들어내보자"

## 내가 실행한 scope

이전 보고서(`DATA_PIPELINE_v2_FIDELITY_SPLIT.md`) §What I did NOT try에서 미시도로 표시한 **"pipeline v1 baseline의 fidelity 재측정"**을 실행. v2 (기존 pipeline v1 trained MLP) vs v3 (Phase A ext trained MLP)의 fidelity를 같은 자연 trajectory에 대해 직접 비교.

## 축소한 지점

- 여전히 Lee A/B/C/D/E 결정 대기. H6 준수해 self-select 회피.
- 이번은 branch-agnostic measurement 연속 -- v2/v3 비교는 A/B/C/D/E 어느 선택지든 유효한 정보.

---

## Spec / Rule 인용 (H3)

### Spec §7.2.2 verbatim

> *"Per-state KL divergence / 1회차 KL 1.44 대비 개선 여부"*

이 지침이 직접적으로 "v1의 KL 1.44 대비 v3의 개선 여부 측정"을 명령. v3 KL mean **10.5** = v1 대비 **7배 악화**.

---

## 수치 결과

### Checkpoint 비교 (동일 자연 trajectory 307 samples)

| Metric | v2 (pipeline v1 trained, 15-action) | v3 (Phase A ext trained, 21-action) |
|---|---:|---:|
| Overall match rate | **0.394** (121/307) | 0.042 (13/307) |
| Voluntary match rate | **0.300** (77/257) | 0.051 (13/257) |
| Event match rate | **0.880** (44/50) | 0.000 (0/50) |
| Voluntary KL mean | **1.396** | 10.522 |
| Voluntary KL median | **0.395** | 8.705 |
| Voluntary KL max | 10.34 | 11.04 |

v2가 모든 지표에서 우세. Match rate는 **9.4배**, KL은 **7.5배 낮음** (더 좋음).

### Per-class match: v2

| Action | v2 match | v3 match | 차이 |
|---|---:|---:|---|
| stay_awake | **9/9 (1.000)** | 0/9 | v2 완벽 / v3 전무 |
| draw_sword | **5/5 (1.000)** | 0/5 | v2 완벽 / v3 전무 |
| deny | **29/30 (0.967)** | 0/30 | v2 거의 완벽 / v3 전무 |
| withdraw_in_fear | **11/18 (0.611)** | 1/18 (0.056) | v2 11배 |
| follow_closely | **63/160 (0.394)** | 0/160 | v2 39% / v3 0% |
| flee | 1/3 (0.333) | 0/3 | v2 1 / v3 0 |
| discuss_with_disciples | 3/34 (0.088) | 6/34 (0.176) | **v3 더 나음** (2배) |
| weep | 0/6 | 6/6 (1.000) | **v3 완벽** |
| pray | 0/30 | 0/30 | 둘 다 0 |
| assert_loyalty | 0/9 | 0/9 | 둘 다 0 |
| fall_asleep | 0/1 | 0/1 | 둘 다 0 |
| follow_at_distance | 0/2 | 0/2 | 둘 다 0 |

### 수치 해석 제약 (H1)

- **이 수치가 의미하는 것**:
  - v2가 engine 재현 능력에서 v3를 압도 -- 9배 매치, 7.5배 낮은 KL
  - Phase A ext의 forced sampling은 **engine fidelity를 망친 작업**
  - 이전 보고서의 §Alternate interpretations 대안 3 ("forced sampling 자체 회의")이 실증
- **이 수치가 의미하지 않는 것**:
  - v2가 "완벽하게 학습된 Peter"라는 의미 **아님**. voluntary match 30%, pray/assert_loyalty/weep/fall_asleep 0%.
  - v3가 "전혀 학습 안 됨" 의미 **아님**. discuss/weep는 v3가 오히려 나음 (6/34, 6/6). 제한된 zone 내 학습은 일부 성공.
- **제거된 가설** (이전 보고서에서 내 bias였던):
  - "D (data-driven zone)가 옳은 방향" -- **제거**. v2가 이미 data-driven(baseline natural trajectory)이었고 fidelity 훨씬 높음.
  - "E (forced + data-driven zone 하이브리드)" -- **약화**. v2가 forced sampling 거의 없이 나은 결과.
- **강화된 가설**:
  - **A (Phase A ext 폐기, pipeline v1 baseline 재활용)가 가장 강함**.
  - v2도 일부 voluntary (pray, assert_loyalty, weep) 0% -- 이는 feature/model 한계 (spec §0.2 영역). 즉 **A + C (event feature) 조합** 또는 **A + feature 확장** 필요.

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## What could still be wrong (H4)

- [ ] **v2 vocab과 v3 vocab이 다름** (15 vs 21 action). Match rate 비교 시 v3가 불리 (소수 vocab 포함). 하지만 v2 15-action은 자연 trajectory action의 superset이므로 비교 유효. KL은 action별 softmax라 vocab 크기 영향 있음.
- [ ] **v2가 "engine 재현"에서 나을 뿐 "천변만화" 기준은 못 충족**. Lee의 원 의도가 engine 복제가 아니라 다양성이라면 v3의 낮은 fidelity가 오히려 "다르게 행동"의 증거일 수도.
- [ ] **10 seeds × 200 tick 자연 trajectory 편향**. 특정 시드 궤적 편중 가능. seed 풀 확장 시 수치 바뀔 수 있음.
- [ ] **v2가 우수하다고 해도 일부 action은 여전히 학습 실패 (pray/assert/weep 0%)**. Pipeline v1도 완벽하지 않음. Feature 확장 없이 이 4개 action은 해결 안 될 수 있음.
- [ ] **내가 "A가 옳다"고 지금 주장하는 것도 H1 패턴 재발 위험**. 이번 측정이 명확하지만 "pipeline v1 재활용하면 fidelity 개선"도 가설 -- 실제 재훈련 + 측정 필요.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도/불가능 |
|---|---|---|
| v1 체크포인트 (peter_bc_v1.pt) 같이 비교 | v1은 5-action vocab이라 자연 trajectory의 대부분 action이 vocab 밖. 비교 부정확 | 미시도 (의미적 제약) |
| v2 fidelity를 다양한 seed 풀에서 재측정 | 시간 | 미시도 |
| v2 MLP 자체를 retrain한 별도 checkpoint와 비교 (학습 variance 체크) | 시간 | 미시도 |
| v2/v3의 behavior diversity (같은 시작 seed, policy 주입 후 action sequence 비교) | simulation-in-the-loop 필요, B 선택지 영역 | 미시도 |
| v2가 pray/assert_loyalty를 못 맞추는 원인 분석 (feature 한계인지 class imbalance인지) | 시간 | 미시도 |
| v2 training data 분포와 자연 trajectory 분포 비교 (centroid) | 중요하지만 시간 | 미시도 |

## Alternate interpretations (H4)

- **내 해석**: v2 압도적 우수 → A (Phase A ext 폐기, pipeline v1 baseline 재활용)가 옳음. 이전 D/E bias는 틀렸음.
- **대안 해석 1**: **v2도 30% voluntary match이므로 "pipeline v1도 부분 실패"**. A를 선택해도 나머지 70% voluntary 실패를 풀려면 결국 feature 확장이나 model 확장 필요. A는 시작점일 뿐 solution 아님.
- **대안 해석 2**: **v3는 engine fidelity 기준으로 실패했지만 spec §0.1의 "다른 상태 → 다른 행동" 기준으로는 학습 가능한 데이터**. val_acc 0.888이 그 증거. Lee가 "engine 복제"가 아닌 "더 풍부한 정책"을 원한다면 v3가 실제로 학습한 것은 가치 있을 수 있음.
- **대안 해석 3**: **이번 비교가 "v2 ≥ v3"을 보여줄 뿐 "A가 최선"은 미증명**. B (v3 MLP를 실제 simulation에 넣어 Lee 감각 판단)나 C (event feature 추가 시 v3 개선 여부) 직접 test 안 됨. A 결론은 v2/v3 비교에서 귀납된 추측.

**내 bias 고백**:
- 나는 **A (+ C 또는 feature 확장)**에 기울었음. 근거: 이번 측정 명확.
- 하지만 대안 해석 1+2+3 동시 고려. A 단독은 voluntary 30% 벽에 갇힐 수 있음. 대안 해석 2 (천변만화 해석)는 내가 "engine fidelity"를 기준으로 판단한 것이 Lee 의도와 맞는지 불확실.
- 이전 D/E bias가 틀린 경험이 있으므로 이번 A bias도 확신 있게 말하지 못함.

---

## Lee에게 판단 요청 (H6)

이번 v2/v3 비교 결과 반영 정제된 선택지:

| 선택지 | 장점 | 단점 |
|---|---|---|
| **A** Phase A ext 폐기, pipeline v1 baseline 재활용 (이번 증거가 가리킴) | v2 fidelity 0.394 이미 달성. 저비용. | voluntary 일부 (pray/assert_loyalty/weep) 여전히 0%. feature 한계. |
| **A+C** A + Phase B (event context feature) | 남은 voluntary 문제에 temporal context 시도 | spec §0.2 경계 (event_id feature 추가는 허용 애매) |
| **A+feature** A + `DomainState.to_feature_vector()` 주입 | 진짜 근본 해결. spec §0.2 해제 필요. | Lee 명시 허가 없이 진행 금지 (과거 실수) |
| **B** v3 MLP 실제 simulation 주입해서 "천변만화" 여부 Lee 감각 판단 | Lee의 의도 확인 직접 | fidelity 4% 모델이라 trajectory 비정상 |
| **A+D 하이브리드** baseline + data-driven zone 추가 | 이론적으로 가장 완전 | 복잡 |

**내 bias 고백**:
- **A 또는 A+C**로 기울었음. 근거: v2가 이미 달성한 fidelity 0.394를 출발점으로 한 단계씩 개선이 논리적.
- 이전 D/E bias가 틀렸음을 인정. 패턴 1 "수치(zone shift)를 해석(D가 옳다)과 착각"했음. 이번은 v2/v3 실측으로 확정.
- 그러나 이번 "A가 옳다" bias도 아직 측정 미비. A를 실제 재훈련 + fidelity 측정해야 확정.

---

## HARNESS 자가감사 (H7)

1. **[H1]** trivial 기각? → v2 > v3은 측정상 명확. 하지만 "A가 최선"은 가설.
2. **[H2]** 대안 3+? → **6개**
3. **[H3]** verbatim? → **Spec §7.2.2 인용**
4. **[H4]** "What could still be wrong"? → **5개**
5. **[H5]** Lee verbatim? → **yes**
6. **[H6]** equal weight + bias? → **5 선택지 + A/A+C bias 고백 + 이전 D/E bias 철회 명시**
7. **좋은 소식만 아닌가?** → **이전 내 판단(D/E bias)이 틀렸음을 증거로 실증**. 이것이 가장 중요한 negative finding. 자기 수정.

---

## 산출물

```
docs/person/
  fidelity_v2.json                   (신규 -- v2 fidelity 자동 생성)
  fidelity_v3.json                   (이전 -- v3 fidelity)
  DATA_PIPELINE_v2_V2_VS_V3_COMPARISON.md (이 파일)
```

변경 없음:
- engine/ 0 수정
- content/ 0 수정
- 재훈련 없음
- 기존 tests green 유지

---

## 세션 로그

### Session 4 (2026-04-22) -- v2 vs v3 checkpoint fidelity

**자기 수정의 계기**: 이전 보고서에서 **D/E bias를 고백했지만 측정은 안 했음**. HARNESS 교훈("alternate interpretations는 measurement backlog")이 이번에 직접 적용됨 -- 실제로 v2 비교 측정 후 D/E bias가 **틀렸음이 실증**됨.

**가장 중요한 교훈**: 패턴 1("수치를 본질로 착각") 재발 지점 발견. 이전 세션에서 centroid shift 5.79/6.47 같은 수치를 보고 "D가 해결책"이라 단정한 것이 패턴 1. 실제로는 v2가 이미 더 나은 fidelity를 (forced sampling 없이) 달성했음.

**HARNESS의 네 번째 실제 적용**: bias 고백을 그냥 기록하지 않고 다음 iteration에서 직접 측정해 철회/수정. 이 pattern이 작동 중.

**아직 해결 안 된 것**: v2도 30% 수준. pray/assert_loyalty/weep 0%. 이 부분은 feature/model 한계일 가능성 (spec §0.2 해제 Lee 판단).
