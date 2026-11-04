"""
Junction & Coordinate Mapping Logic
Handles vehicle routing through intersections, stop lines, turning paths,
and converts longitudinal distances into (x, y, angle) for Canvas rendering.
Follows standard Right-Hand Traffic (RHT) corridor conventions:
- North Arm: Inbound is West (left of yellow), Outbound is East (right of yellow)
- South Arm: Inbound is East (right of yellow), Outbound is West (left of yellow)
- East Arm: Inbound is North (top of yellow), Outbound is South (bottom of yellow)
- West Arm: Inbound is South (bottom of yellow), Outbound is North (top of yellow)
"""
import math
from typing import Tuple
from .vehicle import Vehicle

ROAD_PIXEL_SCALE = 1.75  # 1 meter = 1.75 pixels


def get_junction_dimensions(lanes: int) -> float:
    """Returns half-width of the intersection box in pixels."""
    lane_width_px = 3.5 * ROAD_PIXEL_SCALE  # ~6.1 px per lane
    return max(48.0, lanes * lane_width_px * 2.0 + 16.0)


def calculate_vehicle_pose(
    vehicle: Vehicle,
    lanes: int,
    junction_half: float,
    canvas_w: float = 900.0,
    canvas_h: float = 900.0,
) -> Tuple[float, float, float]:
    """
    Computes (x, y, angle) on the 2D Canvas based on vehicle's current road,
    position, lane index, and turn status.
    """
    center_x = canvas_w / 2.0
    center_y = canvas_h / 2.0

    lane_w_px = 18.0  # visual lane width in pixels matching canvas rendering
    lane_offset = (vehicle.lane + 0.5) * lane_w_px

    if vehicle.on_flyover:
        norm_pos = vehicle.position / 300.0
        if vehicle.origin_direction == "N":
            x = center_x - 10.0
            y = 45.0 + norm_pos * 810.0
            return (x, y, math.pi / 2.0)  # Heading downwards (South)
        else:  # South to North
            x = center_x + 10.0
            y = 855.0 - norm_pos * 810.0
            return (x, y, -math.pi / 2.0)  # Heading upwards (North)

    # Regular Ground Road Traversal
    direction = vehicle.origin_direction
    pos_m = vehicle.position
    pos_px = pos_m * ROAD_PIXEL_SCALE

    inbound_length_px = 220.0 * ROAD_PIXEL_SCALE  # ~385 px
    junction_size = junction_half * 2.0

    if pos_px <= inbound_length_px:
        # INBOUND PHASE: Vehicle approaching junction
        dist_from_start = pos_px
        if direction == "N":
            # Heading South (+y) on West side
            x = center_x - lane_offset
            y = (center_y - junction_half - inbound_length_px) + dist_from_start
            return (x, y, math.pi / 2.0)
        elif direction == "S":
            # Heading North (-y) on East side
            x = center_x + lane_offset
            y = (center_y + junction_half + inbound_length_px) - dist_from_start
            return (x, y, -math.pi / 2.0)
        elif direction == "E":
            # Heading West (-x) on North (top) side
            x = (center_x + junction_half + inbound_length_px) - dist_from_start
            y = center_y - lane_offset
            return (x, y, math.pi)
        elif direction == "W":
            # Heading East (+x) on South (bottom) side
            x = (center_x - junction_half - inbound_length_px) + dist_from_start
            y = center_y + lane_offset
            return (x, y, 0.0)

    elif pos_px <= inbound_length_px + junction_size:
        # JUNCTION TRANSITION PHASE: Inside intersection box
        inter_progress = (pos_px - inbound_length_px) / junction_size
        t = max(0.0, min(1.0, inter_progress))

        # Straight trajectories
        if vehicle.turn_intent == "straight":
            if direction == "N":
                x = center_x - lane_offset
                y = (center_y - junction_half) + t * junction_size
                return (x, y, math.pi / 2.0)
            elif direction == "S":
                x = center_x + lane_offset
                y = (center_y + junction_half) - t * junction_size
                return (x, y, -math.pi / 2.0)
            elif direction == "E":
                x = (center_x + junction_half) - t * junction_size
                # Transitions from North inbound (y = center_y - lane_offset) to West outbound (y = center_y - lane_offset)
                y = center_y - lane_offset
                return (x, y, math.pi)
            elif direction == "W":
                x = (center_x - junction_half) + t * junction_size
                # Transitions from South inbound (y = center_y + lane_offset) to East outbound (y = center_y + lane_offset)
                y = center_y + lane_offset
                return (x, y, 0.0)

        # Turning Left or Right: interpolate with smooth quadratic curve
        start_x, start_y = 0.0, 0.0
        end_x, end_y = 0.0, 0.0
        ctrl_x, ctrl_y = 0.0, 0.0

        if direction == "N":
            start_x, start_y = center_x - lane_offset, center_y - junction_half
            if vehicle.turn_intent == "left":
                # Turn East (+x) -> Destination is East Outbound (South/Bottom lane: y = center_y + lane_offset)
                end_x, end_y = center_x + junction_half, center_y + lane_offset
                ctrl_x, ctrl_y = center_x - lane_offset, center_y + lane_offset
            else:
                # Turn West (-x) -> Destination is West Outbound (North/Top lane: y = center_y - lane_offset)
                end_x, end_y = center_x - junction_half, center_y - lane_offset
                ctrl_x, ctrl_y = center_x - lane_offset, center_y - lane_offset

        elif direction == "S":
            start_x, start_y = center_x + lane_offset, center_y + junction_half
            if vehicle.turn_intent == "left":
                # Turn West (-x) -> Destination is West Outbound (North/Top lane: y = center_y - lane_offset)
                end_x, end_y = center_x - junction_half, center_y - lane_offset
                ctrl_x, ctrl_y = center_x + lane_offset, center_y - lane_offset
            else:
                # Turn East (+x) -> Destination is East Outbound (South/Bottom lane: y = center_y + lane_offset)
                end_x, end_y = center_x + junction_half, center_y + lane_offset
                ctrl_x, ctrl_y = center_x + lane_offset, center_y + lane_offset

        elif direction == "E":
            start_x, start_y = center_x + junction_half, center_y - lane_offset
            if vehicle.turn_intent == "left":
                # Turn South (+y) -> Destination is South Outbound (West lane: x = center_x - lane_offset)
                end_x, end_y = center_x - lane_offset, center_y + junction_half
                ctrl_x, ctrl_y = center_x - lane_offset, center_y - lane_offset
            else:
                # Turn North (-y) -> Destination is North Outbound (East lane: x = center_x + lane_offset)
                end_x, end_y = center_x + lane_offset, center_y - junction_half
                ctrl_x, ctrl_y = center_x + lane_offset, center_y - lane_offset

        else:  # W
            start_x, start_y = center_x - junction_half, center_y + lane_offset
            if vehicle.turn_intent == "left":
                # Turn North (-y) -> Destination is North Outbound (East lane: x = center_x + lane_offset)
                end_x, end_y = center_x + lane_offset, center_y - junction_half
                ctrl_x, ctrl_y = center_x + lane_offset, center_y + lane_offset
            else:
                # Turn South (+y) -> Destination is South Outbound (West lane: x = center_x - lane_offset)
                end_x, end_y = center_x - lane_offset, center_y + junction_half
                ctrl_x, ctrl_y = center_x - lane_offset, center_y + lane_offset

        # Quadratic Bezier
        bx = (1 - t) ** 2 * start_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * end_x
        by = (1 - t) ** 2 * start_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * end_y
        
        # Tangent angle
        dx = 2 * (1 - t) * (ctrl_x - start_x) + 2 * t * (end_x - ctrl_x)
        dy = 2 * (1 - t) * (ctrl_y - start_y) + 2 * t * (end_y - ctrl_y)
        angle = math.atan2(dy, dx)
        return (bx, by, angle)

    else:
        # OUTBOUND PHASE: Moving away from intersection along exit road
        out_dist = pos_px - (inbound_length_px + junction_size)
        out_dir = get_destination_direction(direction, vehicle.turn_intent)
        if out_dir == "N":
            # Heading North (-y) on East side
            x = center_x + lane_offset
            y = (center_y - junction_half) - out_dist
            return (x, y, -math.pi / 2.0)
        elif out_dir == "S":
            # Heading South (+y) on West side
            x = center_x - lane_offset
            y = (center_y + junction_half) + out_dist
            return (x, y, math.pi / 2.0)
        elif out_dir == "E":
            # Heading East (+x) on South (BOTTOM) side
            x = (center_x + junction_half) + out_dist
            y = center_y + lane_offset
            return (x, y, 0.0)
        else:  # W
            # Heading West (-x) on North (TOP) side
            x = (center_x - junction_half) - out_dist
            y = center_y - lane_offset
            return (x, y, math.pi)


def get_destination_direction(origin: str, turn_intent: str) -> str:
    """Returns destination arm given origin direction and turning choice."""
    opposites = {"N": "S", "S": "N", "E": "W", "W": "E"}
    left_turns = {"N": "E", "S": "W", "E": "S", "W": "N"}
    right_turns = {"N": "W", "S": "E", "E": "N", "W": "S"}

    if turn_intent == "straight":
        return opposites[origin]
    elif turn_intent == "left":
        return left_turns[origin]
    else:
        return right_turns[origin]
