import os
import glob
import hashlib
import json
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.configs: Dict[str, Any] = {}
        self.policy_version = "2.0.0"
        self.config_hash = ""
        self.load_configurations()

    def load_configurations(self):
        """Loads configuration files and computes deterministic SHA256 config_hash."""
        if not os.path.exists(self.config_dir):
            self.config_hash = hashlib.sha256(b"default_config").hexdigest()[:16]
            return

        yaml_files = glob.glob(os.path.join(self.config_dir, "*.yaml"))
        combined_raw = []
        for yf in sorted(yaml_files):
            try:
                with open(yf, "r", encoding="utf-8") as f:
                    content = f.read()
                    name = os.path.basename(yf).replace(".yaml", "")
                    self.configs[name] = content
                    combined_raw.append(f"{name}:{content}")
            except Exception as e:
                print(f"[ConfigManager] Error reading '{yf}': {e}")

        raw_str = "|".join(combined_raw) if combined_raw else "empty_config"
        self.config_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:16]

    def get_config_hash(self) -> str:
        return self.config_hash

    def get_policy_version(self) -> str:
        return self.policy_version

    def get_version_binding(self) -> Dict[str, str]:
        return {
            "policy_version": self.policy_version,
            "config_hash": f"sha256:{self.config_hash}"
        }
