import json
from typing import Dict, Any, List
from personal_agent.models.gateway import ModelGateway
from personal_agent.tools.registry import ToolRegistry
from personal_agent.policy.engine import PolicyEngine

class AgentRuntime:
    def __init__(self, model_gateway: ModelGateway, tool_registry: ToolRegistry, policy_engine: PolicyEngine):
        self.llm = model_gateway
        self.tools = tool_registry
        self.policy = policy_engine
        self.messages: List[Dict[str, Any]] = []

    def process_request(self, user_prompt: str) -> str:
        self.messages.append({"role": "user", "content": user_prompt})
        
        # 1. Call LLM
        response = self.llm.chat(
            messages=self.messages,
            tools=self.tools.get_all_schemas() if self.tools.get_all_schemas() else None
        )
        
        self.messages.append(response)

        # 2. Check if the LLM wants to use a tool
        if "tool_calls" in response and response["tool_calls"]:
            for tool_call in response["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                
                # In Ollama, arguments are typically returned as a dictionary directly, but handle string just in case
                tool_args = tool_call["function"]["arguments"]
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}
                
                print(f"[Agent] LLM requested tool: {tool_name} with args: {tool_args}")
                
                # 3. Policy Check
                is_allowed, reason = self.policy.check_permission(tool_name, tool_args)
                print(f"[Policy] {reason}")
                
                if is_allowed:
                    # Execute tool
                    func = self.tools.get_tool(tool_name)
                    if func:
                        try:
                            result = func(**tool_args)
                            print(f"[Tool] Execution result: {result}")
                            self.messages.append({
                                "role": "tool",
                                "content": str(result),
                                "name": tool_name
                            })
                        except Exception as e:
                            self.messages.append({
                                "role": "tool",
                                "content": f"Error executing tool: {e}",
                                "name": tool_name
                            })
                else:
                    self.messages.append({
                        "role": "tool",
                        "content": f"Permission denied: {reason}",
                        "name": tool_name
                    })

            # Call LLM again with tool results
            final_response = self.llm.chat(messages=self.messages)
            self.messages.append(final_response)
            return final_response.get("content", "")
            
        # No tool called, return direct response
        return response.get("content", "")
