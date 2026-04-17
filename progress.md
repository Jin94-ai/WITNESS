# Progress -- Witness

> 마지막 업데이트: 2026-04-17 (최종)

---

## 프로젝트 최종 상태

| 지표 | 값 |
|------|-----|
| 엔진 모듈 | 22개 |
| 콘텐츠 팩 | 2 (Peter + Van Gogh) |
| 테스트 | **213개 전체 통과** |
| 커버리지 | **89%** |
| Ruff lint | 0 errors |
| Git commits | 7 |
| engine/ 인물 특정 용어 | **0건** |

---

## 검증 결과 (확실한 것들)

1. **POM**: current 38.6% 7/7 통과, fear-only 1.2%, uniform 0% (32배 분리)
2. **pyABC Model Selection**: Peter current=100%, Van Gogh current=84%
3. **Parameter Recovery**: PASS (true params in recovered box)
4. **환경 → 부인↑**: 방향성 일관
5. **도주율 29%**: 환경 무관

## 검증 결과 (교정된 것들)

- shapiq 상호작용: 변수 세트에 의존 (3개 vs 5개에서 구조 변동)
- Scale robustness: feature importance가 env scale에 따라 뒤집힘
- Canonical prevalence: rule family에 따라 15~65% (불안정)

---

## 구현 이력

### 엔진
- Hazard-driven 이벤트 (Poisson, competing risks, anchor window, deadline)
- Fast/slow state (HomeostasisRule 조건부, SlowState 비가역적)
- EnvironmentState (surveillance, crowd_pressure, 환경 동적 규칙)
- 동적 해상도 (Chronicle/Episode/Scene, tension trigger)
- POM 검증 체계 (7패턴 동시 필터)

### 분석
- SALib (Sobol, Morris), UMAP+HDBSCAN, Decision Tree
- shapiq (Shapley 상호작용), pyABC (파라미터 보정 + Model Selection)
- EMA Workbench PRIM (시나리오 디스커버리)
- Parameter Recovery Test

### 코드 품질
- 213 tests, 89% coverage
- ruff 0 errors
- engine/ 인물 비종속 (grep 0건)
- ODD Protocol 문서

### 인프라
- Git 7 commits
- main.py CLI (--person, --runs)
- pyproject.toml, requirements.txt
- 시각화 6개 (output/)

---

## 추가 완료 (자율 루프 최종)

- [x] mypy 17→0 errors
- [x] conftest.py 공유 fixture
- [x] POM 기반 pyABC: fear=7.3, love=6.2, hope=7.0
- [x] checkpoint 97%, temporal 100%, 전체 89%
- [x] 213 tests, ruff+mypy clean, 11 git commits

## 진행 중 / 미완료

- [ ] 렌더링 파이프라인 (비전 A) -- 방향 논의 필요
