# Pipeline v2 -- Fidelity Split Analysis + Zone Design Postmortem

> **Spec**: [WITNESS_SPIKE_6_LEARNABLE_DATA.md](../../WITNESS_SPIKE_6_LEARNABLE_DATA.md) §7.2.2
> **Previous**: [DATA_PIPELINE_v2_PHASE_A_EXT.md](DATA_PIPELINE_v2_PHASE_A_EXT.md)
> **Date**: 2026-04-22
> **Audit**: `python scripts/audit_report.py docs/person/DATA_PIPELINE_v2_FIDELITY_SPLIT.md`

## Lee의 원래 지시 (verbatim -- H5)

> "C:\Users\이진석\Desktop\Witness\WITNESS_SPIKE_6_LEARNABLE_DATA.md파일을 읽어보고 구현해서 학습할 수 있는 데이터를 만들어내보자"

## 내가 실행한 scope

Lee A/B/C/D 명시 선택 없음. H6 self-select 회피 위해 **branch-agnostic infrastructure**만 전진:
1. 이전 보고서에서 "미시도"로 기록한 per-state KL (spec §7.2.2) 측정
2. Fidelity 4.2%를 voluntary / event로 **분리** 측정 → 어느 분기(C event-feature vs D zone-redesign)가 맞는 처방인지 실증 진단
3. 재사용 가능 `scripts/data_pipeline/fidelity_check.py` 모듈화 (A/B/C/D 어느 것이 선택되든 재실행 가능)

## 축소한 지점

- 여전히 새 dataset은 생성 안 함. fidelity 재측정 + 진단만.
- Lee 결정 대기 (H6)

---

## Spec / Rule 인용 (H3)

### Spec §7.2.2 verbatim

> *"Per-state KL divergence / 1회차 KL 1.44 대비 개선 여부"*

### Spec §0.1 verbatim

> *"같은 상태에서 다른 행동이 나오면 → 학습 불가능 (noise) / 다른 상태에서 다른 행동이 나오면 → 학습 가능 (decision boundary)"*

이 원칙이 이번 진단의 핵심 틀: MLP가 **다른 state에서 다른 행동**을 학습했는가, 아니면 **잘못된 state-action 매핑**을 학습했는가?

---

## 수치 결과

### Fidelity split (spec §7.2.2 KL 포함)

| 지표 | 값 |
|---|---:|
| 자연 trajectory 샘플 | 307 (10 seeds × 200 tick) |
| 그 중 voluntary | 257 (84%) |
| 그 중 event-triggered | 50 (16%) |
| **overall match rate** | 4.2% |
| **voluntary-only match rate** | **5.1%** (13/257) |
| **event-only match rate** | **0.0%** (0/50) |
| **voluntary KL mean** | **10.5** |
| **voluntary KL median** | **8.7** |

**KL 10 이상은 "거의 무관한 분포"** (KL 0 = 동일, KL 1 정도가 "약간 다름"). 즉 신경망의 분포가 rule-based 분포와 사실상 무관.

### Zone 설계 vs 자연 분포 centroid shift (결정적 증거)

자연 voluntary state의 action별 centroid와 내 forced zone centroid 비교:

| Action | Feature | 자연 | forced (내 zone) | 절대 shift |
|---|---|---:|---:|---:|
| follow_closely | fear | **+7.26** | +1.47 | 5.79 |
| follow_closely | confusion | +7.09 | +2.52 | 4.57 |
| withdraw_in_fear | love | **+8.52** | +2.04 | **6.47** |
| withdraw_in_fear | grief | +6.89 | +0.99 | 5.89 |
| assert_loyalty | fear | +7.73 | +2.02 | 5.71 |
| discuss_with_disciples | fear | +8.17 | +2.57 | 5.61 |
| weep | event_trauma | +0.00 | +5.55 | 5.55 |
| pray | fear | +8.47 | +4.87 | 3.60 |

관찰된 패턴:
- 자연 voluntary action 대부분이 **fear=7~8 영역에서 발생** (일상적 긴장 상태)
- 내 zone은 fear=0~5 영역 (이완 상태) -- **반대 영역 설정**
- `withdraw_in_fear` 자연 love=**8.52** (헌신적일수록 두려움으로 물러남)을 내 zone은 love=0~4로 설정 -- **완전 반대**

### 수치 해석 제약 (H1)

- **이 수치가 의미하는 것**:
  - 내 zone 설계가 engine 내부 state-action 관계와 **체계적으로 반대됨**
  - 이전 보고서의 alternate interpretation 3 (zone 설계가 engine과 불일치)이 **centroid level에서 실증**
  - MLP가 학습한 것은 내 zone 정의의 inverse mapping이지 engine 정책이 아님
