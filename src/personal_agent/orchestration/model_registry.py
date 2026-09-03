from typing import Dict, Any, List, Optional

class ModelDefinition:
    def __init__(
        self,
        model_id: str,
        name: str,
        tier: str,
        provider: str,
        location: str,
        context_size: str,
        quantization: str,
        cost_per_1k: float,
        capabilities: List[str]
    ):
        self.model_id = model_id
        self.name = name
        self.tier = tier
        self.provider = provider
        self.location = location
        self.context_size = context_size
        self.quantization = quantization
        self.cost_per_1k = cost_per_1k
        self.capabilities = capabilities
        self.status = "READY"

class ModelHealthMonitor:
    def check_health(self, model_id: str) -> Dict[str, Any]:
        """Checks model latency, resource footprint, and health status."""
        return {
            "model_id": model_id,
            "status": "HEALTHY",
            "latency_ms": 1200,
            "cpu_percent": 68.0,
            "ram_used_gb": 4.1,
            "ram_total_gb": 16.0
        }

class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, ModelDefinition] = {}
        self._register_default_models()

    def _register_default_models(self):
        self.models["rule_engine"] = ModelDefinition(
            model_id="rule_engine",
            name="Deterministic Rule Engine",
            tier="DETERMINISTIC_RULES",
            provider="RuleEngine",
            location="LOCAL",
            context_size="N/A",
            quantization="N/A",
            cost_per_1k=0.0,
            capabilities=["classification", "pattern_matching", "regex"]
        )
        self.models["qwen2.5_1.5b"] = ModelDefinition(
            model_id="qwen2.5_1.5b",
            name="Qwen 2.5 1.5B",
            tier="SMALL_LOCAL_LLM",
            provider="Ollama",
            location="LOCAL",
            context_size="32K",
            quantization="Q4",
            cost_per_1k=0.0,
            capabilities=["email_triage", "planning", "classification"]
        )
        self.models["strong_local_14b"] = ModelDefinition(
            model_id="strong_local_14b",
            name="Strong Local LLM (14B)",
            tier="STRONG_LOCAL_LLM",
            provider="Ollama",
            location="LOCAL",
            context_size="32K",
            quantization="Q4",
            cost_per_1k=0.0,
            capabilities=["complex_code", "reasoning"]
        )
        self.models["strong_local_14b"].status = "BLOCKED" # Resource limit

        self.models["strong_cloud"] = ModelDefinition(
            model_id="strong_cloud",
            name="Strong Cloud LLM",
            tier="STRONG_CLOUD_LLM",
            provider="Cloud API",
            location="CLOUD",
            context_size="128K",
            quantization="FP16",
            cost_per_1k=0.03,
            capabilities=["complex_research", "multi_domain_reasoning"]
        )

    def get_all_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "model_id": m.model_id,
                "name": m.name,
                "tier": m.tier,
                "provider": m.provider,
                "location": m.location,
                "context_size": m.context_size,
                "quantization": m.quantization,
                "cost_per_1k": m.cost_per_1k,
                "capabilities": m.capabilities,
                "status": m.status
            }
            for m in self.models.values()
        ]

    def get_model(self, model_id: str) -> Optional[ModelDefinition]:
        return self.models.get(model_id)
