"""
Simulation Metrics & Analytics Engine
Calculates aggregate traffic network KPIs based on standard traffic flow theory:

Formulas used:
1. Space-Mean Average Speed (km/h):
   Average Speed = (Total Distance Traveled across all vehicles) / (Total Travel Time across all vehicles) * 3.6
   Formula: V_avg = 3.6 * (sum(d_i) / sum(t_i))

2. Average Waiting Time (s):
   Mean time spent in idling / stopped state (speed < 0.8 m/s):
   Wait_avg = (sum(w_active) + sum(w_completed)) / (N_active + N_completed)

3. Directional Queue Length (veh):
   Count of queued vehicles (speed < 0.8 m/s, position < stop_line_m) per incoming arm (N, S, E, W).

4. Road Utilization (%):
   Utilization = (N_active / Total_Network_Capacity) * 100

5. Traffic Density (veh/km):
   Density = N_active / Total_Network_Length_km

6. Throughput (veh/min):
   Vehicle discharge rate per minute:
   - For sim_time < 60s: Throughput = (N_completed / sim_time) * 60
   - For sim_time >= 60s: Count of vehicles exited in rolling 60-second window
"""
from typing import List, Dict, Any
from .vehicle import Vehicle
from .road import RoadSegment


class MetricsTracker:
    def __init__(self):
        self.completed_vehicles: int = 0
        self.total_completed_wait_time: float = 0.0
        self.total_completed_distance: float = 0.0
        self.total_completed_travel_time: float = 0.0
        self.throughput_window: List[float] = []  # timestamps of vehicle exits

    def record_completed_vehicle(self, vehicle: Vehicle, current_time: float) -> None:
        """Invoked when a vehicle completes its trip through the network."""
        self.completed_vehicles += 1
        self.total_completed_wait_time += vehicle.waiting_time
        self.total_completed_distance += vehicle.total_distance
        self.total_completed_travel_time += vehicle.travel_time
        self.throughput_window.append(current_time)

    def calculate_metrics(
        self,
        active_vehicles: List[Vehicle],
        roads: Dict[str, RoadSegment],
        current_time: float,
    ) -> Dict[str, Any]:
        """Calculates instantaneous and cumulative simulation KPIs."""
        total_active = len(active_vehicles)

        # 1. Throughput (vehicles/min)
        cutoff = current_time - 60.0
        self.throughput_window = [t for t in self.throughput_window if t >= cutoff]
        
        if current_time >= 60.0:
            throughput_vpm = len(self.throughput_window)
        elif current_time >= 5.0:
            # Scaled rate during initial warmup
            throughput_vpm = round((self.completed_vehicles / current_time) * 60.0, 1)
        else:
            throughput_vpm = 0.0

        # 2. Directional Queues (vehicles with speed < 0.8 m/s on inbound road before stop line)
        queues = {"N": 0, "S": 0, "E": 0, "W": 0}
        active_wait_times = []
        active_dist_sum = 0.0
        active_time_sum = 0.0

        for v in active_vehicles:
            active_wait_times.append(v.waiting_time)
            active_dist_sum += v.total_distance
            active_time_sum += v.travel_time
            
            # Count in queue if stopped or crawling prior to stop line
            if v.speed < 0.8 and not v.on_flyover and v.position < 220.0:
                if v.origin_direction in queues:
                    queues[v.origin_direction] += 1

        # 3. Space-Mean Average Speed (km/h): Total Distance / Total Time
        combined_dist = active_dist_sum + self.total_completed_distance
        combined_time = active_time_sum + self.total_completed_travel_time

        if combined_time > 0.0:
            avg_speed_mps = combined_dist / combined_time
            avg_speed_kmh = round(avg_speed_mps * 3.6, 1)
        else:
            avg_speed_kmh = 0.0

        # 4. Average Waiting Time in seconds
        total_wait = sum(active_wait_times) + self.total_completed_wait_time
        total_entities = total_active + self.completed_vehicles
        avg_wait_time = round(total_wait / total_entities, 1) if total_entities > 0 else 0.0

        # 5. Total Capacity & Road Utilization
        total_capacity = sum(r.capacity for r in roads.values())
        road_utilization_pct = (
            round((total_active / max(1, total_capacity)) * 100.0, 1) if total_capacity > 0 else 0.0
        )

        # 6. Total road network length in km and Traffic Density (veh/km)
        total_road_length_km = sum(r.length for r in roads.values()) / 1000.0
        density_vpk = round(total_active / max(0.1, total_road_length_km), 1)

        return {
            "active_vehicles": total_active,
            "completed_vehicles": self.completed_vehicles,
            "avg_speed_kmh": avg_speed_kmh,
            "avg_waiting_time_sec": avg_wait_time,
            "throughput_vpm": throughput_vpm,
            "road_utilization_pct": min(100.0, road_utilization_pct),
            "traffic_density_vpk": density_vpk,
            "queues": queues,
            "total_queue": sum(queues.values()),
        }
