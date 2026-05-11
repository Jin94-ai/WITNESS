# RFC Template — SkeletonOutput / Universal Taxonomy 변경 제안

> Per `docs/witness_narrative_mode_plan.md` §3.3 + §9.5.
>
> **이 RFC는 다음 변경에만 적용된다**:
>
> - `engine/observer/skeleton_output.py` 의 `SkeletonOutput` / 하위 dataclass
>   필드 추가, 제거, 타입 변경, 의미 변경
> - `engine/observer/universal_story_seed.py` 의 `UniversalStorySeed` 필드 변경
> - `content/universal/*.json` 의 schema_version, taxonomy 항목 추가/제거
>
> 다른 변경 (구현 세부, 렌더링 layer, anchor binding 등)은 RFC 불필요.

---

## RFC 메타

```
RFC ID:        RFC-{{nnnn}}
Title:         {{ short title }}
Author:        {{ name }}
Status:        draft | review | approved | superseded
Created:       {{ YYYY-MM-DD }}
Affected:      [SkeletonOutput | UniversalStorySeed | universal taxonomy]
```

## 1. 동기 (Why)

이 변경이 *왜* 필요한가? 다음 중 하나에 명시적으로 매핑되어야 한다:

```
- Plan §X 의 acceptance 항목 충족
- Phase Y 진행 중 발견된 contract gap
- 살 엔진(ML) 작업이 contract 외 정보를 요구함 → 그 정보를 contract에 추가
- 외부 입력 (다른 anchor 추가 등)이 기존 schema로 표현 불가
```

내부 구현 편의 (refactor 등)는 RFC 동기로 *부적합*.

## 2. 제안 (What)

### 2.1 변경 범위

```python
# Before
@dataclass(frozen=True)
class SkeletonOutput:
    seeds: tuple[UniversalStorySeed, ...]
    ...

# After
@dataclass(frozen=True)
class SkeletonOutput:
    seeds: tuple[UniversalStorySeed, ...]
    {{ new_field: NewType }} = ...
    ...
```

### 2.2 schema_version 변경

이 변경이 schema_version bump를 트리거하는가?

```
[ ] 추가만 — 기존 v1 호환 (default value 제공) → version bump 없음
[ ] 필드 제거 / 타입 변경 / 의미 변경 → schema_version 을 v(n+1)로 bump
```

후자라면 *모든 기존 SkeletonOutput consumer*가 깨진다. 마이그레이션 plan 필수.

### 2.3 마이그레이션 plan (필요 시)

```
- 영향 받는 모듈 list
- 각 모듈의 변경 내용
- 기존 산출 파일 (data/, docs/portfolio/demo/) 재생성 필요 여부
```

## 3. 영향 (Impact)

### 3.1 affected modules

```
- engine/observer/...
- engine/anchor/...
- scripts/...
- tests/...
```

### 3.2 acceptance test 갱신

```
- tests/test_skeleton/test_universal_taxonomy.py — 어떤 test가 깨지나?
- 새로 추가할 test 항목
```

### 3.3 flesh engine 영향

flesh engine은 contract만 import한다. contract 변경 시 flesh engine 의존성을
모두 갱신해야 한다.

```
- 영향 받는 flesh 모듈 (engine/flesh/...)
- 학습된 모델 재학습 필요 여부
```

## 4. 대안 (Alternatives Considered)

### 4.1 대안 A: ...
*왜 채택하지 않았는가*.

### 4.2 대안 B: ...
*왜 채택하지 않았는가*.

대안 검토 없이 RFC 승인 금지.

## 5. 리스크

```
- 기존 산출 파일 호환성
- 학습 데이터셋 호환성
- 외부 의존자 (만약 있다면)
```

## 6. 승인 체크리스트

이 RFC가 승인되려면 다음 모두 충족:

```
[ ] 동기가 외부 요구사항 (Plan / Phase / 외부 입력) 에 명시 매핑됨
[ ] 대안 최소 2개 검토됨
[ ] schema_version bump 결정 명시됨
[ ] 영향 받는 모든 모듈 list 작성됨
[ ] acceptance test 갱신 plan 명시됨
[ ] flesh engine 영향 검토됨
[ ] 마이그레이션 plan (필요 시) 작성됨
```

## 7. 변경 이력

| 일시 | 변경 |
|---|---|
| YYYY-MM-DD | initial draft |

---

*RFC 채택 시 이 파일을 `docs/plans/rfc/RFC-{nnnn}-{slug}.md` 로 복사하여
독립 문서로 보관. 동결된 contract 변경은 항상 추적 가능해야 한다.*
