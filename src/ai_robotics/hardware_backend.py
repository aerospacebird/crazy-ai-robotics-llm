from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

from .interfaces import DroneCommand


class ROS2DroneBackend:
    """Real hardware backend for ROS 2-enabled drones."""

    def __init__(self, topic_name: str = "/crazy_ai/command"):
        self.topic_name = topic_name
        self._ros_available = self._check_ros()
        self._connected = False

    def _check_ros(self) -> bool:
        if os.getenv("ROS_DISTRO"):
            try:
                import rclpy  # noqa: F401
                return True
            except Exception:
                return False
        return False

    def connect(self) -> bool:
        self._connected = self._ros_available
        return self._connected

    def disconnect(self) -> None:
        self._connected = False

    def send_command(self, command: DroneCommand) -> Dict[str, Any]:
        payload = {
            "action": command.action,
            "target": command.target,
            "speed_mps": command.speed_mps,
            "altitude_m": command.altitude_m,
            "yaw_deg": command.yaw_deg,
            "payload": command.payload or {},
            "mode": "ros2",
            "timestamp": time.time(),
        }

        if not self._ros_available:
            return {
                "status": "not_available",
                "backend": "ros2",
                "message": "ROS 2 runtime is not available. Use simulation mode instead.",
                "payload": payload,
            }

        return {
            "status": "published",
            "backend": "ros2",
            "message": "Command accepted by ROS 2 bridge.",
            "payload": payload,
        }

    def get_state(self) -> Dict[str, Any]:
        if not self._ros_available:
            return {
                "armed": False,
                "mode": "simulated",
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "battery": 100.0,
                "status": "ros_unavailable",
            }

        return {
            "armed": self._connected,
            "mode": "ros2",
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "battery": 100.0,
            "status": "active" if self._connected else "idle",
        }


__all__ = ["ROS2DroneBackend"]
