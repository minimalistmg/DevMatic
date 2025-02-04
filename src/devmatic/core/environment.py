from pathlib import Path
from typing import Dict, Optional
import os
from ..utils.windows import WindowsUtils

class EnvironmentManager:
    def __init__(self):
        self.install_dirs = WindowsUtils.ensure_install_dirs()
        self.env_file = self.install_dirs['root'] / 'sdk.env'
        self.env_vars: Dict[str, str] = {}

    def load(self) -> None:
        """Load environment variables"""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.env_vars[key.strip()] = value.strip()

    def save(self) -> None:
        """Save environment variables"""
        with open(self.env_file, 'w') as f:
            f.write("# DevMatic SDK Environment Variables\n")
            f.write("# This file is auto-generated - DO NOT EDIT MANUALLY\n\n")
            f.write(f"SDK_ROOT={self.install_dirs['root']}\n\n")
            
            # Group variables by tool
            tool_vars = {}
            for key, value in sorted(self.env_vars.items()):
                tool_name = key.split('_')[0]
                if tool_name not in tool_vars:
                    tool_vars[tool_name] = []
                tool_vars[tool_name].append((key, value))
            
            # Write variables grouped by tool
            for tool_name, vars in tool_vars.items():
                for key, value in vars:
                    f.write(f"{key}={value}\n")
                f.write("\n")  # Empty line between tools

    def add_tool_paths(self, tool_name: str, paths: Dict[str, Path]) -> None:
        """Add tool paths to environment file"""
        tool_upper = tool_name.upper().replace(' ', '_')
        
        # Add main tool path
        if 'home' in paths:
            self.env_vars[f"{tool_upper}_HOME"] = str(paths['home'])
        
        # Add bin directory if it exists
        if 'bin' in paths:
            self.env_vars[f"{tool_upper}_BIN"] = str(paths['bin'])
        
        # Add lib directory if it exists
        if 'lib' in paths:
            self.env_vars[f"{tool_upper}_LIB"] = str(paths['lib'])
        
        self.save()

    def get_tool_path(self, tool_name: str) -> Optional[Path]:
        """Get tool installation path"""
        tool_dir = self.install_dirs['tools'] / tool_name
        return tool_dir if tool_dir.exists() else None 