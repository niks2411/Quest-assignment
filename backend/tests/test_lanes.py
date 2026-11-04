"""
Unit Tests for Lane Directions and Right-Hand Traffic Integrity
Validates that incoming and outgoing traffic on all 4 arms (North, South, East, West)
consistently stay on their respective halves of the roadbed separated by the yellow divider,
eliminating opposite-traffic lane contamination.
"""
import pytest
from simulation.vehicle import Vehicle
from simulation.junction import calculate_vehicle_pose, get_junction_dimensions


def test_east_arm_lane_separation():
    """East arm inbound is North (y < center_y), outbound is South (y > center_y)."""
    junction_half = get_junction_dimensions(lanes=2)
    center_y = 450.0  # 900 / 2

    # Inbound vehicle approaching from East (heading West)
    v_in = Vehicle(id="e_in", origin_direction="E", turn_intent="straight", position=100.0, lane=0)
    x_in, y_in, angle_in = calculate_vehicle_pose(v_in, lanes=2, junction_half=junction_half)
    
    # Must be on the Top half of East arm (above yellow divider)
    assert y_in < center_y, f"East inbound vehicle must be on top side (y < {center_y}), got {y_in}"
    assert angle_in == pytest.approx(3.14159, abs=0.01)

    # Outbound vehicle leaving towards East (heading East)
    # E.g. vehicle originating from West going straight to East
    v_out = Vehicle(id="e_out", origin_direction="W", turn_intent="straight", position=350.0, lane=0)
    x_out, y_out, angle_out = calculate_vehicle_pose(v_out, lanes=2, junction_half=junction_half)
    
    # Must be on the Bottom half of East arm (below yellow divider)
    assert y_out > center_y, f"East outbound vehicle must be on bottom side (y > {center_y}), got {y_out}"
    assert angle_out == pytest.approx(0.0, abs=0.01)

    # Inbound and Outbound MUST NOT share the same y coordinate
    assert abs(y_in - y_out) >= 16.0


def test_west_arm_lane_separation():
    """West arm inbound is South (y > center_y), outbound is North (y < center_y)."""
    junction_half = get_junction_dimensions(lanes=2)
    center_y = 450.0

    # Inbound vehicle approaching from West (heading East)
    v_in = Vehicle(id="w_in", origin_direction="W", turn_intent="straight", position=100.0, lane=0)
    x_in, y_in, angle_in = calculate_vehicle_pose(v_in, lanes=2, junction_half=junction_half)
    
    # Must be on Bottom half of West arm
    assert y_in > center_y, f"West inbound vehicle must be on bottom side (y > {center_y}), got {y_in}"
    assert angle_in == pytest.approx(0.0, abs=0.01)

    # Outbound vehicle leaving towards West (heading West)
    # E.g. vehicle originating from East going straight to West
    v_out = Vehicle(id="w_out", origin_direction="E", turn_intent="straight", position=350.0, lane=0)
    x_out, y_out, angle_out = calculate_vehicle_pose(v_out, lanes=2, junction_half=junction_half)
    
    # Must be on Top half of West arm
    assert y_out < center_y, f"West outbound vehicle must be on top side (y < {center_y}), got {y_out}"
    assert angle_out == pytest.approx(3.14159, abs=0.01)

    # Inbound and Outbound MUST NOT share the same y coordinate
    assert abs(y_in - y_out) >= 16.0


def test_north_and_south_lane_separation():
    """North and South arms maintain clean X separation across divider."""
    junction_half = get_junction_dimensions(lanes=2)
    center_x = 450.0

    # North inbound (heading South): Left of yellow (x < center_x)
    v_n_in = Vehicle(id="n_in", origin_direction="N", turn_intent="straight", position=100.0)
    x_n_in, _, _ = calculate_vehicle_pose(v_n_in, lanes=2, junction_half=junction_half)
    assert x_n_in < center_x

    # North outbound (heading North): Right of yellow (x > center_x)
    v_n_out = Vehicle(id="n_out", origin_direction="S", turn_intent="straight", position=350.0)
    x_n_out, _, _ = calculate_vehicle_pose(v_n_out, lanes=2, junction_half=junction_half)
    assert x_n_out > center_x

    # South inbound (heading North): Right of yellow (x > center_x)
    v_s_in = Vehicle(id="s_in", origin_direction="S", turn_intent="straight", position=100.0)
    x_s_in, _, _ = calculate_vehicle_pose(v_s_in, lanes=2, junction_half=junction_half)
    assert x_s_in > center_x

    # South outbound (heading South): Left of yellow (x < center_x)
    v_s_out = Vehicle(id="s_out", origin_direction="N", turn_intent="straight", position=350.0)
    x_s_out, _, _ = calculate_vehicle_pose(v_s_out, lanes=2, junction_half=junction_half)
    assert x_s_out < center_x
