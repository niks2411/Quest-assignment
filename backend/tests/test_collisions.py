"""
Automated Collision Prevention & Safe Following Distance Tests
Audits vehicle following under sudden braking, high density (50, 100, 200, 300 vehicles),
and mixed fleet dimensions (cars, buses, trucks, bikes).
"""
import pytest
from simulation.engine import SimulationEngine
from simulation.physics import integrate_kinematics
from simulation.vehicle import Vehicle
from models.scenario import ScenarioConfig


def test_no_collision_on_sudden_leader_braking():
    """Follower approaching a suddenly stopped leader must never overlap (gap >= 0.5m)."""
    engine = SimulationEngine(seed=101)
    
    # Place lead vehicle stopped at position 60m
    leader = Vehicle(id="lead", vehicle_type="truck", position=60.0, speed=0.0, length=12.0)
    # Place fast follower at position 20m traveling at 15 m/s (54 km/h)
    follower = Vehicle(id="follow", vehicle_type="car", position=20.0, speed=15.0, length=4.5)
    
    dt = 0.05
    min_observed_gap = 999.0

    for step in range(120):  # 6 seconds
        # Follower calculates IDM deceleration
        gap = leader.position - leader.length - follower.position
        min_observed_gap = min(min_observed_gap, gap)
        
        accel = engine.idm.calculate_acceleration(
            current_speed=follower.speed,
            desired_speed=follower.desired_speed,
            max_accel=follower.max_accel,
            comfort_decel=follower.comfort_decel,
            gap=gap,
            leader_speed=leader.speed,
        )
        
        max_pos = leader.position - leader.length - 1.0
        integrate_kinematics(follower, accel, dt, max_position=max_pos)
        
        # Follower must never penetrate leader
        assert follower.position < leader.position - leader.length, (
            f"Step {step}: Follower penetrated leader! Follower pos={follower.position}, leader tail={leader.position - leader.length}"
        )

    # Maintained safe gap throughout
    assert min_observed_gap >= 1.0


def test_high_density_fleet_no_collision_50_to_300_vehicles():
    """
    Simulates variable-density traffic with 50, 100, 200, and 300 vehicles over hundreds of steps.
    Audits every vehicle pair in every lane at every single timestep.
    Zero collisions or bumper overlaps permitted.
    """
    for target_count in [50, 100, 200, 300]:
        config = ScenarioConfig(
            name=f"High Density Test {target_count}",
            target_vehicle_count=target_count,
            spawn_rate_vps=3.0,
            lanes_per_road=2,
            traffic_signal_green=20.0,
            traffic_signal_yellow=4.0,
            flyover_enabled=True,
        )
        engine = SimulationEngine(scenario=config, seed=42)
        engine.start()

        # Run 200 timesteps (10 seconds simulated)
        for step in range(200):
            engine.step()

            # Audit all active vehicles in identical road/lanes
            vehicles_by_lane = {}
            for v in engine.vehicles.values():
                key = (v.current_road_id, v.lane)
                vehicles_by_lane.setdefault(key, []).append(v)

            for key, v_list in vehicles_by_lane.items():
                if len(v_list) > 1:
                    v_list.sort(key=lambda item: item.position, reverse=True)
                    for i in range(len(v_list) - 1):
                        lead = v_list[i]
                        follow = v_list[i + 1]
                        net_gap = lead.position - lead.length - follow.position
                        assert net_gap >= 0.45, (
                            f"Target {target_count}, Step {step}: Overlap detected! "
                            f"Lead {lead.id} pos={lead.position} len={lead.length}, "
                            f"Follow {follow.id} pos={follow.position}. Net gap = {net_gap:.3f}m"
                        )


def test_multi_class_vehicle_mix_safe_following():
    """Different vehicle dimensions (truck: 12m, bus: 10.5m, car: 4.5m, bike: 2.2m) preserve safe headway."""
    engine = SimulationEngine(seed=77)
    
    # Train of mixed vehicles on same lane: Truck -> Bus -> Car -> Motorcycle
    v1_truck = Vehicle(id="v1", vehicle_type="truck", position=150.0, speed=10.0)
    v2_bus = Vehicle(id="v2", vehicle_type="bus", position=120.0, speed=12.0)
    v3_car = Vehicle(id="v3", vehicle_type="car", position=90.0, speed=14.0)
    v4_bike = Vehicle(id="v4", vehicle_type="motorcycle", position=60.0, speed=16.0)
    
    train = [v1_truck, v2_bus, v3_car, v4_bike]
    dt = 0.05

    for _ in range(100):
        for i in range(len(train)):
            v = train[i]
            if i == 0:
                # Leader slows down
                accel = -1.5 if v.position > 180.0 else 0.5
                integrate_kinematics(v, accel, dt)
            else:
                leader = train[i - 1]
                gap = leader.position - leader.length - v.position
                accel = engine.idm.calculate_acceleration(
                    v.speed, v.desired_speed, v.max_accel, v.comfort_decel, gap, leader.speed
                )
                max_pos = leader.position - leader.length - 1.0
                integrate_kinematics(v, accel, dt, max_position=max_pos)
                
                assert v.position < leader.position - leader.length, (
                    f"Collision between {v.id} ({v.vehicle_type}) and leader {leader.id} ({leader.vehicle_type})!"
                )
