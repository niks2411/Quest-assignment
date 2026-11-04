"""
Scenario Configuration Model
Defines configurable parameters for traffic simulations,
including vehicle volume, road infrastructure, traffic light policies, and presets.
"""
from typing import Dict
from pydantic import BaseModel, Field


class ScenarioConfig(BaseModel):
    name: str = "Custom Scenario"
    target_vehicle_count: int = Field(default=60, ge=5, le=300)
    spawn_rate_vps: float = Field(default=0.8, ge=0.1, le=5.0)  # Vehicles generated per second
    lanes_per_road: int = Field(default=2, ge=1, le=4)
    traffic_signal_green: float = Field(default=25.0, ge=5.0, le=90.0)
    traffic_signal_yellow: float = Field(default=4.0, ge=2.0, le=10.0)
    traffic_signal_mode: str = Field(default="fixed")  # "fixed" or "adaptive"
    flyover_enabled: bool = False
    speed_limit_kmh: float = Field(default=60.0, ge=20.0, le=120.0)
    vehicle_mix: Dict[str, float] = Field(
        default_factory=lambda: {
            "car": 0.65,
            "bus": 0.10,
            "truck": 0.10,
            "motorcycle": 0.15,
        }
    )


# Standard Benchmark Presets
SCENARIO_PRESETS: Dict[str, ScenarioConfig] = {
    "normal": ScenarioConfig(
        name="Scenario A: Normal Flow",
        target_vehicle_count=50,
        spawn_rate_vps=0.6,
        lanes_per_road=2,
        traffic_signal_green=25.0,
        traffic_signal_yellow=4.0,
        traffic_signal_mode="fixed",
        flyover_enabled=False,
    ),
    "peak_hour": ScenarioConfig(
        name="Scenario B: Peak-Hour Gridlock",
        target_vehicle_count=180,
        spawn_rate_vps=2.2,
        lanes_per_road=2,
        traffic_signal_green=25.0,
        traffic_signal_yellow=4.0,
        traffic_signal_mode="fixed",
        flyover_enabled=False,
    ),
    "flyover_bypass": ScenarioConfig(
        name="Scenario C: Flyover Bypass Added",
        target_vehicle_count=180,
        spawn_rate_vps=2.2,
        lanes_per_road=2,
        traffic_signal_green=25.0,
        traffic_signal_yellow=4.0,
        traffic_signal_mode="fixed",
        flyover_enabled=True,
    ),
    "adaptive_signals": ScenarioConfig(
        name="Scenario D: Smart Adaptive Signals",
        target_vehicle_count=160,
        spawn_rate_vps=1.8,
        lanes_per_road=2,
        traffic_signal_green=20.0,
        traffic_signal_yellow=4.0,
        traffic_signal_mode="adaptive",
        flyover_enabled=False,
    ),
}
