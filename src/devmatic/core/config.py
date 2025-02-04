from pathlib import Path
import json
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: Path = Path("sdk.json")):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)

    def save_config(self) -> None:
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_sdk_version(self, sdk_name: str) -> str:
        """Get SDK version from config"""
        for sdk in self.config:
            if sdk["name"] == sdk_name:
                return sdk["version"]
        return None 