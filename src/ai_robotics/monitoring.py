from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RobotTelemetry:
    timestamp: str
    command: str
    intent: str
    target: str
    safety_status: str
    execution_mode: str
    battery: float
    position: str
    obstacle_distance: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class MonitoringService:
    """Basic monitoring layer for robot telemetry and event logging."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(os.getcwd(), "logs", "telemetry.jsonl")
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.events: List[RobotTelemetry] = []

    def log_event(self, telemetry: RobotTelemetry) -> Dict[str, Any]:
        self.events.append(telemetry)
        with open(self.storage_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "timestamp": telemetry.timestamp,
                "command": telemetry.command,
                "intent": telemetry.intent,
                "target": telemetry.target,
                "safety_status": telemetry.safety_status,
                "execution_mode": telemetry.execution_mode,
                "battery": telemetry.battery,
                "position": telemetry.position,
                "obstacle_distance": telemetry.obstacle_distance,
                "metadata": telemetry.metadata,
            }) + "\n")
        return {"status": "logged", "path": self.storage_path, "entries": len(self.events)}

    def read_events(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.storage_path):
            return []
        records: List[Dict[str, Any]] = []
        with open(self.storage_path, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records


DEFAULT_MONITORING_SERVICE = MonitoringService()

__all__ = ["RobotTelemetry", "MonitoringService", "DEFAULT_MONITORING_SERVICE"]
