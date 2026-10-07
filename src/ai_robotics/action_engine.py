from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .geofence import SeoulWorldCupParkAirfield, VirtualAirfield


@dataclass
class SafetyDecision:
    allowed: bool
    reason: str
    status: str
    geofence: Dict[str, Any]
    altitude_m: float


class SafetyValidator:
    """Rule-based safety gate used before robot commands are executed."""

    def __init__(
        self,
        geofence: Optional[VirtualAirfield] = None,
        max_altitude_m: float = 50.0,
        buffer_m: float = 20.0,
    ):
        self.geofence = geofence or SeoulWorldCupParkAirfield
        self.max_altitude_m = max_altitude_m
        self.buffer_m = buffer_m

    def validate_command(
        self,
        command: str,
        position: Tuple[float, float] = (37.5687, 126.8990),
        altitude_m: float = 0.0,
    ) -> Dict[str, Any]:
        normalized = (command or "").strip().lower()
        geofence_result = self.geofence.evaluate(
            position,
            altitude_m=altitude_m,
            buffer_m=self.buffer_m,
            max_altitude_m=self.max_altitude_m,
        )

        if normalized in {"emergency stop", "halt", "stop", "return to base", "return-home", "hold position"}:
            return {
                "allowed": True,
                "status": "safe",
                "reason": "Emergency or hold action approved.",
                "geofence": geofence_result,
                "altitude_m": altitude_m,
            }

        if geofence_result["status"] in {"blocked", "warning"}:
            return {
                "allowed": False,
                "status": geofence_result["status"],
                "reason": geofence_result["message"],
                "geofence": geofence_result,
                "altitude_m": altitude_m,
            }

        return {
            "allowed": True,
            "status": "safe",
            "reason": "Command is within the protected virtual airfield envelope.",
            "geofence": geofence_result,
            "altitude_m": altitude_m,
        }


DEFAULT_SAFETY_VALIDATOR = SafetyValidator()


__all__ = ["SafetyDecision", "SafetyValidator", "DEFAULT_SAFETY_VALIDATOR"]
