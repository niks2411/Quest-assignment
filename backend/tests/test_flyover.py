"""
Automated Elevated Flyover Viaduct Tests
Audits independence of flyover bypass from ground signals and queues.
"""
import pytest
from simulation.engine import SimulationEngine
from simulation.vehicle import Vehicle
from models.scenario import ScenarioConfig


def test_flyover_vehicles_ignore_ground_signals():
    """Flyover vehicles traverse continuously without stopping for ground red lights."""
    config = ScenarioConfig(
        flyover_enabled=True,
        traffic_signal_green=10.0,
        traffic_signal_yellow=4.0,
    )
    engine = SimulationEngine(scenario=config, seed=99)
    
    # Place vehicle on flyover
    v_flyover = Vehicle(
        id="fly_1",
        on_flyover=True,
        origin_direction="N",
        turn_intent="straight",
        position=100.0,
        speed=18.0,
        current_road_id="flyover_NS",
    )
    engine.vehicles["fly_1"] = v_flyover

    # Set ground NS signal to RED (EW is Green)
    engine.traffic_light.current_phase = 2  # EW Green, NS Red
    
    for _ in range(60):  # 3 seconds
        engine.step()
        # Flyover vehicle must maintain high speed and never stop
        assert v_flyover.speed > 10.0, f"Flyover vehicle slowed down unexpectedly! Speed = {v_flyover.speed}"


def test_flyover_vehicles_excluded_from_ground_queues():
    """Flyover vehicles are never counted in directional ground junction queues."""
    config = ScenarioConfig(flyover_enabled=True)
    engine = SimulationEngine(scenario=config, seed=10)

    # Crawling vehicle on flyover
    v_flyover = Vehicle(
        id="fly_slow",
        on_flyover=True,
        origin_direction="N",
        position=150.0,
        speed=0.5,
        current_road_id="flyover_NS",
    )
    engine.vehicles["fly_slow"] = v_flyover

    metrics = engine.metrics_tracker.calculate_metrics(
        list(engine.vehicles.values()), engine.roads, engine.sim_time
    )

    # North queue must remain 0
    assert metrics["queues"]["N"] == 0
    assert metrics["total_queue"] == 0
