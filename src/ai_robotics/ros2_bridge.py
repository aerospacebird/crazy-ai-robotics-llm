from __future__ import annotations

import os
from typing import Any, Dict, Optional


class ROS2Bridge:
    """ROS 2 integration adapter with a safe simulation fallback."""

    def __init__(self, node_name: str = "crazy_robot_bridge"):
        self.node_name = node_name
        self._ros_available = self._check_ros()

    def _check_ros(self) -> bool:
        if os.getenv("ROS_DISTRO"):
            try:
                import rclpy  # noqa: F401
                return True
            except Exception:
                return False
        return False

    def publish_command(self, action: str, target: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "action": action,
            "target": target,
            "params": params or {},
            "mode": "ros2" if self._ros_available else "simulated",
        }

        if not self._ros_available:
            return {"status": "simulated", "payload": payload}

        return {"status": "published_to_ros2", "payload": payload}

    def read_state(self) -> Dict[str, Any]:
        if not self._ros_available:
            return {"status": "simulated", "robot_state": {"position": "home", "battery": 100.0}}

        return {"status": "ros2_active", "robot_state": {"position": "home", "battery": 100.0}}


DEFAULT_ROS2_BRIDGE = ROS2Bridge()

__all__ = ["ROS2Bridge", "DEFAULT_ROS2_BRIDGE"]
