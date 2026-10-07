from ai_robotics.geofence import SeoulWorldCupParkAirfield


def test_geofence_allows_center_point():
    result = SeoulWorldCupParkAirfield.evaluate((37.5687, 126.8990), altitude_m=15.0)
    assert result["status"] == "safe"


def test_geofence_blocks_outside_point():
    result = SeoulWorldCupParkAirfield.evaluate((37.5650, 126.8940), altitude_m=10.0)
    assert result["status"] == "blocked"


def test_geofence_warns_on_buffer_boundary():
    result = SeoulWorldCupParkAirfield.evaluate((37.5708, 126.9030), altitude_m=20.0)
    assert result["status"] in {"warning", "blocked"}


# The virtual airfield is used as a simulation perimeter for the Seoul World Cup Park use case.
# It enforces a protected geofence while allowing a bounded operating space near the center.
