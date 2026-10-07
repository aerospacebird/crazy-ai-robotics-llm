from __future__ import annotations

from ai_robotics.geofence import SeoulWorldCupParkAirfield


def main() -> None:
    samples = [
        ((37.5687, 126.8990), 15.0, "inside-safe"),
        ((37.5660, 126.8950), 8.0, "outside-blocked"),
        ((37.5700, 126.9030), 18.0, "near-boundary-warning"),
    ]

    for position, altitude_m, label in samples:
        result = SeoulWorldCupParkAirfield.evaluate(position, altitude_m=altitude_m)
        print(f"[{label}] {position} -> {result['status']} :: {result['message']}")


if __name__ == "__main__":
    main()
