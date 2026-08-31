from typing import Callable, Dict, Any, List

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, name: str, schema: Dict[str, Any], func: Callable):
        self._tools[name] = func
        self._schemas.append({
            "type": "function",
            "function": {
                "name": name,
                "description": schema.get("description", ""),
                "parameters": schema.get("parameters", {"type": "object", "properties": {}})
            }
        })

    def get_tool(self, name: str) -> Callable:
        return self._tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return self._schemas