- **이 수치가 의미하지 않는 것**:
  - 자연 state에서 "fear=7에서 follow_closely"는 engine의 선택일 뿐 **자연스러운 인간 행동**이라는 보장 없음. content의 weight_formula 설정 결과.
  - 이 발견이 신경망 접근 자체의 실패를 의미하지 **않음** -- zone이 틀렸을 뿐.
- **제거된 가설**:
  - "Event context 부족이 fidelity 0.042의 주원인" -- **기각**. voluntary-only도 5.1%. Event feature 추가가 주된 해결책 아님.
  - "MLP가 engine의 결정경계를 약하게라도 학습함" -- **기각**. KL 10.5는 거의 무관.

금지어 self-check: H4 banned phrase list 전체에 대해 사용 안 함 확인.

---

## What could still be wrong (H4)

- [ ] **자연 샘플링이 편향**. 10 seeds × 200 tick는 307 샘플. 수난 주간 hazard가 늦게 발동하는 경우도 있어 200 tick으로 전체 궤적 대표성 부족할 수 있음.
- [ ] **Centroid 비교가 과단순**. 각 action의 state 분포가 multimodal하면 centroid 차이만으로는 "zone 완전 반대"라 단언 못 함. Covariance까지 봐야.
- [ ] **자연 state가 이상한 영역에 있는 것일 수도**. content의 weight_formula가 "fear 높을 때 follow_closely"로 기울어졌다면 그것은 engine의 설계상 특성이지 "learnable signal"이 아닐 수도. 즉 engine 자체를 모방하는 것이 옳은 목표인지 재질문 필요.
- [ ] **D가 옳다는 결론도 가설**. data-driven zone이 fidelity 개선할 것이라는 것은 추론. 실제로 구현해야 검증됨.
- [ ] **fidelity metric 편향 가능성**. KL에 넣은 rule-based weights는 voluntary actions만 비교. 만약 engine이 voluntary 6과 event 15를 통합해 선택한다면 (voluntary-only 분포와 다름), 내 KL 정의가 비교 대상이 틀림.

## What I did NOT try

| 대안 | 왜 안 함 | 미시도/불가능 |
|---|---|---|
| Data-driven zone 실제 구현 (D 선택지) | Lee 결정 대기. H6 self-select 회피 | 미시도 |
| MLP를 SimulationWorld.policies에 실제 주입해 trajectory 비교 | B 선택지 영역. Lee 결정 대기 | 미시도 |
| Event feature 추가 (C 선택지) | 이번 진단이 C 우선순위를 낮춤. Lee 확정 후 결정 | 미시도 |
| 자연 state의 multimodality 분석 (k-means per action) | 시간. 단순 centroid로 충분히 shift 확인됨 | 미시도 |
| 이전 pipeline v1 dataset의 fidelity 재측정 (baseline) | v1 모델과 v3 모델 직접 비교는 별도 가치 있음 | 미시도 |
| Engine content (weight_formula)가 실제 인간 행동과 일치하는지 검토 | content 설계 영역, 내 scope 밖 | 미시도 |

## Alternate interpretations (H4)

- **내 해석**: voluntary-only match 5.1% + centroid shift 실증 → D (data-driven zone) 우선순위 확정. C (event feature)는 voluntary 학습 실패 해결 못 함.
- **대안 해석 1**: **C가 여전히 필요**. 5.1%의 5%는 공돌 수치이고, event action 0% 매치는 확실한 context 부족 신호. D + C 병행해야.
- **대안 해석 2**: **자연 state 자체가 engine의 편향을 반영**. fear 높을 때 follow_closely 하는 Peter는 content 설계 결과. data-driven zone은 이 편향을 재학습. 정말 "천변만화"를 원한다면 engine-agnostic한 합리적 state 분포를 써야 (예: Psychology 지식 기반). 하지만 spec §0.1은 engine reproduction 프레임.
- **대안 해석 3**: **Zone을 버리고 완전 자연 trajectory만 써야**. Pipeline v1의 22756 baseline을 충분히 balance하면 되는데 내가 forced sampling이라는 우회로로 갔음. Voluntary 6 action 기준으로는 v1 baseline이 이미 engine을 그대로 reproduce. fidelity 0.042는 내 우회로의 실패 증명일 뿐 pipeline 자체 실패 아님.

