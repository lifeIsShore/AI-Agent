import json
import time
from typing import Dict, Any, List, Optional
from personal_agent.models.gateway import ModelGateway
from personal_agent.tools.registry import ToolRegistry
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import ActionProposal
from personal_agent.security.audit import AuditLogger

class AgentRuntime:
    def __init__(
        self,
        model_gateway: ModelGateway,
        tool_registry: ToolRegistry,
        policy_engine: PolicyEngine,
        audit_logger: Optional[AuditLogger] = None
    ):
        self.llm = model_gateway
        self.tools = tool_registry
        self.policy = policy_engine
        self.audit_logger = audit_logger or AuditLogger()
        self.messages: List[Dict[str, Any]] = []

    def process_request(self, user_prompt: str, user_approved: bool = False) -> str:
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
                
                tool_args = tool_call["function"]["arguments"]
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}
                
                print(f"[Agent] LLM requested tool: {tool_name} with args: {tool_args}")
                
                # 3. Create ActionProposal & Evaluate Policy
                target_str = str(tool_args.get("msg_id") or tool_args.get("event_id") or tool_args.get("task_id") or "system")
                proposal = self.policy.create_proposal(
                    action=tool_name,
                    target=target_str,
                    parameters=tool_args,
                    reason=f"LLM tool invocation request for '{tool_name}'"
                )

                is_allowed, reason = self.policy.check_proposal(proposal, user_approved=user_approved)
                print(f"[Policy Proposal {proposal.proposal_id}] Risk: {proposal.risk_level} | Decision: {reason}")

                # 4. Tool Execution & Audit Logging
                start_time = time.time()
                if is_allowed:
                    func = self.tools.get_tool(tool_name)
                    if func:
                        try:
                            result = func(**tool_args)
                            elapsed = time.time() - start_time
                            proposal.status = "EXECUTED"
                            print(f"[Tool Execution] Success ({elapsed:.2f}s): {result}")

                            self.audit_logger.log_proposal(
                                proposal=proposal,
                                policy_decision=reason,
                                user_approved=user_approved,
                                execution_status="SUCCESS",
                                execution_result=result,
                                latency_sec=elapsed
                            )

                            self.messages.append({
                                "role": "tool",
                                "content": str(result),
                                "name": tool_name
                            })
                        except Exception as e:
                            elapsed = time.time() - start_time
                            proposal.status = "FAILED"
                            self.audit_logger.log_proposal(
                                proposal=proposal,
                                policy_decision=reason,
                                user_approved=user_approved,
                                execution_status="FAILED",
                                execution_result=str(e),
                                latency_sec=elapsed
                            )

                            self.messages.append({
                                "role": "tool",
                                "content": f"Error executing tool: {e}",
                                "name": tool_name
                            })
                else:
                    proposal.status = "BLOCKED"
                    self.audit_logger.log_proposal(
                        proposal=proposal,
                        policy_decision=reason,
                        user_approved=user_approved,
                        execution_status="BLOCKED",
                        execution_result=None,
                        latency_sec=0.0
                    )

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
