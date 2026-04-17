"""EnvironmentDynamicsRule 테스트."""

from engine.core.environment import EnvironmentState
from engine.rules.environment import EnvironmentDynamicsRule


class TestEnvironmentDynamics:
    def test_crowd_increases_near_peak(self):
        """유월절(peak tick) 근처에서 crowd_pressure가 증가한다."""
        rule = EnvironmentDynamicsRule(crowd_peak_tick=130, crowd_peak_width=30)
        env = EnvironmentState(crowd_pressure=3.0)
        result = rule.apply(env, tick=130)
        assert result.crowd_pressure > 3.0

    def test_crowd_stable_far_from_peak(self):
        """peak에서 멀면 crowd 변화가 거의 없다."""
        rule = EnvironmentDynamicsRule(crowd_peak_tick=130, crowd_peak_width=30)
        env = EnvironmentState(crowd_pressure=3.0)
        result = rule.apply(env, tick=400)
        assert abs(result.crowd_pressure - 3.0) < 0.01

    def test_threat_decays(self):
        """threat_level이 자연 감소한다."""
        rule = EnvironmentDynamicsRule(threat_decay=0.1)
        env = EnvironmentState(threat_level=8.0)
        result = rule.apply(env, tick=50)
        assert result.threat_level < 8.0

    def test_threat_stays_at_baseline(self):
        """threat_level이 3.0 이하면 감소하지 않는다."""
        rule = EnvironmentDynamicsRule()
        env = EnvironmentState(threat_level=2.0)
        result = rule.apply(env, tick=50)
        assert result.threat_level == 2.0

    def test_isolation_decays(self):
        """isolation_degree가 자연 해소된다."""
        rule = EnvironmentDynamicsRule(isolation_decay=0.1)
        env = EnvironmentState(isolation_degree=5.0)
        result = rule.apply(env, tick=50)
        assert result.isolation_degree < 5.0

    def test_surveillance_varies_by_time(self):
        """밤/낮에 따라 surveillance가 다르다."""
        rule = EnvironmentDynamicsRule()
        env = EnvironmentState(surveillance=5.0)
        day_result = rule.apply(env, tick=3)  # 낮
        night_result = rule.apply(env, tick=9)  # 밤
        assert day_result.surveillance != night_result.surveillance

    def test_multiple_ticks_accumulate(self):
        """여러 tick 적용하면 변화가 누적된다."""
        rule = EnvironmentDynamicsRule()
        env = EnvironmentState(crowd_pressure=3.0, threat_level=8.0, isolation_degree=5.0)
        for tick in range(100, 200):
            env = rule.apply(env, tick)
        # crowd_pressure는 peak(130) 근처이므로 증가했을 것
        assert env.crowd_pressure > 3.0
        # threat는 감소
        assert env.threat_level < 8.0
        # isolation은 감소
        assert env.isolation_degree < 5.0
