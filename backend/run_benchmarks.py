"""
Controlled Benchmark Experiments Runner
Runs multiple trials across Scenarios A, B, C, and D with distinct seeds.
Collects actual empirical metrics:
- Average Speed (km/h)
- Average Waiting Time (s)
- Maximum Queue Length (veh)
- Throughput (veh/min)
- Road Utilization (%)
- Total Stopped Time (s)
"""
import statistics
from simulation.engine import SimulationEngine
from models.scenario import SCENARIO_PRESETS, ScenarioConfig


def run_trial(scenario_config: ScenarioConfig, seed: int, duration_sec: float = 120.0):
    dt = 0.05
    steps = int(duration_sec / dt)
    engine = SimulationEngine(scenario=scenario_config, seed=seed)
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

    total_stopped_time = sum(v.waiting_time for v in engine.vehicles.values()) + engine.metrics_tracker.total_completed_wait_time

    return {
        "avg_speed_kmh": final_metrics["avg_speed_kmh"],
        "avg_waiting_time_sec": final_metrics["avg_waiting_time_sec"],
        "max_queue": max_queue,
        "throughput_vpm": final_metrics["throughput_vpm"],
        "road_utilization_pct": final_metrics["road_utilization_pct"],
        "total_stopped_time_sec": round(total_stopped_time, 1),
        "completed_vehicles": final_metrics["completed_vehicles"],
    }


def execute_benchmarks(seeds=(42, 101, 256), duration_sec=120.0):
    scenarios = {
        "A (Normal Flow)": SCENARIO_PRESETS["normal"],
        "B (Peak-Hour Gridlock)": SCENARIO_PRESETS["peak_hour"],
        "C (Flyover Bypass Added)": SCENARIO_PRESETS["flyover_bypass"],
        "D (Smart Adaptive Signals)": SCENARIO_PRESETS["adaptive_signals"],
    }

    results = {}

    print(f"Executing Controlled Benchmarks across {len(seeds)} trials (duration: {duration_sec}s each)...")
    for name, config in scenarios.items():
        trial_runs = []
        for s in seeds:
            data = run_trial(config, seed=s, duration_sec=duration_sec)
            trial_runs.append(data)

        # Aggregate means and std
        agg = {}
        keys = ["avg_speed_kmh", "avg_waiting_time_sec", "max_queue", "throughput_vpm", "road_utilization_pct", "total_stopped_time_sec", "completed_vehicles"]
        for k in keys:
            vals = [run[k] for run in trial_runs]
            agg[k] = round(statistics.mean(vals), 2)
            agg[f"{k}_std"] = round(statistics.stdev(vals), 2) if len(vals) > 1 else 0.0

        results[name] = {"agg": agg, "raw": trial_runs}

    print("\n" + "=" * 115)
    print("EMPIRICAL BENCHMARK EXPERIMENT RESULTS (Averaged over 3 Independent Trials)")
    print("=" * 115)
    header = f"{'Scenario':<28} | {'Speed (km/h)':<13} | {'Wait Time (s)':<13} | {'Max Queue':<10} | {'Throughput (vpm)':<16} | {'Utilization %':<13} | {'Total Wait (s)':<14}"
    print(header)
    print("-" * 115)
    for name, data in results.items():
        m = data["agg"]
        row = (
            f"{name:<28} | "
            f"{m['avg_speed_kmh']:<5} ± {m['avg_speed_kmh_std']:<4} | "
            f"{m['avg_waiting_time_sec']:<5} ± {m['avg_waiting_time_sec_std']:<4} | "
            f"{m['max_queue']:<10} | "
            f"{m['throughput_vpm']:<7} ± {m['throughput_vpm_std']:<5} | "
            f"{m['road_utilization_pct']:<5} ± {m['road_utilization_pct_std']:<4} | "
            f"{m['total_stopped_time_sec']:<14}"
        )
        print(row)
    print("=" * 115)

    return results


if __name__ == "__main__":
    execute_benchmarks()
