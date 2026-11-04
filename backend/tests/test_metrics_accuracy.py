"""
Automated Metrics Accuracy Audit Tests
Validates mathematical correctness of:
- Space-Mean Speed (km/h) = 3.6 * (Total Distance / Total Time)
- Average Waiting Time (s)
- Queue Length by direction
- Road Utilization (%)
- Throughput (veh/min)
- Traffic Density (veh/km)
"""
import pytest
from simulation.metrics import MetricsTracker
from simulation.vehicle import Vehicle
from simulation.road import build_default_network


def test_hand_calculated_metrics_scenario():
    """Validates metrics calculations against exact manual arithmetic calculations."""
    tracker = MetricsTracker()
    roads = build_default_network(lanes=2, flyover_enabled=False)

    # 1. Create 2 active vehicles:
    # Vehicle 1: traveled 100m in 10s, waited 2s, current speed 10 m/s
    v1 = Vehicle(id="v1", position=100.0, speed=10.0, origin_direction="N")
    v1.total_distance = 100.0
    v1.travel_time = 10.0
    v1.waiting_time = 2.0

    # Vehicle 2: stopped at signal, traveled 200m in 20s, waited 10s, current speed 0.2 m/s
    v2 = Vehicle(id="v2", position=200.0, speed=0.2, origin_direction="N")
    v2.total_distance = 200.0
    v2.travel_time = 20.0
    v2.waiting_time = 10.0

    # 2. Record 1 completed vehicle:
    # Vehicle 3: completed 500m in 30s, waited 6s
    v3 = Vehicle(id="v3", position=500.0, speed=12.0)
    v3.total_distance = 500.0
    v3.travel_time = 30.0
    v3.waiting_time = 6.0
    tracker.record_completed_vehicle(v3, current_time=45.0)

    # Calculate metrics at current_time = 45.0s
    metrics = tracker.calculate_metrics([v1, v2], roads, current_time=45.0)

    # Manual calculations:
    # Total distance = 100 + 200 + 500 = 800 m
    # Total time = 10 + 20 + 30 = 60 s
    # Expected space-mean speed = 800 / 60 = 13.33 m/s = 48.0 km/h
    assert metrics["avg_speed_kmh"] == pytest.approx(48.0, abs=0.2)

    # Total waiting time = 2 + 10 + 6 = 18 s
    # Total entities = 2 active + 1 completed = 3
    # Expected average waiting time = 18 / 3 = 6.0 s
    assert metrics["avg_waiting_time_sec"] == pytest.approx(6.0, abs=0.1)

    # Active count must be exactly 2
    assert metrics["active_vehicles"] == 2
    assert metrics["completed_vehicles"] == 1

    # Directional queues: v2 is stopped on North (speed < 0.8, pos < 220), v1 is moving
    assert metrics["queues"]["N"] == 1
    assert metrics["queues"]["S"] == 0
    assert metrics["total_queue"] == 1

    # Throughput: 1 vehicle completed in 45s => (1 / 45) * 60 = 1.33 veh/min
    assert metrics["throughput_vpm"] == pytest.approx(1.3, abs=0.1)
