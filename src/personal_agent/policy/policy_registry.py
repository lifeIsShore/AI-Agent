import os
import glob
from typing import Dict, Any, List, Optional

class DeclarativePolicyRegistry:
    def __init__(self, policy_dir: str = "policies"):
        self.policy_dir = policy_dir
        self.rules: Dict[str, Dict[str, Any]] = {}
        self.load_policies()

    def load_policies(self):
        """Loads and parses declarative policy rules from YAML files."""
        if not os.path.exists(self.policy_dir):
            return

        yaml_files = glob.glob(os.path.join(self.policy_dir, "*.yaml"))
        for yf in yaml_files:
            try:
                with open(yf, "r", encoding="utf-8") as f:
                    content = f.read()
                    self._parse_yaml_content(content)
            except Exception as e:
                print(f"[PolicyRegistry] Error loading policy file '{yf}': {e}")

    def _parse_yaml_content(self, content: str):
        """Simple, robust YAML block parser for policy files."""
        blocks = content.split("- action:")
        for block in blocks[1:]:
            lines = block.strip().split("\n")
            action_name = lines[0].strip()
            
            rule = {
                "action": action_name,
                "permission_level": "MODIFY",
                "risk_level": "HIGH",
                "approval_required": True,
                "allowed_principals": ["USER"],
                "prohibited_targets": []
            }
            
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("permission_level:"):
                    rule["permission_level"] = line.split(":", 1)[1].strip()
                elif line.startswith("risk_level:"):
                    rule["risk_level"] = line.split(":", 1)[1].strip()
                elif line.startswith("approval_required:"):
                    rule["approval_required"] = line.split(":", 1)[1].strip().lower() == "true"

            self.rules[action_name] = rule

    def get_rule(self, action: str) -> Optional[Dict[str, Any]]:
        """Retrieves compiled declarative policy rule for an action."""
        return self.rules.get(action)
