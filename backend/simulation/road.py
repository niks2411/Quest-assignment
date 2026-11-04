"""
Road Network & Segment Modeling
Represents individual road branches, lanes, capacities, speed limits,
and coordinate transformations for 2D rendering.
"""
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class RoadSegment:
    id: str
    name: str
    direction: str              # 'N', 'S', 'E', 'W'
    is_incoming: bool           # True = toward junction, False = away from junction
    length: float = 220.0       # Road length in meters
    lanes: int = 2              # Number of lanes: 1, 2, or 4
    lane_width: float = 3.5     # Lane width in meters
    speed_limit: float = 16.66  # 60 km/h in m/s
    is_flyover: bool = False    # Whether this segment is an elevated flyover
    
    @property
    def capacity(self) -> int:
        """
        Nominal road storage capacity:
        Based on length, average car length (4.5m) + min jam headway (2.0m).
        Multiplied by the number of lanes.
        """
        effective_vehicle_space = 4.5 + 2.5  # 7 meters per vehicle
        single_lane_cap = int(self.length / effective_vehicle_space)
        return max(5, single_lane_cap * self.lanes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "direction": self.direction,
            "is_incoming": self.is_incoming,
            "length": self.length,
            "lanes": self.lanes,
            "lane_width": self.lane_width,
            "speed_limit_kmh": round(self.speed_limit * 3.6, 1),
            "is_flyover": self.is_flyover,
            "capacity": self.capacity,
        }


def build_default_network(lanes: int = 2, flyover_enabled: bool = False) -> Dict[str, RoadSegment]:
    """
    Constructs the 4-way intersection road network, plus optional elevated flyover bypass.
    """
    roads = {
        # Incoming roads to junction
        "road_N_in": RoadSegment("road_N_in", "North Avenue (Inbound)", "N", True, lanes=lanes),
        "road_S_in": RoadSegment("road_S_in", "South Boulevard (Inbound)", "S", True, lanes=lanes),
        "road_E_in": RoadSegment("road_E_in", "East Expressway (Inbound)", "E", True, lanes=lanes),
        "road_W_in": RoadSegment("road_W_in", "West Parkway (Inbound)", "W", True, lanes=lanes),

        # Outgoing roads from junction
        "road_N_out": RoadSegment("road_N_out", "North Avenue (Outbound)", "N", False, lanes=lanes),
        "road_S_out": RoadSegment("road_S_out", "South Boulevard (Outbound)", "S", False, lanes=lanes),
        "road_E_out": RoadSegment("road_E_out", "East Expressway (Outbound)", "E", False, lanes=lanes),
        "road_W_out": RoadSegment("road_W_out", "West Parkway (Outbound)", "W", False, lanes=lanes),
    }

    if flyover_enabled:
        # Flyover spans North-South bidirectional over the junction
        roads["flyover_NS"] = RoadSegment(
            "flyover_NS", "North-South Elevated Flyover", "N", True, length=300.0, lanes=2, speed_limit=22.2, is_flyover=True
        )
        roads["flyover_SN"] = RoadSegment(
            "flyover_SN", "South-North Elevated Flyover", "S", True, length=300.0, lanes=2, speed_limit=22.2, is_flyover=True
        )

    return roads
