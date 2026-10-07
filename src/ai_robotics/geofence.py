from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


def _point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[(i + 1) % n]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi)
        if intersect:
            inside = not inside
    return inside


@dataclass(frozen=True)
class GeofencePoint:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class GeofenceResult:
    status: str
    inside: bool
    distance_to_boundary_m: float
    altitude_m: float
    max_altitude_m: float
    buffer_m: float
    message: str


class VirtualAirfield:
    """Simple geofence model for a protected virtual airfield."""

    def __init__(
        self,
        polygon: Optional[List[Tuple[float, float]]] = None,
        max_altitude_m: float = 50.0,
        buffer_m: float = 20.0,
        name: str = "virtual-airfield",
    ):
        self.polygon = polygon or []
        self.max_altitude_m = max_altitude_m
        self.buffer_m = buffer_m
        self.name = name

    def contains(self, position: Tuple[float, float]) -> bool:
        if not self.polygon:
            return True
        return _point_in_polygon(position, self.polygon)

    def distance_to_boundary_m(self, position: Tuple[float, float]) -> float:
        if not self.polygon:
            return 0.0

        # Approximate planar distance using a local metric. This is intentionally a lightweight
        # simulation-friendly implementation rather than full GIS-grade geometry.
        min_distance = float("inf")
        for i in range(len(self.polygon)):
            x1, y1 = self.polygon[i]
            x2, y2 = self.polygon[(i + 1) % len(self.polygon)]
            x, y = position
            dx = x2 - x1
            dy = y2 - y1
            segment_length_sq = dx * dx + dy * dy
            if segment_length_sq == 0:
                dist = (x - x1) ** 2 + (y - y1) ** 2
            else:
                t = ((x - x1) * dx + (y - y1) * dy) / segment_length_sq
                t = max(0.0, min(1.0, t))
                px = x1 + t * dx
                py = y1 + t * dy
                dist = (x - px) ** 2 + (y - py) ** 2
            min_distance = min(min_distance, dist)
        return min_distance ** 0.5

    def evaluate(
        self,
        position: Tuple[float, float],
        altitude_m: float = 0.0,
        buffer_m: Optional[float] = None,
        max_altitude_m: Optional[float] = None,
    ) -> Dict[str, Any]:
        buffer_m = self.buffer_m if buffer_m is None else buffer_m
        max_altitude_m = self.max_altitude_m if max_altitude_m is None else max_altitude_m

        if not self.polygon:
            return {
                "status": "safe",
                "inside": True,
                "distance_to_boundary_m": 0.0,
                "altitude_m": altitude_m,
                "max_altitude_m": max_altitude_m,
                "buffer_m": buffer_m,
                "message": "No geofence defined; operation is unrestricted.",
            }

        inside = self.contains(position)
        boundary_distance = self.distance_to_boundary_m(position)
        if altitude_m > max_altitude_m:
            return {
                "status": "blocked",
                "inside": inside,
                "distance_to_boundary_m": boundary_distance,
                "altitude_m": altitude_m,
                "max_altitude_m": max_altitude_m,
                "buffer_m": buffer_m,
                "message": f"Altitude {altitude_m}m exceeds the allowed {max_altitude_m}m ceiling.",
            }
        if inside and boundary_distance >= buffer_m:
            return {
                "status": "safe",
                "inside": True,
                "distance_to_boundary_m": boundary_distance,
                "altitude_m": altitude_m,
                "max_altitude_m": max_altitude_m,
                "buffer_m": buffer_m,
                "message": "Drone remains within the protected virtual airfield.",
            }
        if inside and boundary_distance < buffer_m:
            return {
                "status": "warning",
                "inside": True,
                "distance_to_boundary_m": boundary_distance,
                "altitude_m": altitude_m,
                "max_altitude_m": max_altitude_m,
                "buffer_m": buffer_m,
                "message": "Approaching the geofence buffer. Reduce speed and hold position.",
            }
        return {
            "status": "blocked",
            "inside": False,
            "distance_to_boundary_m": boundary_distance,
            "altitude_m": altitude_m,
            "max_altitude_m": max_altitude_m,
            "buffer_m": buffer_m,
            "message": "Position is outside the protected virtual airfield. Flight is denied.",
        }


SeoulWorldCupParkAirfield = VirtualAirfield(
    polygon=[
        (37.5673, 126.8960),
        (37.5676, 126.9028),
        (37.5704, 126.9036),
        (37.5712, 126.9004),
        (37.5705, 126.8969),
        (37.5687, 126.8948),
    ],
    max_altitude_m=50.0,
    buffer_m=20.0,
    name="seoul-worldcup-park-virtual-airfield",
)


def evaluate_geofence(
    position: Tuple[float, float],
    altitude_m: float = 0.0,
    *,
    geofence: Optional[VirtualAirfield] = None,
    buffer_m: Optional[float] = None,
    max_altitude_m: Optional[float] = None,
) -> Dict[str, Any]:
    geofence = geofence or SeoulWorldCupParkAirfield
    return geofence.evaluate(position, altitude_m, buffer_m=buffer_m, max_altitude_m=max_altitude_m)


__all__ = [
    "GeofencePoint",
    "GeofenceResult",
    "VirtualAirfield",
    "SeoulWorldCupParkAirfield",
    "evaluate_geofence",
]


# This is a lightweight geofence model designed for simulation and rule-enforcement in
# a protected public-park environment. It is not intended to replace a full GIS or
# aviation-grade geofencing system when deployed to real hardware.
