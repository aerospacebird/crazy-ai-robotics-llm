from __future__ import annotations

from typing import Any, Dict, Optional

from .hardware_backend import ROS2DroneBackend
from .interfaces import DroneCommand
from .simulation_backend import SimulatedDroneBackend


class DroneController:
    """Runtime-selectable controller that supports both real hardware and simulation."""

    def __init__(
        self,
        mode: str = "auto",
        hardware_backend: Optional[ROS2DroneBackend] = None,
        simulation_backend: Optional[SimulatedDroneBackend] = None,
    ):
        self.mode = mode
        self.hardware_backend = hardware_backend or ROS2DroneBackend()
        self.simulation_backend = simulation_backend or SimulatedDroneBackend()

    def resolve_backend(self):
        if self.mode == "hardware":
            return self.hardware_backend
        if self.mode == "simulation":
            return self.simulation_backend

        if self.hardware_backend._ros_available:
            return self.hardware_backend
        return self.simulation_backend

    def connect(self) -> bool:
        backend = self.resolve_backend()
        return backend.connect()

    def disconnect(self) -> None:
        self.resolve_backend().disconnect()

    def execute(
        self,
        action: str,
        *,
        target: Optional[tuple] = None,
        altitude_m: Optional[float] = None,
        speed_mps: float = 1.0,
        yaw_deg: Optional[float] = None,
        payload: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        backend = self.resolve_backend() if mode is None else (
            self.hardware_backend if mode == "hardware" else self.simulation_backend
        )

        cmd = DroneCommand(
            action=action,
            target=target,
            altitude_m=altitude_m,
            speed_mps=speed_mps,
            yaw_deg=yaw_deg,
            payload=payload,
        )
        result = backend.send_command(cmd)
        state = backend.get_state()

        selected_mode = mode or (
            "hardware" if backend is self.hardware_backend else "simulation"
        )
        return {
            "selected_mode": selected_mode,
            "result": result,
            "state": state,
        }

    def get_state(self) -> Dict[str, Any]:
        return self.resolve_backend().get_state()

    def resolve_runtime_mode(self, prefer_ros: bool = False) -> str:
        if prefer_ros and self.hardware_backend._ros_available:
            return "hardware"
        if self.mode in {"hardware", "simulation"}:
            return self.mode
        if self.hardware_backend._ros_available:
            return "hardware"
        return "simulation"


__all__ = ["DroneController"]
