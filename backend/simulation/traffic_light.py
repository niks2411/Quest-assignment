"""
Traffic Light Controller
Manages signal phases for a 4-way intersection with support for
fixed-time cycles and queue-length adaptive signal timing.
"""
from typing import Dict, Any


class SignalState:
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class TrafficLightController:
    def __init__(
        self,
        green_duration: float = 25.0,
        yellow_duration: float = 4.0,
        mode: str = "fixed",  # "fixed" or "adaptive"
    ):
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.mode = mode
        
        # Phases:
        # 0: NS Green, EW Red
        # 1: NS Yellow, EW Red
        # 2: EW Green, NS Red
        # 3: EW Yellow, NS Red
        self.current_phase = 0
        self.phase_time = 0.0
        
        # Adaptive thresholds
        self.min_green_time = 10.0
        self.max_green_time = 45.0

    def update(self, dt: float, queue_ns: int = 0, queue_ew: int = 0) -> None:
        """Advance traffic light state machine by dt seconds."""
        self.phase_time += dt

        target_green = self.green_duration
        if self.mode == "adaptive":
            # If current is NS and EW has twice as many cars waiting, reduce green time (down to min)
            if self.current_phase == 0:
                if queue_ew > queue_ns * 1.5 and self.phase_time >= self.min_green_time:
                    target_green = self.min_green_time
                elif queue_ns > queue_ew * 1.5:
                    target_green = min(self.max_green_time, self.green_duration + 10.0)
            elif self.current_phase == 2:
                if queue_ns > queue_ew * 1.5 and self.phase_time >= self.min_green_time:
                    target_green = self.min_green_time
                elif queue_ew > queue_ns * 1.5:
                    target_green = min(self.max_green_time, self.green_duration + 10.0)

        # Transition logic
        if self.current_phase == 0:  # NS Green
            if self.phase_time >= target_green:
                self.current_phase = 1
                self.phase_time = 0.0
        elif self.current_phase == 1:  # NS Yellow
            if self.phase_time >= self.yellow_duration:
                self.current_phase = 2
                self.phase_time = 0.0
        elif self.current_phase == 2:  # EW Green
            if self.phase_time >= target_green:
                self.current_phase = 3
                self.phase_time = 0.0
        elif self.current_phase == 3:  # EW Yellow
            if self.phase_time >= self.yellow_duration:
                self.current_phase = 0
                self.phase_time = 0.0

    def get_signal(self, direction: str) -> str:
        """
        Returns signal color for an approaching direction ('N', 'S', 'E', 'W').
        """
        is_ns = direction in ("N", "S")
        if self.current_phase == 0:
            return SignalState.GREEN if is_ns else SignalState.RED
        elif self.current_phase == 1:
            return SignalState.YELLOW if is_ns else SignalState.RED
        elif self.current_phase == 2:
            return SignalState.RED if is_ns else SignalState.GREEN
        elif self.current_phase == 3:
            return SignalState.RED if is_ns else SignalState.YELLOW
        return SignalState.RED

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for dashboard."""
        return {
            "current_phase": self.current_phase,
            "phase_time": round(self.phase_time, 1),
            "mode": self.mode,
            "signals": {
                "N": self.get_signal("N"),
                "S": self.get_signal("S"),
                "E": self.get_signal("E"),
                "W": self.get_signal("W"),
            },
        }
