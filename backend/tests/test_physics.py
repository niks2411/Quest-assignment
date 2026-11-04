"""
Unit Tests for Vehicle Kinematics and Physics
"""
import pytest
from simulation.vehicle import Vehicle
from simulation.physics import integrate_kinematics, check_collision


def test_kinematics_acceleration():
    v = Vehicle(id="test_1", vehicle_type="car", position=0.0, speed=0.0)
    # Accelerate at 2 m/s^2 for 1 second
    integrate_kinematics(v, target_acceleration=2.0, dt=1.0)
    
    assert v.speed == pytest.approx(2.0, abs=1e-3)
    # Distance: (0 + 2)/2 * 1 = 1.0 m
    assert v.position == pytest.approx(1.0, abs=1e-3)
    assert v.status == "accelerating"


def test_speed_cannot_be_negative():
    v = Vehicle(id="test_2", vehicle_type="car", position=10.0, speed=1.0)
    # Strong braking for 2 seconds
    integrate_kinematics(v, target_acceleration=-5.0, dt=2.0)
    
    assert v.speed == 0.0
    assert v.status == "stopped"


def test_max_speed_clamped():
    v = Vehicle(id="test_3", vehicle_type="car", position=0.0, speed=16.0)
    integrate_kinematics(v, target_acceleration=5.0, dt=2.0)
    
    assert v.speed <= v.max_speed


def test_collision_detection():
    v1 = Vehicle(id="lead", current_road_id="road_N_in", lane=0, position=30.0, length=4.5)
    v2 = Vehicle(id="follower", current_road_id="road_N_in", lane=0, position=28.0, length=4.5)
    
    # Gap = 30.0 - 4.5 - 28.0 = -2.5 (overlap!)
    assert check_collision(v1, v2) is True

    # Move follower back to safe distance: gap = 30.0 - 4.5 - 20.0 = 5.5m
    v2.position = 20.0
    assert check_collision(v1, v2) is False
