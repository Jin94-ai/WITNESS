"""환경 동적 변화 규칙.

tick 진행에 따라 환경이 자체적으로 변화한다.
에이전트 규칙과 별도로, runner에서 매 tick 호출.
"""

from __future__ import annotations

import math

from engine.core.environment import EnvironmentState
from engine.core.state import clamp


class EnvironmentDynamicsRule:
    """환경의 자연 동적 변화.

    - 유월절 접근 시 crowd_pressure 증가 (tick 100~150 구간)
    - 체포 후 threat_level 유지, 이후 점진 감소
    - 밤에 surveillance 감소, 낮에 증가
    - 고립 상태는 시간에 따라 서서히 해소
    """

    def __init__(
        self,
        crowd_peak_tick: int = 130,
        crowd_peak_width: int = 30,
        crowd_peak_amplitude: float = 0.03,
        night_surveillance_drop: float = 0.02,
        isolation_decay: float = 0.005,
        threat_decay: float = 0.002,
    ) -> None:
        self.crowd_peak_tick = crowd_peak_tick
        self.crowd_peak_width = crowd_peak_width
        self.crowd_peak_amplitude = crowd_peak_amplitude
        self.night_surveillance_drop = night_surveillance_drop
        self.isolation_decay = isolation_decay
        self.threat_decay = threat_decay

    def apply(self, env: EnvironmentState, tick: int) -> EnvironmentState:
        """환경 상태를 갱신한다. 새 EnvironmentState를 반환."""
        crowd = env.crowd_pressure
        surv = env.surveillance
        threat = env.threat_level
        isolation = env.isolation_degree

        # 유월절 접근: 가우시안 형태로 crowd_pressure 증가
        dist = abs(tick - self.crowd_peak_tick)
        if dist < self.crowd_peak_width * 2:
            crowd_boost = self.crowd_peak_amplitude * math.exp(
                -(dist ** 2) / (2 * self.crowd_peak_width ** 2)
            )
            crowd = clamp(crowd + crowd_boost)

        # 밤/낮 cycle: surveillance 변동
        hour_phase = (tick % 12) / 12.0
        circadian = math.sin(hour_phase * 2 * math.pi)
        if circadian > 0:
            # 밤: surveillance 감소
            surv = clamp(surv - circadian * self.night_surveillance_drop)
        else:
            # 낮: surveillance 약간 증가
            surv = clamp(surv - circadian * self.night_surveillance_drop * 0.5)

        # threat 자연 감소
        if threat > 3.0:
            threat = clamp(threat - self.threat_decay)

        # isolation 자연 해소
        if isolation > 0:
            isolation = clamp(isolation - self.isolation_decay)

        return EnvironmentState(
            crowd_pressure=crowd,
            surveillance=surv,
            threat_level=threat,
            time_pressure=env.time_pressure,
            isolation_degree=isolation,
        )
