from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SensorFrame:
    obstacle_distance: float = 5.0
    object_count: int = 0
    detected_objects: List[str] = field(default_factory=list)
    scene_tags: List[str] = field(default_factory=list)
    battery: float = 100.0
    position: str = "home"
    confidence: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict)


class VisionSensorSystem:
    """Sensor and vision wrapper for environment-aware robot decisions."""

    def __init__(self, frame: Optional[SensorFrame] = None):
        self.frame = frame or SensorFrame()

    def detect_objects(self, objects: Optional[List[str]] = None, scene_tags: Optional[List[str]] = None) -> SensorFrame:
        self.frame.detected_objects = objects or ["desk", "chair", "door"]
        self.frame.scene_tags = scene_tags or ["indoor", "structured"]
        self.frame.object_count = len(self.frame.detected_objects)
        self.frame.confidence = 0.88
        self.frame.raw = {
            "detected_objects": self.frame.detected_objects,
            "scene_tags": self.frame.scene_tags,
            "object_count": self.frame.object_count,
        }
        return self.frame

    def estimate_scene(self, obstacle_distance: float = 4.0, battery: float = 100.0, position: str = "home") -> SensorFrame:
        self.frame.obstacle_distance = obstacle_distance
        self.frame.battery = battery
        self.frame.position = position
        self.frame.confidence = 0.9 if obstacle_distance > 0 else 0.0
        self.frame.raw.update({
            "obstacle_distance": obstacle_distance,
            "battery": battery,
            "position": position,
        })
        return self.frame

    def get_frame(self) -> SensorFrame:
        return self.frame


__all__ = ["SensorFrame", "VisionSensorSystem"]
