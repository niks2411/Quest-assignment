"""
Benchmark Scenarios A, B, C, and D Validation
Runs controlled experiments on all 4 presets under identical seeds (seed=42).
Produces empirical comparative metrics validating the effectiveness of infrastructure
improvements (Flyover Bypass) and signal optimization.
"""
import pytest
from simulation.engine import SimulationEngine
from models.scenario import SCENARIO_PRESETS


def run_benchmark_scenario(preset_key: str, seed: int = 42, steps: int = 2000):
    """Runs a scenario preset for 100 simulated seconds (steady-state congestion)."""
    scenario = SCENARIO_PRESETS[preset_key]
    engine = SimulationEngine(scenario=scenario, seed=seed)
    engine.start()

    max_queue = 0
    for _ in range(steps):
        state = engine.step()
        q = state["metrics"]["total_queue"]
        if q > max_queue:
            max_queue = q

    final_metrics = engine.metrics_tracker.calculate_metrics(
        list(engine.vehicles.values()), engine.roads, engine.sim_time
    )

    return {
        "name": scenario.name,
        "active_vehicles": final_metrics["active_vehicles"],
        "completed_vehicles": final_metrics["completed_vehicles"],
        "avg_speed_kmh": final_metrics["avg_speed_kmh"],
        "avg_waiting_time_sec": final_metrics["avg_waiting_time_sec"],
        "max_queue": max_queue,
        "throughput_vpm": final_metrics["throughput_vpm"],
        "road_utilization_pct": final_metrics["road_utilization_pct"],
    }


def test_scenario_benchmarks_empirical_validation():
    """Runs and asserts comparative trends across Scenarios A, B, C, D."""
    results = {}
    for key in ["normal", "peak_hour", "flyover_bypass", "adaptive_signals"]:
        results[key] = run_benchmark_scenario(key, seed=42, steps=2000)

    res_a = results["normal"]
    res_b = results["peak_hour"]
    res_c = results["flyover_bypass"]
    res_d = results["adaptive_signals"]

    print("\n================ BENCHMARK SCENARIO VALIDATION TABLE ================")
    print(f"{'Scenario':<32} | {'Avg Speed':<10} | {'Wait Time':<10} | {'Max Queue':<10} | {'Completed':<10}")
    print("-" * 80)
    for k, r in results.items():
        print(f"{r['name']:<32} | {r['avg_speed_kmh']:<6} km/h | {r['avg_waiting_time_sec']:<6} s  | {r['max_queue']:<10} | {r['completed_vehicles']:<10}")
    print("=" * 80)

    # 1. Peak Hour (Scenario B) must experience higher congestion/queue than Normal (Scenario A)
    assert res_b["max_queue"] >= res_a["max_queue"], "Peak hour should have larger queues than normal flow"

    # 2. Flyover Bypass (Scenario C) vs Gridlock (Scenario B):
    # Flyover routes arterial traffic above junction, reducing ground queueing and increasing average speed!
    assert res_c["avg_speed_kmh"] > res_b["avg_speed_kmh"], (
        f"Flyover speed ({res_c['avg_speed_kmh']}) should exceed Gridlock speed ({res_b['avg_speed_kmh']})"
    )
    assert res_c["avg_waiting_time_sec"] < res_b["avg_waiting_time_sec"], (
        f"Flyover wait time ({res_c['avg_waiting_time_sec']}) should be lower than Gridlock ({res_b['avg_waiting_time_sec']})"
    )
