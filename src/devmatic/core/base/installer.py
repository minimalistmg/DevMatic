from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from ...utils.windows import WindowsUtils

class WindowsInstaller(ABC):
    """Base class for Windows tool installers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.windows_utils = WindowsUtils()
        self.install_dirs = self.windows_utils.ensure_install_dirs()
        self.tool_dir = self.install_dirs['tools']
    
    @abstractmethod
    async def install(self) -> bool:
        """Install tool"""
        pass
    
    @abstractmethod
    async def uninstall(self) -> bool:
        """Uninstall tool"""
        pass
    
    @abstractmethod
    async def update(self, version: str) -> bool:
        """Update tool"""
        pass
    
    @abstractmethod
    def is_installed(self) -> bool:
        """Check if tool is installed"""
        pass
    
    def get_tool_path(self, tool_name: str) -> Path:
        """Get tool installation directory"""
        return self.tool_dir / tool_name
    
    def create_shortcut(self, target: Path, name: str) -> bool:
        """Create start menu shortcut"""
        return self.windows_utils.create_shortcut(target, name) 