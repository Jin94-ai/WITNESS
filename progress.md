# Progress -- Witness

> 마지막 업데이트: 2026-04-17 (자율 루프 최종)

---

## 세션 전체 요약

### 구현
- 엔진 22개 모듈 (core 5, rules 6, simulation 8, io 2, environment 1)
- 콘텐츠: 베드로 (10 hazard 이벤트, 7 체크포인트) + 반 고흐 (5 이벤트, 4 체크포인트)
- 194개 테스트 전체 통과
- engine/ 인물 특정 용어 0건

### 검증 4단계 (POM → PRIM → pyABC Model Selection → shapiq)
- POM: current 38.6% 7/7 통과, fear-only 1.2%, uniform 0%
- PRIM: love [1.4, 8.7], crowd [1.1, 7.2], fear 제한 없음
- pyABC: current = 100% posterior probability
- shapiq: fear x love 상호작용 = 1위 (0.123)

### Robustness 검증
- Scale robustness: feature importance가 scale에 따라 뒤집힘 → artifact 확인
- Canonical prevalence: rule family에 따라 15~65% → 불안정
- Rule ablation: 3개 가설 비교, 모두 baseline(7%) 대비 유효
- Parameter Recovery: PASS (true params in recovered box)
- Cross-Persona: 베드로=fear x love, 반 고흐=fear 단독

### 최종 발견
> "부인은 공포 단독도, 사랑 부재 단독도 아니다.
> 공포와 사랑이 충돌하는 곳에서 나왔다.
> 그가 두려워한 것은, 사랑했기 때문이다."

---

## 프로젝트 현재 상태

| 구성요소 | 상태 |
|---------|------|
| 엔진 | 22 모듈, 인물 비종속 |
| 테스트 | 194개 전체 통과 |
| POM 검증 | 구축, 적용, clamp 수정으로 개선 |
| PRIM | 적용됨 |
| pyABC Model Selection | current=100% |
| shapiq | fear x love = 1위 |
| Parameter Recovery | PASS |
| ODD Protocol | 작성 완료 |
| 시각화 | 6개 (output/) |
| 콘텐츠 | 베드로 + 반 고흐 |

---

## shapiq 환경 포함 재실행 결과 (교정)

**이전 (3개 변수)**: fear x love = 0.123 (1위)
**현재 (5개 변수, 환경 포함)**: fear 단독 = 0.026, surveillance = 0.025, love x crowd = 0.024 (공동 상위)

**교정**: "fear x love가 핵심"은 3개 변수 세트에서만 유효. 환경을 넣으면 상호작용 구조가 완전히 바뀜. **shapiq 결과는 변수 세트에 의존하는 surrogate 해석이지, 시뮬레이터의 구조적 사실이 아님.**

**확실한 것 (변수 세트 무관하게 안정적):**
- POM이 규칙군을 분리 (current 38.6% vs fear-only 1.2%)
- pyABC Model Selection: current = 100%
- Parameter Recovery: PASS
- 환경이 강해지면 부인↑ (방향성 일관)
- 도주는 환경 무관 (29% 안정)

---

## 진행 중 / 미완료

- [ ] POM 필터링 강화 -- Medium
- [ ] 렌더링 파이프라인 -- 방향 논의 필요
