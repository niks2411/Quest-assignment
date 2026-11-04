"""
Unit & Integration Tests for Simulation Engine
"""
import pytest
from simulation.engine import SimulationEngine
from models.scenario import SCENARIO_PRESETS, ScenarioConfig


def test_engine_initialization():
    engine = SimulationEngine(scenario=SCENARIO_PRESETS["normal"])
    state = engine.get_state()
    assert state["sim_time"] == 0.0
    assert state["is_running"] is False
    assert state["vehicle_count"] == 0
    assert "metrics" in state
    assert "traffic_light" in state


def test_engine_simulation_steps():
    engine = SimulationEngine(scenario=SCENARIO_PRESETS["normal"])
    engine.start()
    
    # Run 100 timesteps (5 seconds simulated)
    for _ in range(100):
        state = engine.step()
    
    assert state["sim_time"] == pytest.approx(5.0, abs=1e-2)
    # Should have spawned vehicles
    assert state["vehicle_count"] > 0
    assert len(state["vehicles"]) == state["vehicle_count"]
    
    # Verify vehicle coordinates are finite numbers
    for v in state["vehicles"]:
        assert isinstance(v["x"], (int, float))
        assert isinstance(v["y"], (int, float))
        assert not (v["x"] != v["x"])  # NaN check
        assert not (v["y"] != v["y"])


def test_flyover_scenario():
    engine = SimulationEngine(scenario=SCENARIO_PRESETS["flyover_bypass"])
    engine.start()
    
    # Run 200 timesteps (10 seconds simulated)
    has_flyover_vehicle = False
    for _ in range(200):
        state = engine.step()
        if any(v.get("on_flyover") for v in state["vehicles"]):
            has_flyover_vehicle = True
            break
            
    assert has_flyover_vehicle is True