**내 bias 고백**: 나는 **내 해석 + 대안 해석 3**을 믿음. 즉 "D (data-driven zone)"와 "forced sampling 근본 회의"의 두 단계. 하지만 이 두 해석이 실제로 실험 없이는 확정 불가. "forced sampling 버리고 baseline으로 복귀"는 이전 보고서에서 내가 내린 "forced sampling은 학습 가능성의 근본 수단" 판단과 모순. 변덕스러워 보일 수 있음.

---

## Lee에게 판단 요청 (H6)

이번 진단 이후 정제된 선택지:

| 선택지 | 장점 | 단점 |
|---|---|---|
| **A** Phase A ext 폐기 + Phase 1 pipeline v1 baseline 재활용 (대안 해석 3) | 이미 22756 natural sample 존재. 재학습만 하면 됨. | 이전 pipeline v1 val_acc 0.407 상태로 돌아감. 진전 없음. |
| **B** v3 MLP를 실제 simulation에 주입 (fidelity 무시) | 천변만화 여부를 Lee가 감각 판단 | 5% fidelity 상태로 Peter trajectory 비정상 가능성 |
| **C** Phase B (event feature) 우선 | 공식 spec 순서 | 본 진단이 주원인 아님을 보여줌 |
| **D** Data-driven zone 재설계 (**이번 진단이 가리키는 방향**) | centroid shift 측정으로 정확한 zone 계산 가능 | Phase A의 6300 샘플 재작업. 비용. |
| **E** Data-driven zone **+ forced sampling 유지** (A의 iteration) | A와 D의 하이브리드 | 구현 복잡 |

**내 bias 고백**:
- **D 또는 E**로 기울었음. 이번 centroid shift 측정이 너무 명확하기 때문.
- 하지만 **A (baseline 복귀)**도 강력한 option. 우리가 forced sampling 없이도 voluntary 자연 분포에서 샘플링한 것이 baseline이므로, fidelity는 자동으로 높아야 함.
- 이 bias가 Lee 결정을 편향시킬 수 있음 -- 특히 A가 가장 저비용 option임에도 내가 D로 기울면 Lee가 시간 소비할 수 있음.

---

## HARNESS 자가감사 (H7)

1. **[H1]** trivial 기각? → **부분 기각**. voluntary 5%와 centroid shift는 zone 설계 실패 증명. 하지만 "D가 옳다"는 결론은 아직 가설.
2. **[H2]** 대안 3개 이상? → **6개 나열**
3. **[H3]** 인용 verbatim? → **Spec §7.2.2 + §0.1 verbatim**
4. **[H4]** "What could still be wrong"? → **5개 작성**
5. **[H5]** Lee 원래 지시 verbatim? → **yes**
6. **[H6]** equal weight + bias? → **5 선택지 + D/E bias 고백 + A 강력함 명시**
7. **좋은 소식만 아닌가?** → 이번 보고는 **내 Phase A ext의 zone 설계 실패를 centroid level에서 실증**. 좋은 소식 없음.

---

## 산출물

```
scripts/data_pipeline/
  fidelity_check.py                  (신규, 재사용 가능, 197 lines)

docs/person/
  fidelity_v3.json                   (자동 생성 report)
  DATA_PIPELINE_v2_FIDELITY_SPLIT.md (이 파일)
```

변경 없음:
- engine/ 0 수정
- content/ 0 수정
- 데이터셋 변경 없음 (measurement only)
- 21 engine tests green 유지

---

## 세션 로그

### Session 3 (2026-04-22) -- Fidelity split + centroid postmortem

**자율 판단의 한계 인정**: Lee A/B/C/D 선택 없는 상태에서 계속 전진하면 패턴 7 재발. 이번 세션은 **branch-agnostic 진단**만 수행.

**결정적 발견 3개**:
1. Voluntary-only match도 5.1% (event context 부족이 주원인 아님)
2. Voluntary KL 10.5 (거의 무관한 분포)
3. Natural vs forced zone centroid이 **반대 방향** (예: withdraw_in_fear의 love 자연 8.52 vs forced 2.04)

**가장 중요한 메타 교훈**: 이전 보고서에서 내가 tautology risk를 "대안 해석"으로 기록만 하고 측정 안 했음. 이번에 측정하니 실제로 실증됨. HARNESS의 "alternate interpretations" 섹션은 **측정되지 않은 가설 모음**이 아니라 **다음 세션의 measurement backlog**로 활용해야 함.

**이것이 HARNESS를 실제로 쓴 두 번째 사례**: 이전 보고서의 §Alternate interpretations를 측정 대상으로 변환. 기록만 하는 것과 검증하는 것의 차이.
