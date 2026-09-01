import time
from typing import List, Dict, Any, Optional
from personal_agent.models.ollama import OllamaClient
from personal_agent.telemetry.tracer import AgentTracer
from personal_agent.telemetry.trace import TraceContext

class ModelGateway:
    def __init__(self, provider: str = "ollama", tracer: Optional[AgentTracer] = None):
        self.provider = provider
        self.tracer = tracer or AgentTracer()
        if self.provider == "ollama":
            self.client = OllamaClient()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _estimate_tokens(self, text: str) -> int:
        """Estimates token count (~4 chars per token) when server does not return usage stats."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    def generate(self, prompt: str, system: Optional[str] = None, format: Optional[str] = None, trace_ctx: Optional[TraceContext] = None) -> str:
        start = time.time()
        res = self.client.generate(prompt=prompt, system=system, format=format)
        elapsed = time.time() - start

        if trace_ctx and self.tracer:
            p_tokens = self._estimate_tokens(prompt)
            c_tokens = self._estimate_tokens(res)
            self.tracer.record_llm_call(
                trace_ctx=trace_ctx,
                model=self.provider,
                intent="GENERATE",
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                latency_sec=elapsed
            )

        return res

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, trace_ctx: Optional[TraceContext] = None) -> Dict[str, Any]:
        start = time.time()
        res = self.client.chat(messages=messages, tools=tools)
        elapsed = time.time() - start

        if trace_ctx and self.tracer:
            prompt_text = "".join(m.get("content", "") for m in messages)
            comp_text = str(res.get("content", ""))
            p_tokens = self._estimate_tokens(prompt_text)
            c_tokens = self._estimate_tokens(comp_text)

            self.tracer.record_llm_call(
                trace_ctx=trace_ctx,
                model=self.provider,
                intent="CHAT",
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                latency_sec=elapsed
            )

        return res
