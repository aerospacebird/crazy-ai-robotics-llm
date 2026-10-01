from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ai_robotics.execution_loop import RoboticsExecutionLoop
from ai_robotics.monitoring import MonitoringService, RobotTelemetry


class DashboardService:
    """Lightweight dashboard service for AI robot status monitoring."""

    def __init__(self, monitoring: Optional[MonitoringService] = None):
        self.monitoring = monitoring or MonitoringService()

    def capture(self, command: str, result: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = RobotTelemetry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            command=command,
            intent=str(result.get("plan", {}).get("intent", "unknown")),
            target=str(result.get("plan", {}).get("target", "unknown")),
            safety_status=str(result.get("safety_status", "unknown")),
            execution_mode=str(result.get("execution_mode", "unknown")),
            battery=float(result.get("final_state", {}).get("battery", 0.0)),
            position=str(result.get("final_state", {}).get("position", "unknown")),
            obstacle_distance=float(result.get("final_state", {}).get("obstacle_distance", 0.0)),
            metadata={"action_results": result.get("action_results", [])},
        )
        return self.monitoring.log_event(telemetry)


DEFAULT_DASHBOARD_SERVICE = DashboardService()


__all__ = ["DashboardService", "DEFAULT_DASHBOARD_SERVICE"]
