import json
import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from personal_agent.models.gateway import ModelGateway
from personal_agent.tools.registry import ToolRegistry
from personal_agent.policy.engine import PolicyEngine
from personal_agent.policy.proposal import ActionProposal, STATUS_EXECUTED, STATUS_FAILED, STATUS_EXPIRED
from personal_agent.security.audit import AuditLogger
from personal_agent.events.bus import EventBus
from personal_agent.events.event import AgentEvent, EVENT_ACTION_EXECUTED, EVENT_ACTION_FAILED

class AgentRuntime:
    def __init__(
        self,
        model_gateway: ModelGateway,
        tool_registry: ToolRegistry,
        policy_engine: PolicyEngine,
        audit_logger: Optional[AuditLogger] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.llm = model_gateway
        self.tools = tool_registry
        self.policy = policy_engine
        self.audit_logger = audit_logger or AuditLogger()
        self.event_bus = event_bus
        self.messages: List[Dict[str, Any]] = []
        self.idempotency_cache: Dict[str, Dict[str, Any]] = {}

    def get_idempotency_key(self, action: str, target: str, parameters: Dict[str, Any]) -> str:
        """Calculates a deterministic idempotency key for an action proposal."""
        raw_str = f"{action}:{target}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:16]

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
                
                target_str = str(tool_args.get("msg_id") or tool_args.get("event_id") or tool_args.get("task_id") or "system")
                idem_key = self.get_idempotency_key(tool_name, target_str, tool_args)
                execution_id = f"exec_{uuid.uuid4().hex[:10]}"

                # Check Idempotency Cache (Prevent duplicate execution on network retries)
                if idem_key in self.idempotency_cache:
                    cached_res = self.idempotency_cache[idem_key]
                    print(f"[Idempotency Cache Hit] Tool '{tool_name}' already executed cleanly (Key: {idem_key}). Returning cached result.")
                    self.messages.append({
                        "role": "tool",
                        "content": str(cached_res["result"]),
                        "name": tool_name
                    })
                    continue

                # 3. Create ActionProposal & Evaluate Policy
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
                            proposal.status = STATUS_EXECUTED
                            print(f"[Tool Execution {execution_id}] Success ({elapsed:.2f}s): {result}")

                            # Cache execution result with execution_id
                            self.idempotency_cache[idem_key] = {
                                "execution_id": execution_id,
                                "proposal_id": proposal.proposal_id,
                                "result": result,
                                "timestamp": time.time()
                            }

                            self.audit_logger.log_proposal(
                                proposal=proposal,
                                policy_decision=reason,
                                user_approved=user_approved,
                                execution_status="SUCCESS",
                                execution_result=result,
                                latency_sec=elapsed
                            )

                            # Publish ACTION_EXECUTED event to EventBus
                            if self.event_bus:
                                self.event_bus.publish(AgentEvent(
                                    event_type=EVENT_ACTION_EXECUTED,
                                    source="AgentRuntime",
                                    entity_id=proposal.proposal_id,
                                    payload={
                                        "execution_id": execution_id,
                                        "idempotency_key": idem_key,
                                        "action": tool_name,
                                        "target": target_str,
                                        "result": str(result)
                                    }
                                ))

                            self.messages.append({
                                "role": "tool",
                                "content": str(result),
                                "name": tool_name
                            })
                        except Exception as e:
                            elapsed = time.time() - start_time
                            proposal.status = STATUS_FAILED
                            err_msg = str(e)
                            self.audit_logger.log_proposal(
                                proposal=proposal,
                                policy_decision=reason,
                                user_approved=user_approved,
                                execution_status="FAILED",
                                execution_result=err_msg,
                                latency_sec=elapsed
                            )

                            if self.event_bus:
                                self.event_bus.publish(AgentEvent(
                                    event_type=EVENT_ACTION_FAILED,
                                    source="AgentRuntime",
                                    entity_id=proposal.proposal_id,
                                    payload={
                                        "execution_id": execution_id,
                                        "idempotency_key": idem_key,
                                        "action": tool_name,
                                        "target": target_str,
                                        "error": err_msg
                                    }
                                ))

                            self.messages.append({
                                "role": "tool",
                                "content": f"Error executing tool: {err_msg}",
                                "name": tool_name
                            })
                else:
                    self.audit_logger.log_proposal(
                        proposal=proposal,
                        policy_decision=reason,
                        user_approved=user_approved,
                        execution_status=proposal.status,
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
