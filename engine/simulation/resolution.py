"""동적 해상도 시스템.

저화질(Chronicle)로 전체가 돌아가다가, 특정 조건에서 고화질(Scene)로 전환.

전환 기준:
- anchor_window: 미리 지정된 고해상도 구간
- tension_trigger: 에이전트 내부 긴장도가 임계값을 넘으면 자동 전환
- event_density: hazard 이벤트가 빠르게 연속 발동하면 전환

저화질: dt=1 (기본), 규칙 적용 간소화
고화질: dt=1이지만 더 세밀한 스냅샷 + 추가 규칙 가능
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from engine.core.state import AgentState


class ResolutionTier(str, Enum):
    """해상도 등급."""
    CHRONICLE = "chronicle"  # 저화질: 일~주 단위 요약
    EPISODE = "episode"      # 중간: 시간~일 단위
    SCENE = "scene"          # 고화질: 분~시간 단위, 세밀한 상태 추적


class AnchorWindow(BaseModel):
    """미리 지정된 고해상도 구간."""
    start_tick: int = Field(ge=0)
    end_tick: int = Field(ge=0)
    tier: ResolutionTier = Field(default=ResolutionTier.SCENE)
    description: str = ""


class ResolutionConfig(BaseModel):
    """동적 해상도 설정."""
    anchor_windows: list[AnchorWindow] = Field(default_factory=list)
    tension_threshold: float = Field(
        default=7.0, description="긴장도 이 이상이면 자동 고해상도"
    )
    event_density_window: int = Field(
        default=5, description="최근 N tick 내 이벤트 수로 밀도 계산"
    )
    event_density_threshold: int = Field(
        default=2, description="밀도가 이 이상이면 고해상도"
    )
    default_tier: ResolutionTier = Field(default=ResolutionTier.CHRONICLE)


def compute_tension(state: AgentState) -> float:
    """에이전트의 현재 긴장도를 계산한다.

    긴장도 = 감정 극단값들의 조합.
    높은 fear + 높은 confusion + 높은 fatigue = 높은 긴장.
    """
    e = state.emotions
    p = state.physical

    # 각 요인의 기여 (0~10 범위)
    fear_contrib = e.fear * 0.3
    confusion_contrib = e.confusion * 0.2
    grief_contrib = e.grief * 0.2
    fatigue_contrib = p.fatigue * 0.15

    # 감정 간 갈등 (love와 fear가 동시에 높으면 긴장)
    conflict = min(e.love, e.fear) * 0.15

    return min(fear_contrib + confusion_contrib + grief_contrib + fatigue_contrib + conflict, 10.0)


class ResolutionEngine:
    """동적 해상도 결정 엔진."""

    def __init__(self, config: ResolutionConfig) -> None:
        self._config = config
        self._recent_event_ticks: list[int] = []

    def determine_tier(self, tick: int, state: AgentState) -> ResolutionTier:
        """현재 tick의 해상도 등급을 결정한다."""
        # 1. anchor window 체크 (최우선)
        for aw in self._config.anchor_windows:
            if aw.start_tick <= tick <= aw.end_tick:
                return aw.tier

        # 2. 긴장도 체크
        tension = compute_tension(state)
        if tension >= self._config.tension_threshold:
            return ResolutionTier.SCENE

        # 3. 이벤트 밀도 체크
        recent = [
            t for t in self._recent_event_ticks
            if t > tick - self._config.event_density_window
        ]
        if len(recent) >= self._config.event_density_threshold:
            return ResolutionTier.EPISODE

        return self._config.default_tier

    def record_event(self, tick: int) -> None:
        """이벤트 발동을 기록한다 (밀도 계산용)."""
        self._recent_event_ticks.append(tick)
        # 오래된 기록 정리
        cutoff = tick - self._config.event_density_window * 2
        self._recent_event_ticks = [
            t for t in self._recent_event_ticks if t > cutoff
        ]

    def should_snapshot(self, tier: ResolutionTier) -> bool:
        """이 해상도에서 상태 스냅샷을 저장해야 하는지."""
        return tier in (ResolutionTier.SCENE, ResolutionTier.EPISODE)

    @property
    def config(self) -> ResolutionConfig:
        return self._config
