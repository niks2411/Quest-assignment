"""
Simulation Engine
Core coordinator that advances agent-based simulation timesteps,
handles vehicle generation, IDM car-following, intersection arbitration,
junction conflict detection, and state serialization.
"""
import random
import math
from typing import Dict, List, Any, Optional, Tuple

from .vehicle import Vehicle
from .idm import IntelligentDriverModel
from .physics import integrate_kinematics, check_spatial_2d_collision
from .road import RoadSegment, build_default_network
from .traffic_light import TrafficLightController
from .junction import calculate_vehicle_pose, get_junction_dimensions, get_destination_direction
from .metrics import MetricsTracker
from models.scenario import ScenarioConfig, SCENARIO_PRESETS


class SimulationEngine:
    def __init__(self, scenario: Optional[ScenarioConfig] = None, seed: Optional[int] = 42):
        if seed is not None:
            random.seed(seed)
        
        self.scenario = scenario or SCENARIO_PRESETS["normal"]
        self.sim_time: float = 0.0
        self.is_running: bool = False
        self.dt: float = 0.05  # 20 updates per simulated second (50ms)
        self.spawn_timer: float = 0.0
        
        # IDM Model with realistic parameters and visible safe jam distance
        self.idm = IntelligentDriverModel(s0=3.5, headway_time=1.5)
        
        # Roads & Traffic Lights
        self.roads: Dict[str, RoadSegment] = build_default_network(
            lanes=self.scenario.lanes_per_road,
            flyover_enabled=self.scenario.flyover_enabled,
        )
        self.traffic_light = TrafficLightController(
            green_duration=self.scenario.traffic_signal_green,
            yellow_duration=self.scenario.traffic_signal_yellow,
            mode=self.scenario.traffic_signal_mode,
        )
        
        # Vehicles & Metrics
        self.vehicles: Dict[str, Vehicle] = {}
        self.metrics_tracker = MetricsTracker()
        self.vehicle_counter = 0

    def reset(self, scenario: Optional[ScenarioConfig] = None, seed: Optional[int] = 42) -> None:
        """Resets the simulation to the initial state with an optional new scenario."""
        if seed is not None:
            random.seed(seed)
        if scenario is not None:
            self.scenario = scenario
            
        self.sim_time = 0.0
        self.spawn_timer = 0.0
        self.is_running = False
        self.vehicles.clear()
        self.metrics_tracker = MetricsTracker()
        self.vehicle_counter = 0

        self.roads = build_default_network(
            lanes=self.scenario.lanes_per_road,
            flyover_enabled=self.scenario.flyover_enabled,
        )
        self.traffic_light = TrafficLightController(
            green_duration=self.scenario.traffic_signal_green,
            yellow_duration=self.scenario.traffic_signal_yellow,
            mode=self.scenario.traffic_signal_mode,
        )

    def start(self) -> None:
        self.is_running = True

    def pause(self) -> None:
        self.is_running = False

    def _sample_vehicle_type(self) -> str:
        """Samples vehicle category according to scenario mix distribution."""
        types = list(self.scenario.vehicle_mix.keys())
        weights = list(self.scenario.vehicle_mix.values())
        return random.choices(types, weights=weights, k=1)[0]

    def _try_spawn_vehicle(self) -> None:
        """Attempts to spawn a new vehicle on an incoming road or flyover."""
        if len(self.vehicles) >= self.scenario.target_vehicle_count:
            return

        directions = ["N", "S", "E", "W"]
        origin = random.choice(directions)
        
        # Check if taking flyover
        take_flyover = False
        if self.scenario.flyover_enabled and origin in ("N", "S") and random.random() < 0.40:
            take_flyover = True

        road_id = f"flyover_{origin}{'S' if origin == 'N' else 'N'}" if take_flyover else f"road_{origin}_in"
        road = self.roads.get(road_id)
        if not road:
            return

        target_lane = random.randint(0, road.lanes - 1)

        # Check if lane entrance has sufficient clearance (minimum safe headway of 18m)
        for v in self.vehicles.values():
            if v.current_road_id == road_id and v.lane == target_lane:
                if v.position < 18.0:
                    return

        # Choose turn intent: 60% straight, 20% left, 20% right
        if take_flyover:
            turn_intent = "straight"
        else:
            turn_intent = random.choices(["straight", "left", "right"], weights=[0.60, 0.20, 0.20], k=1)[0]

        v_type = self._sample_vehicle_type()
        self.vehicle_counter += 1
        vehicle_id = f"v_{self.vehicle_counter}"

        new_vehicle = Vehicle(
            id=vehicle_id,
            vehicle_type=v_type,
            position=0.0,
            speed=road.speed_limit * 0.6,  # Enters with initial cruising speed
            lane=target_lane,
            target_lane=target_lane,
            origin_direction=origin,
            turn_intent=turn_intent,
            current_road_id=road_id,
            on_flyover=take_flyover,
        )

        # Calculate initial 2D pose
        junction_half = get_junction_dimensions(self.scenario.lanes_per_road)
        x, y, angle = calculate_vehicle_pose(new_vehicle, self.scenario.lanes_per_road, junction_half)
        new_vehicle.x = x
        new_vehicle.y = y
        new_vehicle.angle = angle

        self.vehicles[vehicle_id] = new_vehicle

    def _is_oncoming_through_traffic_present(self, vehicle: Vehicle, stop_line: float) -> bool:
        """
        Left-turn conflict check:
        Vehicles turning left across the intersection must yield to oncoming through traffic.
        """
        opposites = {"N": "S", "S": "N", "E": "W", "W": "E"}
        opp_origin = opposites.get(vehicle.origin_direction)
        if not opp_origin:
            return False

        opp_road = f"road_{opp_origin}_in"
        for other in self.vehicles.values():
            if other.on_flyover or other.origin_direction != opp_origin:
                continue
            # If oncoming vehicle is going straight and close to/in the junction
            if other.turn_intent == "straight":
                # Inside junction or within 45m of stop line
                if stop_line - 45.0 <= other.position <= stop_line + 50.0:
                    return True
        return False

    def _is_junction_exit_blocked(self, vehicle: Vehicle, stop_line: float, junction_length: float) -> bool:
        """
        Anti-gridlock 'Don't Block the Box' rule:
        Prevents vehicles from entering intersection if destination exit lane is jammed.
        """
        dest_dir = get_destination_direction(vehicle.origin_direction, vehicle.turn_intent)
        exit_pos = stop_line + junction_length

        for other in self.vehicles.values():
            if other.on_flyover or other.id == vehicle.id:
                continue
            # If another vehicle is on the same exit road and lane, stopped right at junction exit
            other_dest = get_destination_direction(other.origin_direction, other.turn_intent)
            if other_dest == dest_dir and other.lane == vehicle.lane:
                if exit_pos <= other.position <= exit_pos + 12.0 and other.speed < 1.0:
                    return True
        return False

    def step(self, custom_dt: Optional[float] = None) -> Dict[str, Any]:
        """Advances the simulation by one timestep dt."""
        dt = custom_dt or self.dt
        self.sim_time += dt

        # 1. Update Traffic Lights with directional queue sensor
        queue_ns = sum(
            1 for v in self.vehicles.values()
            if v.origin_direction in ("N", "S") and v.speed < 0.8 and not v.on_flyover and v.position < 220.0
        )
        queue_ew = sum(
            1 for v in self.vehicles.values()
            if v.origin_direction in ("E", "W") and v.speed < 0.8 and not v.on_flyover and v.position < 220.0
        )
        self.traffic_light.update(dt, queue_ns=queue_ns, queue_ew=queue_ew)

        # 2. Spawner
        self.spawn_timer += dt
        spawn_interval = 1.0 / max(0.01, self.scenario.spawn_rate_vps)
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            self._try_spawn_vehicle()

        # 3. Geometry & Thresholds
        junction_half = get_junction_dimensions(self.scenario.lanes_per_road)
        stop_line_m = 220.0
        junction_length_m = 60.0
        exit_line_m = stop_line_m + junction_length_m
        total_trip_length = 500.0

        # Group vehicles into three distinct routing regimes:
        # A) Inbound / Stop-line regime (pos <= 220.0) grouped by (current_road_id, lane)
        # B) Outbound regime (pos > 280.0) grouped by (dest_direction, lane)
        # C) Flyover regime grouped by road_id
        inbound_map: Dict[tuple, List[Vehicle]] = {}
        outbound_map: Dict[tuple, List[Vehicle]] = {}
        flyover_map: Dict[str, List[Vehicle]] = {}

        for v in self.vehicles.values():
            if v.on_flyover:
                flyover_map.setdefault(v.current_road_id, []).append(v)
            elif v.position <= stop_line_m + 0.05:
                inbound_map.setdefault((v.current_road_id, v.lane), []).append(v)
            else:
                dest_dir = get_destination_direction(v.origin_direction, v.turn_intent)
                outbound_map.setdefault((dest_dir, v.lane), []).append(v)

        # Sort each group descending by position (furthest along route is leader)
        for group in inbound_map.values():
            group.sort(key=lambda item: item.position, reverse=True)
        for group in outbound_map.values():
            group.sort(key=lambda item: item.position, reverse=True)
        for group in flyover_map.values():
            group.sort(key=lambda item: item.position, reverse=True)

        to_remove: List[str] = []

        # 4. Agent Kinematics & IDM Update
        for v in self.vehicles.values():
            gap = None
            leader_speed = None
            max_allowed_pos = None

            if v.on_flyover:
                # Flyover Car-Following
                same_flyover = flyover_map.get(v.current_road_id, [])
                v_idx = same_flyover.index(v)
                if v_idx > 0:
                    leader = same_flyover[v_idx - 1]
                    gap = leader.position - leader.length - v.position
                    leader_speed = leader.speed
                    max_allowed_pos = leader.position - leader.length - 2.5

            elif v.position <= stop_line_m + 0.05:
                # INBOUND CORRIDOR CAR-FOLLOWING & STOP LINE ARBITRATION
                key = (v.current_road_id, v.lane)
                lane_group = inbound_map.get(key, [v])
                v_idx = lane_group.index(v) if v in lane_group else 0

                if v_idx > 0:
                    # Vehicle ahead in inbound queue
                    leader = lane_group[v_idx - 1]
                    gap = leader.position - leader.length - v.position
                    leader_speed = leader.speed
                    max_allowed_pos = leader.position - leader.length - 2.5
                else:
                    # Lead vehicle on inbound road approaching intersection
                    signal = self.traffic_light.get_signal(v.origin_direction)
                    dist_to_signal = max(0.0, stop_line_m - v.position)

                    # Stopping required conditions
                    need_stop_at_signal = False
                    if signal == "RED":
                        need_stop_at_signal = True
                    elif signal == "YELLOW":
                        # Yellow dilemma zone: stop if possible, otherwise clear intersection
                        stopping_dist = (v.speed ** 2) / (2.0 * max(0.5, v.comfort_decel))
                        if dist_to_signal > stopping_dist:
                            need_stop_at_signal = True

                    # Left-Turn Yielding & Anti-Gridlock on Green
                    if not need_stop_at_signal and signal == "GREEN":
                        if dist_to_signal <= 40.0:
                            if self._is_junction_exit_blocked(v, stop_line_m, junction_length_m):
                                need_stop_at_signal = True
                            elif v.turn_intent == "left" and self._is_oncoming_through_traffic_present(v, stop_line_m):
                                need_stop_at_signal = True

                    if need_stop_at_signal:
                        gap = max(0.01, dist_to_signal - 1.5)
                        leader_speed = 0.0
                        max_allowed_pos = stop_line_m - 1.5  # Stop cleanly with 1.5m buffer before stop line
                        if dist_to_signal <= 1.55:
                            v.position = stop_line_m - 1.5
                            v.speed = 0.0
                            v.status = "stopped"

            else:
                # INSIDE JUNCTION OR ON OUTBOUND ARM
                dest_dir = get_destination_direction(v.origin_direction, v.turn_intent)
                out_key = (dest_dir, v.lane)
                out_group = outbound_map.get(out_key, [])
                v_idx = out_group.index(v)

                if v_idx > 0:
                    leader = out_group[v_idx - 1]
                    gap = leader.position - leader.length - v.position
                    leader_speed = leader.speed
                    max_allowed_pos = leader.position - leader.length - 2.5

                # 2D Junction Conflict Yielding:
                # If inside junction (stop_line_m < pos <= exit_line_m), check for intersecting vehicles
                if stop_line_m < v.position <= exit_line_m:
                    for other in self.vehicles.values():
                        if other.id == v.id or other.on_flyover:
                            continue
                        if stop_line_m < other.position <= exit_line_m:
                            # Both in junction; if close in 2D space, trailing vehicle yields
                            dx = other.x - v.x
                            dy = other.y - v.y
                            spatial_dist = (dx * dx + dy * dy) ** 0.5
                            if spatial_dist < 15.0:
                                # Determine precedence: vehicle further along or going straight has priority
                                other_priority = (other.turn_intent == "straight")
                                my_priority = (v.turn_intent == "straight")
                                if (other.position > v.position) or (other_priority and not my_priority):
                                    junction_gap = max(1.0, spatial_dist - other.length)
                                    if gap is None or junction_gap < gap:
                                        gap = junction_gap
                                        leader_speed = other.speed

            # Calculate IDM Acceleration
            road_speed_limit = self.roads[v.current_road_id].speed_limit
            target_v0 = min(v.desired_speed, road_speed_limit)

            accel = self.idm.calculate_acceleration(
                current_speed=v.speed,
                desired_speed=target_v0,
                max_accel=v.max_accel,
                comfort_decel=v.comfort_decel,
                gap=gap,
                leader_speed=leader_speed,
            )

            # Kinematic numerical integration with collision-prevention clamp
            integrate_kinematics(v, accel, dt, max_position=max_allowed_pos)

            # Update 2D Canvas Position
            x, y, angle = calculate_vehicle_pose(v, self.scenario.lanes_per_road, junction_half)
            v.x = x
            v.y = y
            v.angle = angle

            # Check for completed trip
            max_len = 300.0 if v.on_flyover else total_trip_length
            if v.position >= max_len:
                to_remove.append(v.id)

        # 5. Remove finished vehicles
        for vid in to_remove:
            finished_v = self.vehicles.pop(vid)
            self.metrics_tracker.record_completed_vehicle(finished_v, self.sim_time)

        # 6. Compile Metrics
        metrics = self.metrics_tracker.calculate_metrics(
            list(self.vehicles.values()), self.roads, self.sim_time
        )

        return self.get_state(metrics=metrics)

    def get_state(self, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Serializes current simulation state for client applications."""
        if metrics is None:
            metrics = self.metrics_tracker.calculate_metrics(
                list(self.vehicles.values()), self.roads, self.sim_time
            )

        return {
            "sim_time": round(self.sim_time, 2),
            "is_running": self.is_running,
            "vehicle_count": len(self.vehicles),
            "traffic_light": self.traffic_light.to_dict(),
            "metrics": metrics,
            "scenario": self.scenario.model_dump(),
            "vehicles": [v.to_dict() for v in self.vehicles.values()],
        }
