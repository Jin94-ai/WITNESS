"""Tests for RunLog (Run Experience Layer)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from engine.observer.run_log import (
    PIPELINE_STEP_LABELS, PipelineStep, RunLog, StepTimer,
    make_pipeline_steps, render_run_log_md,
)

ROOT = Path(__file__).resolve().parents[2]


def test_pipeline_step_labels_are_six():
    assert len(PIPELINE_STEP_LABELS) == 6
    for label, plain in PIPELINE_STEP_LABELS:
        assert label
        assert plain  # 한국어 라벨


def test_make_pipeline_steps_default_durations_zero():
    steps = make_pipeline_steps()
    assert len(steps) == 6
    assert all(s.duration_ms == 0 for s in steps)
    assert all(s.status == "completed" for s in steps)
    assert [s.step_no for s in steps] == [1, 2, 3, 4, 5, 6]


def test_make_pipeline_steps_with_durations():
    steps = make_pipeline_steps([10, 20, 30, 40, 50, 60])
    durations = [s.duration_ms for s in steps]
    assert durations == [10, 20, 30, 40, 50, 60]


def test_pipeline_step_to_dict():
    s = PipelineStep(step_no=1, label="simulation", plain_label="시뮬레이션",
                     status="completed", duration_ms=100)
    d = s.to_dict()
    assert d["step_no"] == 1
    assert d["plain_label"] == "시뮬레이션"
    assert d["duration_ms"] == 100


def test_run_log_to_dict_has_required_fields():
    log = RunLog(
        anchor_id="test", seed=0, ticks=200, agents=12, groups=3,
        story_threads_found=4, story_seeds_generated=4,
        episode_outlines_generated=1, audit_failures=0,
        pipeline_steps=make_pipeline_steps(),
        started_at_iso="2026-05-08T12:00:00",
        runtime_seconds=0.5,
    )
    d = log.to_dict()
    assert d["schema_version"] == "run_log_v1"
    for field in ("anchor_id", "seed", "ticks", "agents", "groups",
                  "story_threads_found", "story_seeds_generated",
                  "episode_outlines_generated", "audit_failures",
                  "pipeline_steps", "runtime_seconds"):
        assert field in d


def test_run_log_md_renders_korean():
    log = RunLog(
        anchor_id="peter_scarcity_baseline", seed=0, ticks=200, agents=12,
        groups=3, story_threads_found=4, story_seeds_generated=4,
        episode_outlines_generated=1, audit_failures=0,
        pipeline_steps=make_pipeline_steps([10, 20, 30, 40, 50, 60]),
        started_at_iso="2026-05-08T12:00:00",
        runtime_seconds=0.5,
    )
    md = render_run_log_md(log)
    # 핵심 한국어 라벨 포함
    assert "실행 요약" in md
    assert "파이프라인" in md
    assert "peter_scarcity_baseline" in md
    # 6 step plain labels 모두 포함
    for _, plain_label in PIPELINE_STEP_LABELS:
        assert plain_label in md
    # 200ms 이상 duration이 표시되어 있어야
    assert "ms" in md


def test_step_timer_records_durations():
    timer = StepTimer()
    with timer.step("simulation"):
        time.sleep(0.001)  # 1ms
    with timer.step("pressure"):
        time.sleep(0.001)
    durations = timer.durations_ms()
    assert len(durations) == 6  # PIPELINE_STEP_LABELS count
    # First two should be > 0
    assert durations[0] >= 1
    assert durations[1] >= 1
    # Untimed steps remain 0
    assert durations[2] == 0


def test_run_log_serializable():
    log = RunLog(
        anchor_id="test", seed=0, ticks=200, agents=12, groups=3,
        story_threads_found=4, story_seeds_generated=4,
        episode_outlines_generated=1, audit_failures=0,
        pipeline_steps=make_pipeline_steps(),
        started_at_iso="2026-05-08T12:00:00",
        runtime_seconds=0.5,
    )
    json.dumps(log.to_dict(), ensure_ascii=False)


def test_run_log_module_no_hardcoded_hero():
    src = (ROOT / "engine/observer/run_log.py").read_text(encoding="utf-8")
    for forbidden in ("peter", "Peter", "베드로", "vangogh"):
        assert forbidden not in src, f"hero '{forbidden}' in run_log source"
