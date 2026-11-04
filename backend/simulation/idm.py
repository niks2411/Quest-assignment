"""
Intelligent Driver Model (IDM) Implementation
Calculates realistic, continuous car-following acceleration based on
headway gap, relative speed, desired velocity, and physical comfort constraints.
Reference: Treiber, Hennecke, and Helbing (2000).
"""
import math
from typing import Optional


class IntelligentDriverModel:
    def __init__(
        self,
        s0: float = 3.5,        # Minimum safe jam distance between stopped vehicles (m)
        headway_time: float = 1.5, # Desired safe time headway T (s)
        delta: float = 4.0,     # Acceleration exponent
        max_emergency_decel: float = 8.0, # Max braking power (m/s^2)
    ):
        self.s0 = s0
        self.headway_time = headway_time
        self.delta = delta
        self.max_emergency_decel = max_emergency_decel

    def calculate_desired_gap(
        self,
        speed: float,
        delta_v: float,
        a: float,
        b: float,
    ) -> float:
        """
        Calculate dynamic desired gap s*(v, delta_v).
        s*(v, delta_v) = s0 + max(0, v*T + (v * delta_v) / (2 * sqrt(a * b)))
        """
        sqrt_ab = 2.0 * math.sqrt(max(0.001, a * b))
        interaction_term = (speed * delta_v) / sqrt_ab
        dynamic_term = speed * self.headway_time + interaction_term
        return self.s0 + max(0.0, dynamic_term)

    def calculate_acceleration(
        self,
        current_speed: float,
        desired_speed: float,
        max_accel: float,
        comfort_decel: float,
        gap: Optional[float] = None,
        leader_speed: Optional[float] = None,
    ) -> float:
        """
        Calculate continuous IDM acceleration.
        
        Args:
            current_speed: Current vehicle speed (m/s).
            desired_speed: Desired / free-flow speed (m/s).
            max_accel: Vehicle max acceleration parameter 'a' (m/s^2).
            comfort_decel: Comfortable deceleration parameter 'b' (m/s^2).
            gap: Net distance (m) to lead bumper. None if free road.
            leader_speed: Speed of lead vehicle (m/s). Required if gap is not None.

        Returns:
            Computed acceleration in m/s^2.
        """
        v = max(0.0, current_speed)
        v0 = max(0.1, desired_speed)
        a = max(0.1, max_accel)
        b = max(0.1, comfort_decel)

        # Free road acceleration term: a * [1 - (v / v0)^delta]
        free_ratio = min(v / v0, 5.0)  # prevent overflow if overspeeding
        accel_free = a * (1.0 - math.pow(free_ratio, self.delta))

        # If no vehicle or obstacle ahead, return free flow acceleration
        if gap is None or math.isinf(gap):
            return max(-self.max_emergency_decel, min(a, accel_free))

        # Interaction / braking term
        lead_v = max(0.0, leader_speed if leader_speed is not None else 0.0)
        delta_v = v - lead_v

        # Desired gap calculation
        s_star = self.calculate_desired_gap(v, delta_v, a, b)

        # Guard against zero or negative gaps
        safe_gap = max(0.1, gap)

        accel_brake = -a * math.pow(s_star / safe_gap, 2)
        total_accel = accel_free + accel_brake

        # Bound acceleration between max emergency deceleration and max acceleration
        return max(-self.max_emergency_decel, min(a, total_accel))
