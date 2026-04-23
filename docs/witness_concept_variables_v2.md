# Witness v3 Phase 2 v2 -- Concept Variables (Spec §7 산출물)

> **Spec**: [WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md](../WITNESS_V3_PHASE2_V2_CONCEPT_VARIABLES.md)
> **Code**: [engine/person/state_v3.py](../engine/person/state_v3.py), [engine/person/state_candidates.py](../engine/person/state_candidates.py), [engine/person/state_derived.py](../engine/person/state_derived.py)

## 0. 핵심 원칙 (v2 §0)

> *"모든 추출 변수는 ontology 후보일 뿐이며, 실제 시뮬레이션 활성 변수는 별도로 선별한다."* (ChatGPT)

- 추출 ≠ 활성화
- 3등급: Candidate / Active / Derived
- 외부 변수 3 Layer (별도 문서)
- 정경 근거 Level A / B / C

## 1. Person Variables (Active 20개 초안)

### 1.1 Scalar emotion/state (11개)

| # | name | Level | scripture hint |
|---:|---|---|---|
| 1 | `fear` | A | 마 14:30 '두려워' |
| 2 | `hope` | A | (content 제공) |
| 3 | `grief` | A | 마 26:75 '심히 통곡' |
| 4 | `confusion` | A | 막 9:6 '무엇을 말할지' |
| 5 | `joy` | A | 눅 24:41 '기뻐하고' |
| 6 | `anger` | A | 요 18:10 '칼을 빼어' |
| 7 | `awe` | A | 눅 5:8 '나를 떠나소서' |
| 8 | `fatigue` | A | 마 26:40 '잠시도 깨어' |
| 9 | `hunger` | A | 눅 22:15 '먹기를 원하고' |
| 10 | `vitality` | A | (physical baseline) |
| 11 | `doubt` | A | 마 14:31 '왜 의심하였느냐' |

### 1.2 Target-aware (6개, Rule #18)

| # | name | Level | structure | default targets |
|---:|---|---|---|---|
| 12 | `love[target]` | A | dict[str, float] | primary_figure, peers, family |
| 13 | `loyalty[target]` | A | dict | primary_figure, peers |
| 14 | `trust[target]` | A | dict | primary_figure, peers |
| 15 | `belonging[group]` | B | dict | twelve_disciples, broader_followers |
| 16 | `guilt[toward_whom + self]` | B | dict | primary_figure, self |
| 17 | `shame[before_whom]` | B | dict | crowd, peers, self |

> **Dynamics Step 5 semantics clarification (2026-04-23)**
>
> `shame` 과 `guilt` 의 target semantics는 dict 구조상 동일하지만 **해석이 다름**:
>
> - `shame[before_whom]`: "누구 앞에서 수치를 느끼는가"
>   - `shame["crowd"]` = 군중 앞에서의 수치
>   - `shame["self"]` = 자기 앞에서의 수치 (자기 혐오 / self-loathing)
> - `guilt[toward_whom + self]`: "누구에게 잘못했는가" + "자기 판단상의 죄책"
>   - `guilt["primary_figure"]` = 주된 결속 대상에게 잘못한 죄책감 ("toward" semantics)
>   - `guilt["self"]` = 자기 판단상 자기 자신에게 진 죄책 ("self-judgment" semantics)
>
> 구현상 `dict[str, float]` 은 동일하지만 **target key의 의미가 다름**.
> 문서와 테스트에서 이 구분을 유지해야 사후 해석이 뭉개지지 않는다 (ChatGPT 지적).

### 1.3 Secondary scalars (2개)

| # | name | Level |
|---:|---|---|
| 18 | `resolve` | B |
| 19 | `trauma` | B |

### 1.4 Trajectory

_Dynamics Step 1 (2026-04-23)_: `faith_stage` 는 **Active → Derived 강등**.
서사 압축 레이블이며 관찰자의 사후 태그이기 때문에 leakage 방지를 위해
Active에서 제거했다. 이제 `state_derived.faith_stage_tag(state)` 가 love/guilt/
trust/shame/hope/resolve 조합으로 매 tick 계산한다.

_ActiveState 필드 총 **19개** (scalar 13 + target_aware 6 = 19)._

**provisional=True**: Lee 승인 전 초안. Lee가 각 변수 승인 시 provisional 플래그 flip.

## 2. Candidate Variables (10개 초안)

[state_candidates.py](../engine/person/state_candidates.py) 의 `CANDIDATE_VARIABLES` 참조.

### 2.1 Promotion blocker 별 분류

| blocker | count | 예시 |
|---|---:|---|
| `derivable_from_active` | 3 | stress, peace, admiration |
| `level_C` | 3 | forgiveness_perception, identity_restoration, spiritual_courage |
| `low_sensitivity` | 2 | attention, envy |
| `low_behavior_impact` | 1 | hunger_specificity |

### 2.2 승격 4조건 (v2 §1.2)

1. 정경 Level A/B (not C)
2. 다른 Active의 단순 합/차 아님
3. 행동 결정 영향
4. Sensitivity (policy output 변화)

**4 모두 만족 시만 Active 승격**. 현재 Candidate 10개 전부 하나 이상 blocker 보유.

**Lee 판단 필수** (v2 §11):
- Level C 후보 (`forgiveness_perception`, `identity_restoration`, `spiritual_courage`) 의 Active 승격 여부
- Low sensitivity 후보의 실측 후 재평가 (Phase B 작업)

## 3. Derived Variables (8개)

[state_derived.py](../engine/person/state_derived.py) 의 `DERIVED_VARIABLES`.

| name | 계산식 |
|---|---|
| `stress` | `0.4*fear + 0.3*confusion + 0.3*fatigue` |
| `distress` | `0.4*grief + 0.3*guilt_max + 0.3*trauma` |
| `peace` | `0.5*hope + 0.5*vitality - 0.3*stress` |
| `inner_turmoil` | `0.4*doubt + 0.3*confusion + 0.3*avg_shame` |
| `loyalty_composite` | `mean(loyalty[*])` |
| `isolation_index` | `10 - avg(belonging[*])` |
| `repentance_depth` | `mean(guilt_max, grief, trauma)` |
| `restoration_readiness` | `hope + derived_faith_stage_num*1.5 - guilt_max*0.8` (Step 1: faith_stage_tag 사용) |

**저장 안 함** (Rule #15). 매 tick `DerivedCalculator.compute_all()` 호출.

## 4. 정경 근거 Level 분포 (Rule #17)

| Level | Active count | Candidate count |
|---:|---:|---:|
| A | 12 | 2 (stress, peace) |
| B | 8 | 3 (attention, curiosity, envy) |
| C | **0** (Rule #17 금지) | 3 (forgiveness_perception 등) |

**Rule #17 준수**: Active 20개 중 Level C **0개**. Candidate만 Level C 허용.

## 5. 다음 단계 (Lee 판단)

- [ ] 20 Active 변수 각각 provisional=False 로 flip (Lee 승인)
- [ ] Level C Candidate 3개 중 Active 승격할 것 선택
- [ ] Target 목록 확정 (v2 §4.4 의 default_targets 가 초안)
- [ ] Candidate 리스트 확장 (현재 10, v2 §1.1 목표 50-60)

## 6. 한 줄 요약

**"Active 20 (Level A/B only) + Candidate 10 (blocker 있음) + Derived 8 (Active 조합). Rule #17 준수로 Level C는 Active 0. Lee 승인 전 전부 provisional."**
