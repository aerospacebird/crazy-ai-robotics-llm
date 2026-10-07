from __future__ import annotations

from typing import Any, Dict, List, Optional

from ai_robotics.action_engine import ActionExecutionEngine
from ai_robotics.drone_controller import DroneController
from ai_robotics.llm import LLMPlan, LLMPlanner
from ai_robotics.ros2_bridge import ROS2Bridge
from ai_robotics.safety import SafetyValidator
from ai_robotics.simulator import RobotSimulator
from ai_robotics.vision import VisionSensorSystem


class RoboticsExecutionLoop:
    """End-to-end execution loop with both ROS 2 hardware and simulation support."""

    def __init__(
        self,
        planner: Optional[LLMPlanner] = None,
        engine: Optional[ActionExecutionEngine] = None,
        vision: Optional[VisionSensorSystem] = None,
        safety: Optional[SafetyValidator] = None,
        simulator: Optional[RobotSimulator] = None,
        ros_bridge: Optional[ROS2Bridge] = None,
        controller: Optional[DroneController] = None,
    ):
        self.planner = planner or LLMPlanner()
        self.engine = engine or ActionExecutionEngine(safety_validator=safety or SafetyValidator())
        self.vision = vision or VisionSensorSystem()
        self.simulator = simulator or RobotSimulator(engine=self.engine, planner=self.planner)
        self.ros_bridge = ros_bridge or ROS2Bridge()
        self.controller = controller or DroneController(mode="auto")

    def run(self, command: str, prefer_ros: bool = False, mode: Optional[str] = None) -> Dict[str, Any]:
        plan: LLMPlan = self.planner.plan(command)
        sensor = self.vision.estimate_scene(obstacle_distance=3.2, battery=90.0, position="home")
        sensor = self.vision.detect_objects(objects=["desk", "charge_station"], scene_tags=["indoor", "navigation"])

        action_results = self.engine.execute_plan(
            plan.actions,
            target=plan.target,
            obstacle_distance=sensor.obstacle_distance,
        )
        safety_status = "ok" if all(item["allowed"] for item in action_results) else "blocked"

        runtime_mode = mode or self.controller.resolve_runtime_mode(prefer_ros=prefer_ros)

        if runtime_mode == "hardware" and self.controller.hardware_backend._ros_available:
            execution_mode = "ros2"
            first_action = plan.actions[0] if plan.actions else "hold"
            hardware_result = self.controller.execute(
                first_action,
                target=(0.0, 0.0, 2.0),
                altitude_m=2.0,
                speed_mps=1.5,
                mode="hardware",
            )
            action_results = [{
                "action": first_action,
                "allowed": True,
                "status": hardware_result["result"]["status"],
                "backend": "hardware",
                "payload": hardware_result,
            }]
            safety_status = "ok"
        else:
            execution_mode = "simulated"
            simulation = self.simulator.simulate_command(command)
            action_results = simulation["simulation_results"]
            safety_status = "ok" if all(item["status"] == "executed" for item in action_results) else "blocked"

        final_state = {
            "position": sensor.position,
            "battery": sensor.battery,
            "obstacle_distance": sensor.obstacle_distance,
            "scene_tags": sensor.scene_tags,
            "execution_mode": execution_mode,
        }

        return {
            "command": command,
            "plan": {
                "intent": plan.intent,
                "target": plan.target,
                "confidence": plan.confidence,
                "actions": plan.actions,
            },
            "sensor_frame": {
                "obstacle_distance": sensor.obstacle_distance,
                "object_count": sensor.object_count,
                "scene_tags": sensor.scene_tags,
                "battery": sensor.battery,
                "position": sensor.position,
                "confidence": sensor.confidence,
            },
            "action_results": action_results,
            "safety_status": safety_status,
            "execution_mode": execution_mode,
            "final_state": final_state,
            "runtime_mode": runtime_mode,
        }


DEFAULT_EXECUTION_LOOP = RoboticsExecutionLoop()

__all__ = ["RoboticsExecutionLoop", "DEFAULT_EXECUTION_LOOP"]
