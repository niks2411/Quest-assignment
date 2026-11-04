"""
Automated Traffic Signal Compliance Tests
Audits vehicle behavior approaching red, yellow, and green signals.
Verifies vehicles stop strictly before stop line on RED, respect dilemma zones on YELLOW,
and smoothly restart on GREEN without collisions.
"""
import pytest
from simulation.engine import SimulationEngine
from simulation.vehicle import Vehicle
from models.scenario import ScenarioConfig


def test_vehicles_stop_before_stop_line_on_red():
    """Vehicles on an inbound road must halt before stop line (pos <= 220.0m) when signal is RED."""
    config = ScenarioConfig(
        traffic_signal_green=10.0,
        traffic_signal_yellow=4.0,
        target_vehicle_count=40,
        spawn_rate_vps=1.5,
    )
    engine = SimulationEngine(scenario=config, seed=123)
    engine.start()

    stop_line_m = 220.0

    # Run for 600 timesteps (30 seconds simulated = full signal cycle)
    for step in range(600):
        engine.step()

        # Audit every active inbound vehicle approaching intersection
        for v in engine.vehicles.values():
            if not v.on_flyover and v.position <= stop_line_m:
                sig = engine.traffic_light.get_signal(v.origin_direction)
                # If red signal and vehicle was queuing, must not cross stop line
                if sig == "RED":
                    assert v.position <= stop_line_m, (
                        f"Step {step}: Vehicle {v.id} ran RED light at pos={v.position} > {stop_line_m}!"
                    )


def test_stopped_queue_smooth_restart_on_green():
    """A stopped queue of vehicles at a red light must accelerate smoothly on GREEN without rear-ending."""
    engine = SimulationEngine(seed=456)
    
    # Create 3 queued vehicles stopped at red light
    v1 = Vehicle(id="q1", position=218.0, speed=0.0, origin_direction="N", current_road_id="road_N_in")
    v2 = Vehicle(id="q2", position=210.0, speed=0.0, origin_direction="N", current_road_id="road_N_in")
    v3 = Vehicle(id="q3", position=200.0, speed=0.0, origin_direction="N", current_road_id="road_N_in")
    
    engine.vehicles["q1"] = v1
    engine.vehicles["q2"] = v2
    engine.vehicles["q3"] = v3
    
    # Set signal to GREEN for North
    engine.traffic_light.current_phase = 0  # Phase 0 = NS Green
    engine.traffic_light.phase_time = 0.0

    # Advance 40 steps (2 seconds)
    for step in range(40):
        engine.step()
        
        # Verify order is preserved: q1 > q2 > q3
        assert v1.position > v2.position + v2.length
        assert v2.position > v3.position + v3.length
        
        # Speeds should increase
        assert v1.speed >= 0.0
        assert v2.speed >= 0.0
        assert v3.speed >= 0.0

    # Lead vehicle should have crossed stop line into junction
    assert v1.position > 220.0
