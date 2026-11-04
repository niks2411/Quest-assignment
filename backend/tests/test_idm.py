"""
Unit Tests for Intelligent Driver Model (IDM)
Validates car-following kinematics, safe headway braking, and boundary conditions.
"""
import pytest
from simulation.idm import IntelligentDriverModel


def test_free_road_acceleration():
    """On an empty road, a vehicle should accelerate towards desired speed."""
    idm = IntelligentDriverModel(s0=2.0, headway_time=1.5)
    
    # Stopped vehicle (speed = 0) with desired speed 14 m/s should accelerate at max_accel
    accel = idm.calculate_acceleration(
        current_speed=0.0,
        desired_speed=14.0,
        max_accel=2.0,
        comfort_decel=2.0,
        gap=None,
        leader_speed=None,
    )
    assert accel == pytest.approx(2.0, rel=1e-2)

    # When already at desired speed, acceleration should be near 0
    accel_at_v0 = idm.calculate_acceleration(
        current_speed=14.0,
        desired_speed=14.0,
        max_accel=2.0,
        comfort_decel=2.0,
        gap=None,
        leader_speed=None,
    )
    assert accel_at_v0 == pytest.approx(0.0, abs=0.1)


def test_deceleration_approaching_slower_vehicle():
    """Approaching a slower car closely should cause smooth deceleration."""
    idm = IntelligentDriverModel(s0=2.0, headway_time=1.5)
    
    # Ego speed = 15 m/s, Leader speed = 5 m/s, Gap = 10 m
    accel = idm.calculate_acceleration(
        current_speed=15.0,
        desired_speed=15.0,
        max_accel=2.0,
        comfort_decel=2.0,
        gap=10.0,
        leader_speed=5.0,
    )
    # Must decelerate strongly
    assert accel < 0.0


def test_stopped_obstacle_safe_distance():
    """Approaching a stopped car or red light should trigger braking to stop before s0."""
    idm = IntelligentDriverModel(s0=2.0, headway_time=1.5)
    
    # Ego speed = 10 m/s, lead speed = 0, gap = 5 m
    accel = idm.calculate_acceleration(
        current_speed=10.0,
        desired_speed=14.0,
        max_accel=2.0,
        comfort_decel=2.0,
        gap=5.0,
        leader_speed=0.0,
    )
    assert accel < -1.5


def test_critical_small_gap_protection():
    """Extremely small gaps must not produce NaN, inf, or crash."""
    idm = IntelligentDriverModel(s0=2.0, headway_time=1.5)
    
    accel = idm.calculate_acceleration(
        current_speed=5.0,
        desired_speed=14.0,
        max_accel=2.0,
        comfort_decel=2.0,
        gap=0.05,
        leader_speed=0.0,
    )
    # Should apply maximum emergency braking clamped to limit
    assert accel == pytest.approx(-idm.max_emergency_decel, abs=0.1)
