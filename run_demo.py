from ai_robotics.execution_loop import RoboticsExecutionLoop


def main():
    loop = RoboticsExecutionLoop()
    command = input("Enter a robot command: ").strip()
    result = loop.run(command)
    print("\n=== Execution result ===")
    print({
        "command": result.command,
        "intent": result.plan["intent"],
        "target": result.plan["target"],
        "safety_status": result.safety_status,
        "execution_mode": result.execution_mode,
        "final_state": result.final_state,
    })


if __name__ == "__main__":
    main()
