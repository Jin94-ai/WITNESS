"""Run Log — Run Experience Layer.

Per `WITNESS_PORTFOLIO_DEMO_PIPELINE_PLAN` Story Assembly directive.

실행 로그 모델 — *시뮬레이션을 실제로 돌렸다는 느낌*을 주기 위한 산출물.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineStep:
    """파이프라인 한 단계."""
    step_no: int
    label: str               # 영어 (내부)
    plain_label: str         # 한국어 (UI)
    status: str              # "completed" / "skipped" / "failed"
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "step_no": self.step_no,
            "label": self.label,
            "plain_label": self.plain_label,
            "status": self.status,
            "duration_ms": self.duration_ms,
        }


@dataclass(frozen=True)
class RunLog:
    anchor_id: str
    seed: int
    ticks: int
    agents: int
    groups: int
    story_threads_found: int
    story_seeds_generated: int
    episode_outlines_generated: int
    audit_failures: int
    pipeline_steps: tuple[PipelineStep, ...]
    started_at_iso: str
    runtime_seconds: float

    def to_dict(self) -> dict:
        return {
            "schema_version": "run_log_v1",
            "anchor_id": self.anchor_id,
            "seed": self.seed,
            "ticks": self.ticks,
            "agents": self.agents,
            "groups": self.groups,
            "story_threads_found": self.story_threads_found,
            "story_seeds_generated": self.story_seeds_generated,
            "episode_outlines_generated": self.episode_outlines_generated,
            "audit_failures": self.audit_failures,
            "pipeline_steps": [s.to_dict() for s in self.pipeline_steps],
            "started_at_iso": self.started_at_iso,
            "runtime_seconds": round(self.runtime_seconds, 3),
        }


# ---------------------------------------------------------------------------
# Pipeline step labels (6 steps per directive)
# ---------------------------------------------------------------------------

PIPELINE_STEP_LABELS: tuple[tuple[str, str], ...] = (
    ("simulation",       "세계 시뮬레이션 실행"),
    ("pressure",         "압력 변화 관찰"),
    ("threads",          "이야기 흐름 채굴"),
    ("episode",          "에피소드 개요 조립"),
    ("seed_cards",       "이야기 씨앗 카드 생성"),
    ("evidence",         "근거 / 검증 패키징"),
)


def make_pipeline_steps(durations_ms: list[int] | None = None) -> tuple[PipelineStep, ...]:
    """Construct the 6-step pipeline label list. Durations optional."""
    if durations_ms is None:
        durations_ms = [0] * len(PIPELINE_STEP_LABELS)
    out: list[PipelineStep] = []
    for i, ((label, plain_label), dur) in enumerate(zip(PIPELINE_STEP_LABELS, durations_ms), start=1):
        out.append(PipelineStep(
            step_no=i,
            label=label,
            plain_label=plain_label,
            status="completed",
            duration_ms=dur,
        ))
    return tuple(out)


def render_run_log_md(log: RunLog) -> str:
    steps_block = "\n".join(
        f"{s.step_no}. {s.plain_label} ({s.duration_ms} ms)" if s.duration_ms > 0
        else f"{s.step_no}. {s.plain_label}"
        for s in log.pipeline_steps
    )
    return f"""# WITNESS Demo Run Log

> 시뮬레이션을 실행했고, 다음 결과가 나왔습니다.

## 실행 요약

- 시나리오: `{log.anchor_id}`
- Seed: `{log.seed}`
- 시간 단계: {log.ticks}
- 인물: {log.agents}명
- 집단: {log.groups}개
- 발견된 이야기 흐름: **{log.story_threads_found}**
- 이야기 씨앗: **{log.story_seeds_generated}**
- 에피소드 개요: **{log.episode_outlines_generated}**
- 검증 실패: **{log.audit_failures}**
- 시작 시각: `{log.started_at_iso}`
- 총 실행 시간: **{log.runtime_seconds}s**

## 파이프라인

{steps_block}

---

*이 로그는 `scripts/narrative/run_portfolio_demo.py` 실행 시 자동 생성됩니다.*
"""


# ---------------------------------------------------------------------------
# Stopwatch helper for orchestrator integration
# ---------------------------------------------------------------------------

class StepTimer:
    """Context manager-style step timer for orchestrator usage.

    Usage:
        timer = StepTimer()
        with timer.step("simulation"):
            # do work
        durations_ms = timer.durations_ms()
    """
    def __init__(self) -> None:
        self._durations: dict[str, int] = {}
        self._current_label: str | None = None
        self._current_start: float = 0.0

    def step(self, label: str):
        return _StepContext(self, label)

    def _enter(self, label: str) -> None:
        self._current_label = label
        self._current_start = time.time()

    def _exit(self) -> None:
        if self._current_label is None:
            return
        dur_ms = int((time.time() - self._current_start) * 1000)
        self._durations[self._current_label] = dur_ms
        self._current_label = None

    def durations_ms(self) -> list[int]:
        """Returns durations in PIPELINE_STEP_LABELS order."""
        return [
            self._durations.get(label, 0)
            for label, _ in PIPELINE_STEP_LABELS
        ]


class _StepContext:
    def __init__(self, parent: StepTimer, label: str) -> None:
        self._parent = parent
        self._label = label

    def __enter__(self) -> "_StepContext":
        self._parent._enter(self._label)
        return self

    def __exit__(self, *args: Any) -> None:
        self._parent._exit()
