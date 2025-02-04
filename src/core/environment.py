from pathlib import Path
from typing import Dict, Optional
import os
import platform

class EnvironmentManager:
    def __init__(self, env_file: Path = Path("sdk.env")):
        self.env_file = env_file
        self.env_vars: Dict[str, str] = {}

    def load_environment(self) -> None:
        """Load environment variables from file"""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.env_vars[key.strip()] = value.strip()

    def save_environment(self) -> None:
        """Save environment variables to file"""
        with open(self.env_file, 'w') as f:
            f.write("# DevMatic SDK Environment Variables\n")
            f.write("# This file is auto-generated - DO NOT EDIT MANUALLY\n\n")
            
            for key, value in sorted(self.env_vars.items()):
                f.write(f"{key}={value}\n")

    def get_sdk_path(self, sdk_name: str) -> Optional[Path]:
        """Get SDK installation path"""
        key = f"{sdk_name.upper()}_HOME"
        path = self.env_vars.get(key)
        return Path(path) if path else None 