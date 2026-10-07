from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Tuple


@dataclass
class DroneCommand:
    """Single drone command that can be executed on real hardware or in simulation."""

    action: str
    target: Optional[Tuple[float, float, float]] = None
    speed_mps: float = 1.0
    altitude_m: Optional[float] = None
    yaw_deg: Optional[float] = None
    payload: Optional[Dict[str, Any]] = None


class DroneBackend(Protocol):
    def connect(self) -> bool:
        ...

    def disconnect(self) -> None:
        ...

    def send_command(self, command: DroneCommand) -> Dict[str, Any]:
        ...

    def get_state(self) -> Dict[str, Any]:
        ...


__all__ = ["DroneCommand", "DroneBackend"]
