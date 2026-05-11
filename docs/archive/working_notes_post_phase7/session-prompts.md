# Claude Code 착수 프롬프트

아래 내용을 그대로 복사해서 Claude Code 첫 메시지로 붙여넣으세요. `DESIGN.md`가 프로젝트 루트에 이미 있어야 합니다.

---

## 📋 복사용 프롬프트

```
안녕. "베드로 시뮬레이터" 프로젝트를 시작한다.
프로젝트 루트의 DESIGN.md를 먼저 끝까지 읽어줘.

## 프로젝트 한 줄 정의
기독교인이 베드로의 시점으로 예수의 마지막 50일을 체험하는 텍스트 시뮬레이터.

## 절대 원칙 (위반 금지)
1. 예수님의 정경 말씀은 개역개정 성경 본문 그대로만 등장. 재작성·변형 절대 금지.
2. 성경에 기록되지 않은 예수님의 발화는 생성하지 않는다. 필요하면 간접 묘사만.
3. 엔진 코드(engine/)에 베드로 전용 로직 금지. 콘텐츠(content/peter/)에 엔진 로직 금지.
4. Beat의 scripture_* 타입은 LLM이 절대 관여하지 않도록 파이프라인 차단.

## 오늘 세션 목표: M1 (최소 뼈대) 시작

작업 순서:
1. DESIGN.md 섹션 4.1의 폴더 구조 생성
2. Pydantic 기반 핵심 스키마 작성
   - engine/core/agent.py (Agent, PhysicalState, EmotionalState, Relationship)
   - engine/core/event.py (Event, Beat, Source)
   - engine/core/world.py (World, Timestamp)
   - engine/core/state.py (상태 관리 유틸)
3. content/shared/scripture/john.json 스키마 정의 후 요한복음 21장 채우기
4. engine/rendering/scripture.py — scripture_ref로 원문 로드하는 함수 (절대 변경 없이)

## 작업 규칙
- 모든 클래스에 타입 힌트 + docstring 필수
- 복잡한 추상화보다 명확한 단순함
- 의심스러우면 멈추고 질문할 것
- 오늘 베드로 전용 코드는 작성하지 않는다 (engine 뼈대만)

## 진행 방식
먼저 DESIGN.md를 읽고, 작업 계획을 나에게 공유해줘.
내가 승인하면 1번부터 순차적으로 진행.
각 단계 완료 시 간단히 보고 후 다음으로.
```

---

## 사용 팁

**첫 세션 후 이어가는 세션**에서는 이렇게 시작하세요:

```
이전 세션에서 [완료한 작업]까지 진행했다.
오늘은 [다음 작업]을 하자.
DESIGN.md 섹션 [번호] 참조.

절대 원칙 (재확인):
- 정경 말씀 재작성 금지
- 엔진/콘텐츠 분리 유지
- scripture_* Beat는 LLM 관여 금지
```

---

## Scene 작성 세션에서 쓸 프롬프트

M2 이후 실제 Scene을 만들 때:

```
오늘은 Scene [번호] ([장면 이름])를 작성한다.
DESIGN.md 섹션 2.2의 해당 Scene 설명 참조.

이 Scene의 Beat 시퀀스를 먼저 설계해줘:
- 각 Beat의 타입 (narration / interior / dialogue / scripture_jesus / scripture_other / action)
- scripture_* Beat는 정확한 scripture_ref 명시
- 베드로의 상태 변화 지점 표시

내가 Beat 시퀀스를 승인하면, 그 다음 각 Beat의 실제 텍스트를 작성한다.
scripture_* Beat는 content/shared/scripture/에서 원문 로드만 하고 절대 재작성하지 않는다.
```

---

## 검증용 프롬프트 (자주 사용 권장)

작업 중간중간 사용하세요:

**엔진/콘텐츠 경계 확인:**
```
지금까지 작성한 코드에서 engine/ 아래에 베드로 전용 하드코딩이 있는지 검사해줘.
있다면 어떻게 content/peter/로 분리할 수 있는지 제안해줘.
```

**정경 인용 정확성 검증:**
```
content/peter/scenes/ 아래 모든 Scene 파일의 scripture_jesus Beat를 검사해줘.
각 Beat의 scripture_ref가 content/shared/scripture/ 본문과 문자 단위로 일치하는지 확인.
불일치가 있으면 보고만 하고 수정하지 말 것.
```

**확장성 체크:**
```
현재 구조에서 두 번째 인물(예: 반 고흐)을 추가한다고 가정하자.
engine/은 얼마나 수정해야 하나? content/는 어떤 새 폴더가 필요한가?
실제 수정은 하지 말고 분석만 해줘.
```

---

## Milestone 전환 시 체크리스트

각 M 단계 완료 시 Claude Code에게 물어볼 것:

**M1 완료 체크:**
- [ ] 모든 엔진 스키마가 Pydantic으로 정의되었는가
- [ ] Scripture 로더가 개역개정 본문을 정확히 반환하는가
- [ ] 테스트로 Beat 렌더링이 작동하는가
- [ ] engine/에 베드로 하드코딩이 없는가

**M2 완료 체크:**
- [ ] Scene 9, 15, 17이 콘솔에서 재생 가능한가
- [ ] Scene ↔ Chronicle 전환이 자연스러운가
- [ ] Faith Journey 상태가 Scene을 거치며 변화하는가
- [ ] "네가 나를 사랑하느냐" × 3이 개역개정 그대로 출력되는가

**M3 완료 체크:**
- [ ] 15개 Scene 전부 재생 가능한가
- [ ] 50일 흐름이 끊김 없이 이어지는가
- [ ] 모든 정경 인용이 문자 단위로 정확한가

**M4 완료 체크:**
- [ ] CLI에서 처음부터 끝까지 완주 가능한가
- [ ] 문체 Layer A/B가 일관되는가
- [ ] 신학적 오류가 없는가 (감수 필요)
