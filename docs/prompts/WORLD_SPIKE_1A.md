# WORLD_SPIKE_1A.md — 세계 시뮬레이션 첫 실행 지시

---

## 배경

Witness 프로젝트가 전기 시뮬레이터에서 세계 시뮬레이션으로 확장한다.
WORLD_DESIGN.md와 WORLD_DESIGN_v1.1_amendments.md를 참조하되,
이 문서의 지시가 최우선이다.

## 외부 리뷰어(Gemini + ChatGPT) 조언 반영 사항

아래 조언들을 구현에 반드시 반영할 것:

### 1. 동역학 규칙 명시
모든 변수에 갱신 방정식, 시간 상수, 관측 출력을 명시한다.
"변수가 있다"가 아니라 "이 변수가 이렇게 변한다"를 코드로 정의한다.

### 2. Layer 간 인과에 제동 장치
cross-layer 연결에 delay, threshold, saturation 중 하나 이상 필수.
즉각 반응하는 feed-forward chain 금지.

### 3. 세계 성공 기준 수치화
"세계가 돌아간다"를 측정 가능한 수치로 정의한다.
테스트에서 이 수치를 검증한다.

### 4. 가변 시간 단계 고려
평상시 1일 단위, 향후 핵심 사건 시 세분화 가능한 구조로 설계.
지금은 1일 고정이지만, dt를 파라미터로 받는 구조로 만든다.

### 5. Aggregation 전략 명시
agent가 연결될 때(Spike 2) 하루 동안의 행동을 세계에 어떻게 반영할지,
각 WorldEffect마다 집계 방식(sum/max/mean/threshold)을 정의할 수 있는 구조를 미리 잡아둔다.
Spike 1A에서 실제 agent는 없지만, 인터페이스는 준비.

### 6. Runaway detection
변수가 비정상적으로 폭발하면 자동 감쇄하는 안전장치를 넣는다.
clamp은 기본, 추가로 급격한 변화율 감지 시 경고 로그.

### 7. 인과적 일관성 테스트
Layer 간 상관관계의 물리적 제약을 테스트로 작성한다.
예: 순례자 유입↑ 이면 군중 밀도↑ 이어야 함 (역방향이면 버그).

### 8. Spike를 세분화
Spike 1A: 달력 + 군중 밀도 (이것만)
Spike 1B: 경제 (staple_price)
Spike 1C: 정치 (roman_alertness)  
Spike 1D: Sync Layer 통합
한 번에 다 만들지 않는다.

## 실행 지시

```
WORLD_DESIGN.md, WORLD_DESIGN_v1.1_amendments.md, 이 문서를 읽어라.

Spike 1A를 실행한다. 달력과 군중 밀도 두 개만.

절대 규칙:
1. engine/ 수정 금지
2. content/ 기존 파일 수정 금지
3. 기존 1003 테스트 보존
4. world/ 아래에만 새 코드

리뷰어 조언 반영 (위 8개 항목 모두 적용):
- 모든 변수에 갱신 방정식 명시
- cross-layer 인과에 delay/threshold/saturation 적용
- 성공 기준을 수치로 정의하고 테스트로 검증
- dt를 파라미터로 받는 구조 (지금은 1일 고정)
- WorldEffect aggregation 인터페이스 준비 (구현은 Spike 2)
- 변수 폭발 시 runaway detection + 경고 로그
- 인과적 일관성 테스트 작성 (순례자↑→군중↑ 등)
- Spike 1B/1C/1D는 하지 않는다

만들 것:
- world/ 폴더 구조
- Layer 프로토콜
- 유대 달력 (90일, 절기 자동 계산)
- 군중 밀도 (달력 연동, 갱신 방정식 명시)
- 세계 틱 진행기
- content/worlds/jerusalem_ad30/ 초기 데이터
- 90일 데모 스크립트
- 단위 테스트 + 인과 일관성 테스트

성공 기준 (테스트로 검증):
- 유월절 window에서 crowd_density peak가 평시 대비 3배 이상
- 유월절 후 crowd_density가 감소 곡선을 그림
- 오순절에 두 번째 peak 발생
- 안식일이 정확히 7일마다
- 100 seed 실행 시 flatline 비율 < 10%

자율 진행. 완료 후 보고.
시작해라.
```

---

*이 문서를 프로젝트 루트에 배치 후, 위 프롬프트를 Claude Code에 전달.*
