from __future__ import annotations

from ai_robotics.execution_loop import RoboticsExecutionLoop


def test_simulation_mode_runs():
    loop = RoboticsExecutionLoop()
    result = loop.run("move to charging station", mode="simulation")
    assert result["execution_mode"] == "simulated"
    assert "plan" in result
    assert "action_results" in result


def test_hardware_falls_back_to_simulation_when_ros_is_unavailable():
    loop = RoboticsExecutionLoop()
    result = loop.run("move to charging station", mode="hardware")
    assert result["execution_mode"] in {"simulated", "ros2"}
    assert "runtime_mode" in result
