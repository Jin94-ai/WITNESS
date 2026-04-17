# Witness

> 역사적 인물의 생애를 시뮬레이션으로 수천 번 돌리고, 결과 분포를 관측한다.
> "이 사람의 삶에서, 무엇이 갈라지는 순간이었는가?"

---

## 방법론

**Agent-based, hazard-driven, ensemble historical simulator**

- 이벤트가 고정 시점이 아니라 상태 기반 위험도(hazard)로 확률적 발생
- 수천 회 앙상블 실행, 결과 분포 관측
- 역사적 경로(ground truth)와 대조하여 시뮬레이션 검증 (Hindcasting)
- 파라미터 공간 지형도, 경로 클러스터링, 분기점 탐지

## 첫 인물: 베드로

예수의 마지막 50일. 성경 기록을 ground truth로 사용.

## 기술 스택

Python 3.11+ / Pydantic / pytest / SALib / UMAP / HDBSCAN

## 시작하기

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest
```

## 프로젝트 문서

| 문서 | 설명 |
|------|------|
| [DESIGN.md](DESIGN.md) | 설계도 (아키텍처, 방법론) |
| [CLAUDE.md](CLAUDE.md) | AI 행동 강령 |
