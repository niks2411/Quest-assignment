"""
Kinematic Physics & Numerical Integration Module
Handles vehicle velocity updates, positional integration, boundary limits,
and collision avoidance safety guards.
"""
from typing import Tuple, Optional
from .vehicle import Vehicle


def integrate_kinematics(
    vehicle: Vehicle,
    target_acceleration: float,
    dt: float,
    max_position: Optional[float] = None,
) -> None:
    """
    Applies numerical integration for vehicle speed, position, and travel statistics.
    Uses trapezoidal integration with a strict physical collision prevention clamp.
    
    Args:
        vehicle: Vehicle instance to integrate.
        target_acceleration: Desired acceleration (m/s^2) from IDM.
        dt: Timestep (seconds).
        max_position: Upper bound on position to strictly prevent overlapping leader.
    """
    vehicle.acceleration = target_acceleration
    old_speed = vehicle.speed
    
    # Update velocity with bounding: cannot be negative, cannot exceed max_speed
    new_speed = old_speed + target_acceleration * dt
    new_speed = max(0.0, min(vehicle.max_speed, new_speed))
    
    # Midpoint integration for position
    avg_speed = (old_speed + new_speed) / 2.0
    distance_traveled = avg_speed * dt
    target_position = vehicle.position + distance_traveled
    
    # Physical collision guard: never allow follower bumper to penetrate leader bumper buffer
    if max_position is not None and target_position > max_position:
        target_position = max_position
        distance_traveled = max(0.0, target_position - vehicle.position)
        # Cap speed to match the constraint
        new_speed = min(new_speed, distance_traveled / max(0.0001, dt))

    vehicle.speed = new_speed
    vehicle.position = target_position
    vehicle.total_distance += distance_traveled
    vehicle.travel_time += dt

    # Status classification
    if new_speed < 0.3:
        vehicle.waiting_time += dt
        vehicle.status = "stopped"
    elif target_acceleration < -0.3:
        vehicle.status = "braking"
    elif target_acceleration > 0.3:
        vehicle.status = "accelerating"
    else:
        vehicle.status = "moving"


def check_collision(v1: Vehicle, v2: Vehicle, min_buffer: float = 0.5) -> bool:
    """
    Checks if two vehicles occupy overlapping physical space on the same road/lane.
    Returns True if bumper-to-bumper net gap is less than min_buffer.
    """
    if v1.current_road_id != v2.current_road_id or v1.lane != v2.lane:
        return False

    lead, follower = (v1, v2) if v1.position >= v2.position else (v2, v1)
    gap = lead.position - lead.length - follower.position
    return gap < min_buffer


def check_spatial_2d_collision(v1: Vehicle, v2: Vehicle, collision_distance: float = 2.5) -> bool:
    """
    Checks if two vehicles physically intersect in 2D Euclidean canvas/world space.
    Used for junction conflict detection across different crossing arms.
    """
    dx = v1.x - v2.x
    dy = v1.y - v2.y
    dist = (dx * dx + dy * dy) ** 0.5
    # Combined effective radii
    min_safe_dist = (v1.length + v2.length) * 0.4
    return dist < min_safe_dist


def clamp(val: float, min_val: float, max_val: float) -> float:
    """Utility clamp."""
    return max(min_val, min(max_val, val))
