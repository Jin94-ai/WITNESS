# AI-Hub 023 Data — Local Path Note

> Day 1 작업 시점 (2026-05-12) 상태 기록.

---

## 1. 현재 위치 (Lee 다운로드 그대로)

```
data/023.방송 콘텐츠 대본 요약 데이터/01.데이터/
├── 1.Training/
│   ├── 라벨링데이터/TL1.zip   (114M, 84,382 entries)
│   └── 원천데이터/TS1.zip     (100M, 84,382 entries)
└── 2.Validation/
    ├── 라벨링데이터/VL1.zip   (14M, 10,018 entries)
    └── 원천데이터/VS1.zip     (12M, 10,000 entries)
```

**한국어 경로 유지** — Windows symlink는 관리자 권한 필요하므로 그대로 두고 loader에서 path constant로 alias.

`.gitignore`로 보호됨 (.gitignore line 137-142 `data/aihub_023/` + `data/023.방송 콘텐츠 대본 요약 데이터/`).

---

## 2. Plan §5 vs 현실

`docs/witness_drama_mining_plan.md` §5는 `data/aihub_023/` 경로를 가정하지만, Lee 다운로드는 한국어 dir 그대로.

**해결**: `drama_mining/data/loader.py` (Day 2 작성)에서:

```python
AIHUB_023_ROOT_CANDIDATES = [
    Path("data/aihub_023/01.데이터"),                              # plan §5 가정 경로
    Path("data/023.방송 콘텐츠 대본 요약 데이터/01.데이터"),       # 현실 경로
]
```

먼저 존재하는 것을 사용. 둘 다 없으면 명확한 에러.

---

## 3. 라이선스

`docs/data_card.md` 참조. **Raw 절대 commit 금지.** 학습 산출 (model card / metrics) 공개 시 인용 의무.
