"""
Vehicle Agent Model
Represents an individual vehicle agent with physical properties,
kinematics, intent, and status in the traffic network.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


VEHICLE_PROFILES = {
    "car": {
        "length": 4.5,
        "width": 2.0,
        "max_speed": 16.6,      # ~60 km/h
        "desired_speed": 13.88, # ~50 km/h
        "max_accel": 2.5,       # m/s^2
        "comfort_decel": 2.2,   # m/s^2
        "color": "#3B82F6",     # Blue
    },
    "bus": {
        "length": 10.5,
        "width": 2.6,
        "max_speed": 12.5,      # ~45 km/h
        "desired_speed": 11.11, # ~40 km/h
        "max_accel": 1.2,
        "comfort_decel": 1.8,
        "color": "#F59E0B",     # Amber/Orange
    },
    "truck": {
        "length": 12.0,
        "width": 2.6,
        "max_speed": 11.1,      # ~40 km/h
        "desired_speed": 10.0,  # ~36 km/h
        "max_accel": 1.0,
        "comfort_decel": 1.6,
        "color": "#EF4444",     # Red
    },
    "motorcycle": {
        "length": 2.2,
        "width": 0.9,
        "max_speed": 18.0,      # ~65 km/h
        "desired_speed": 15.27, # ~55 km/h
        "max_accel": 3.2,
        "comfort_decel": 3.0,
        "color": "#10B981",     # Emerald/Green
    },
}


@dataclass
class Vehicle:
    id: str
    vehicle_type: str = "car"
    
    # Kinematics
    position: float = 0.0          # Longitudinal distance along current segment (m)
    speed: float = 0.0             # Current speed (m/s)
    acceleration: float = 0.0      # Current acceleration (m/s^2)
    
    # Geometry & Physical parameters
    length: float = 4.5
    width: float = 2.0
    max_speed: float = 16.6
    desired_speed: float = 13.88
    max_accel: float = 2.5
    comfort_decel: float = 2.2
    color: str = "#3B82F6"
    
    # Navigation & Routing
    origin_direction: str = "N"    # 'N', 'S', 'E', 'W'
    turn_intent: str = "straight"  # 'straight', 'left', 'right'
    current_road_id: str = "road_N_in"
    lane: int = 0
    target_lane: int = 0
    on_flyover: bool = False
    
    # 2D World coordinates (meters / canvas units)
    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0             # Radians (0 = heading right/East)
    
    # Performance & Analytics Tracking
    total_distance: float = 0.0
    travel_time: float = 0.0
    waiting_time: float = 0.0      # Time spent with speed < 0.5 m/s
    status: str = "moving"         # 'moving', 'accelerating', 'braking', 'waiting', 'completed'

    def __post_init__(self):
        profile = VEHICLE_PROFILES.get(self.vehicle_type, VEHICLE_PROFILES["car"])
        # Apply profile properties if defaults were kept
        if self.length == 4.5 and self.vehicle_type != "car":
            self.length = profile["length"]
        if self.width == 2.0 and self.vehicle_type != "car":
            self.width = profile["width"]
        if self.max_speed == 16.6 and self.vehicle_type != "car":
            self.max_speed = profile["max_speed"]
        if self.desired_speed == 13.88 and self.vehicle_type != "car":
            self.desired_speed = profile["desired_speed"]
        if self.max_accel == 2.5 and self.vehicle_type != "car":
            self.max_accel = profile["max_accel"]
        if self.comfort_decel == 2.2 and self.vehicle_type != "car":
            self.comfort_decel = profile["comfort_decel"]
        if self.color == "#3B82F6" and self.vehicle_type != "car":
            self.color = profile["color"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert vehicle state to serializable dictionary for API/WebSocket."""
        return {
            "id": self.id,
            "type": self.vehicle_type,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "angle": round(self.angle, 3),
            "speed": round(self.speed, 2),
            "speed_kmh": round(self.speed * 3.6, 1),
            "acceleration": round(self.acceleration, 2),
            "length": self.length,
            "width": self.width,
            "lane": self.lane,
            "direction": self.origin_direction,
            "turn_intent": self.turn_intent,
            "on_flyover": self.on_flyover,
            "color": self.color,
            "status": self.status,
            "waiting_time": round(self.waiting_time, 1),
        }
