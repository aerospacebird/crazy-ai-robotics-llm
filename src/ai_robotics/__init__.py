from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .safety import SafetyValidator


class ActionExecutionEngine:
    """Executes robot actions while enforcing safety checks."""

    def __init__(self, safety_validator: Optional[SafetyValidator] = None):
        self.safety_validator = safety_validator or SafetyValidator()

    def execute(
        self,
        action_name: str,
        *,
        target: Optional[str] = None,
        obstacle_distance: float = 3.2,
        speed: float = 0.5,
        position: Tuple[float, float] = (37.5687, 126.8990),
        altitude_m: float = 0.0,
    ) -> Dict[str, Any]:
        normalized = (action_name or "").strip().lower()
        validation = self.safety_validator.validate_command(normalized, position=position, altitude_m=altitude_m)

        if not validation["allowed"]:
            return {
                "action": normalized,
                "target": target,
                "allowed": False,
                "status": "blocked",
                "reason": validation["reason"],
                "geofence": validation["geofence"],
                "obstacle_distance": obstacle_distance,
                "speed": speed,
            }

        if normalized in {"move", "navigate", "go", "travel"}:
            return {
                "action": normalized,
                "target": target,
                "allowed": True,
                "status": "executed",
                "reason": f"Navigating toward {target or 'waypoint'} within the protected airspace.",
                "geofence": validation["geofence"],
                "obstacle_distance": obstacle_distance,
                "speed": speed,
            }

        if normalized in {"scan", "inspect", "observe"}:
            return {
                "action": normalized,
                "target": target,
                "allowed": True,
                "status": "executed",
                "reason": "Perception task executed with safety gate cleared.",
                "geofence": validation["geofence"],
                "obstacle_distance": obstacle_distance,
                "speed": speed,
            }

        if normalized in {"stop", "halt", "return", "return to base", "hold position"}:
            return {
                "action": normalized,
                "target": target,
                "allowed": True,
                "status": "executed",
                "reason": "Safety hold or return command executed.",
                "geofence": validation["geofence"],
                "obstacle_distance": obstacle_distance,
                "speed": speed,
            }

        return {
            "action": normalized,
            "target": target,
            "allowed": True,
            "status": "executed",
            "reason": "Command completed within the geofenced virtual airfield.",
            "geofence": validation["geofence"],
            "obstacle_distance": obstacle_distance,
            "speed": speed,
        }


DEFAULT_ACTION_ENGINE = ActionExecutionEngine()


__all__ = ["ActionExecutionEngine", "DEFAULT_ACTION_ENGINE"]
