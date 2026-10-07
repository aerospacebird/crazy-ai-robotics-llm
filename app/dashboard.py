from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from ai_robotics.dashboard import DashboardService
from ai_robotics.execution_loop import RoboticsExecutionLoop
from ai_robotics.llm import LLMPlanner
from ai_robotics.monitoring import MonitoringService
from ai_robotics.ros2_bridge import ROS2Bridge
from ai_robotics.simulator import RobotSimulator

app = FastAPI(title="Crazy AI Robotics System", version="0.1.0")


class CommandRequest(BaseModel):
    command: str
    mode: Optional[str] = None
    prefer_ros: bool = False


def _run_requested_command(request: CommandRequest, *, mode_override: Optional[str] = None):
    loop = RoboticsExecutionLoop()
    mode = mode_override or request.mode
    result = loop.run(request.command, prefer_ros=request.prefer_ros, mode=mode)
    dashboard = DashboardService(MonitoringService())
    dashboard.capture(request.command, {
        "plan": result["plan"],
        "safety_status": result["safety_status"],
        "execution_mode": result["execution_mode"],
        "final_state": result["final_state"],
        "action_results": result["action_results"],
        "runtime_mode": result.get("runtime_mode"),
    })
    return {
        "command": result["command"],
        "plan": result["plan"],
        "sensor_frame": result["sensor_frame"],
        "action_results": result["action_results"],
        "safety_status": result["safety_status"],
        "execution_mode": result["execution_mode"],
        "final_state": result["final_state"],
        "runtime_mode": result.get("runtime_mode"),
    }


@app.get("/")
def read_root():
    return {
        "message": "Crazy AI Robotics System is running.",
        "systems": [
            "LLM integration",
            "Robot control",
            "Simulation",
            "Vision and sensors",
            "ROS 2 bridge",
            "Monitoring dashboard",
            "Hardware runtime",
        ],
    }


@app.post("/command")
def handle_command(request: CommandRequest):
    plan = LLMPlanner().plan(request.command)
    return {
        "status": "received",
        "command": request.command,
        "intent": plan.intent,
        "target": plan.target,
        "actions": plan.actions,
        "mode": request.mode,
    }


@app.post("/plan")
def generate_plan(request: CommandRequest):
    plan = LLMPlanner().plan(request.command)
    return {
        "intent": plan.intent,
        "target": plan.target,
        "confidence": plan.confidence,
        "actions": plan.actions,
    }


@app.post("/simulate")
def simulate_command(request: CommandRequest):
    return _run_requested_command(request, mode_override="simulation")


@app.post("/hardware")
def hardware_command(request: CommandRequest):
    return _run_requested_command(request, mode_override="hardware")


@app.post("/auto")
def auto_command(request: CommandRequest):
    return _run_requested_command(request, mode_override="auto")


@app.post("/execute")
def execute_command(request: CommandRequest):
    return _run_requested_command(request)


@app.get("/dashboard")
def dashboard():
    monitor = MonitoringService()
    return {"entries": monitor.read_events()}


@app.get("/ros")
def ros_status():
    bridge = ROS2Bridge()
    return bridge.read_state()
