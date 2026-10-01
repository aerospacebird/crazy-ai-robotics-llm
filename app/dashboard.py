from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from ai_robotics.execution_loop import RoboticsExecutionLoop
from ai_robotics.llm import LLMPlanner
from ai_robotics.monitoring import MonitoringService
from ai_robotics.ros2_bridge import ROS2Bridge
from ai_robotics.simulator import RobotSimulator
from ai_robotics.dashboard import DashboardService

app = FastAPI(title="Crazy AI Robotics System", version="0.1.0")


class CommandRequest(BaseModel):
    command: str


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
    simulator = RobotSimulator()
    return simulator.simulate_command(request.command)


@app.post("/execute")
def execute_command(request: CommandRequest):
    loop = RoboticsExecutionLoop()
    result = loop.run(request.command)
    dashboard = DashboardService(MonitoringService())
    dashboard.capture(request.command, {
        "plan": result.plan,
        "safety_status": result.safety_status,
        "execution_mode": result.execution_mode,
        "final_state": result.final_state,
        "action_results": result.action_results,
    })
    return {
        "command": result.command,
        "plan": result.plan,
        "sensor_frame": result.sensor_frame,
        "action_results": result.action_results,
        "safety_status": result.safety_status,
        "execution_mode": result.execution_mode,
        "final_state": result.final_state,
    }


@app.get("/dashboard")
def dashboard():
    monitor = MonitoringService()
    return {"entries": monitor.read_events()}


@app.get("/ros")
def ros_status():
    bridge = ROS2Bridge()
    return bridge.read_state()
