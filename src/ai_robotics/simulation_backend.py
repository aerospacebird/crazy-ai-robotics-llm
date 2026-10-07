from __future__ import annotations

import math
import time
from typing import Any, Dict

from .interfaces import DroneCommand


class SimulatedDroneBackend:
    """Simulation backend for safe local testing and controller validation."""

    def __init__(self):
        self._connected = False
        self.state = {
            "armed": False,
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "battery": 100.0,
            "heading_deg": 0.0,
            "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
            "status": "idle",
        }

    def connect(self) -> bool:
        self._connected = True
        self.state["status"] = "connected"
        return True

    def disconnect(self) -> None:
        self._connected = False
        self.state["status"] = "disconnected"

    def send_command(self, command: DroneCommand) -> Dict[str, Any]:
        if not self._connected:
            self.connect()

        pos = self.state["position"]
        target = command.target or (pos["x"], pos["y"], pos["z"])
        dx = target[0] - pos["x"]
        dy = target[1] - pos["y"]
        dz = target[2] - pos["z"]
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)

        if command.action in {"takeoff", "move", "fly_to"}:
            pos["x"] = target[0]
            pos["y"] = target[1]
            pos["z"] = target[2] if command.altitude_m is None else command.altitude_m
            self.state["armed"] = True
            self.state["status"] = "moving"
        elif command.action in {"land", "stop", "hold"}:
            self.state["armed"] = False
            self.state["status"] = "holding"
        elif command.action == "arm":
            self.state["armed"] = True
            self.state["status"] = "armed"

        self.state["battery"] = max(0.0, self.state["battery"] - 0.5 * distance / 10.0)
        self.state["heading_deg"] = command.yaw_deg or self.state["heading_deg"]

        return {
            "status": "executed",
            "backend": "simulation",
            "message": f"Simulation command executed: {command.action}",
            "target": target,
            "distance_m": distance,
            "state": self.state.copy(),
            "timestamp": time.time(),
        }

    def get_state(self) -> Dict[str, Any]:
        return self.state.copy()


__all__ = ["SimulatedDroneBackend"]
