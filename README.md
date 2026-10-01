# Crazy AI & Robotics System

This repository is the starting point for a hybrid AI + robotics system that combines:

- a language model for command understanding and task planning
- sensor and perception modules for environment awareness
- safety logic for real-time validation
- robot control orchestration for execution
- simulation and ROS 2 integration for real-world deployment readiness
- monitoring and dashboard support for telemetry and command tracking

## Architecture overview

The system is layered to support production-style autonomous robot behavior:

1. User input and natural-language command parsing
2. LLM-driven intent extraction and planning
3. Sensor and vision perception
4. Safety validation and emergency checks
5. Robot action execution
6. ROS 2 or simulation bridge
7. Monitoring dashboard and event logging

## Included capabilities

- OpenAI-compatible LLM adapter with rule-based fallback
- Robot action engine
- Safety validation engine
- Simulator for safe validation before execution
- Vision and sensor frame abstraction
- ROS 2 bridge adapter
- Monitoring and dashboard service

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_demo.py
```

## Run the API

```bash
uvicorn app.dashboard:app --reload
```

## Example requests

```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command":"move to the charging dock"}'

curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"scan the room"}'
```

## Environment variables

- `OPENAI_API_KEY` for OpenAI LLM integration
- `ROS_DISTRO` for ROS 2 runtime detection

## Next milestones

- add real camera/LiDAR sensor drivers
- plug in external ROS 2 topics and services
- expand monitoring to a UI dashboard
- add persistent robot telemetry storage
