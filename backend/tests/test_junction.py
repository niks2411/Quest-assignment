"""
Automated Junction Conflict & Arbitration Tests
Audits left-turn conflict yielding, anti-gridlock box clearance,
and merging safety inside 4-way intersection.
"""
import pytest
from simulation.engine import SimulationEngine
from simulation.vehicle import Vehicle


def test_left_turn_yields_to_oncoming_through_traffic():
    """Vehicle attempting a left turn yields at stop line when oncoming through traffic is present."""
    engine = SimulationEngine(seed=55)
    
    # North vehicle wanting to turn left (into East arm)
    v_left = Vehicle(
        id="v_turn_left",
        origin_direction="N",
        turn_intent="left",
        position=215.0,
        speed=8.0,
        current_road_id="road_N_in",
    )
    # Oncoming South vehicle going straight through intersection
    v_oncoming = Vehicle(
        id="v_thru",
        origin_direction="S",
        turn_intent="straight",
        position=210.0,
        speed=14.0,
        current_road_id="road_S_in",
    )
    
    engine.vehicles["v_turn_left"] = v_left
    engine.vehicles["v_thru"] = v_oncoming

    # Signal set to NS Green
    engine.traffic_light.current_phase = 0
    engine.traffic_light.phase_time = 0.0

    # Advance 20 steps (1 second)
    for _ in range(20):
        engine.step()

    # The turning vehicle must yield at stop line (pos <= 220.0m) until oncoming car clears
    assert v_left.position <= 220.0, f"Turning vehicle entered junction without yielding! Pos = {v_left.position}"
    # Oncoming vehicle proceeded through
    assert v_oncoming.position > 220.0


def test_anti_gridlock_box_rule():
    """Vehicle on green does not enter intersection if exit lane is blocked."""
    engine = SimulationEngine(seed=88)
    
    # Vehicle blocked right at junction exit (pos = 285m), stationary due to obstruction ahead
    v_blocker = Vehicle(
        id="blocker",
        origin_direction="N",
        turn_intent="straight",
        position=285.0,
        speed=0.0,
        max_speed=0.0,  # Holds stationary to simulate downstream jam
        current_road_id="road_N_in",
    )
    # Approaching vehicle on green
    v_approaching = Vehicle(
        id="approacher",
        origin_direction="N",
        turn_intent="straight",
        position=215.0,
        speed=8.0,
        current_road_id="road_N_in",
    )
    
    engine.vehicles["blocker"] = v_blocker
    engine.vehicles["approacher"] = v_approaching
    
    engine.traffic_light.current_phase = 0  # Green
    engine.traffic_light.phase_time = 0.0

    for _ in range(30):
        engine.step()

    # Approacher must hold at stop line (pos <= 220.0m) rather than blocking the box
    assert v_approaching.position <= 220.0, (
        f"Vehicle entered junction despite blocked exit! Pos = {v_approaching.position}"
    )
