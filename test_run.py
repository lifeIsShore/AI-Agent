import sys
import os

# Add src to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from datetime import datetime
from personal_agent.models.gateway import ModelGateway
from personal_agent.tools.registry import ToolRegistry
from personal_agent.policy.engine import PolicyEngine
from personal_agent.agent.runtime import AgentRuntime

def get_current_time(timezone: str = "local") -> str:
    """Get the current time."""
    return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def main():
    gateway = ModelGateway(provider="ollama")
    registry = ToolRegistry()
    policy = PolicyEngine()
    
    # Register a simple tool
    registry.register(
        name="get_current_time",
        schema={
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone to get the time for, e.g. 'local'"
                    }
                }
            }
        },
        func=get_current_time
    )
    
    runtime = AgentRuntime(
        model_gateway=gateway,
        tool_registry=registry,
        policy_engine=policy
    )
    
    print("User: What time is it right now?")
    response = runtime.process_request("What time is it right now?")
    print(f"Agent: {response}")

if __name__ == "__main__":
    main()
