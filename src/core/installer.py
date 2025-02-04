from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict

class BaseInstaller(ABC):
    def __init__(self, install_dir: Path):
        self.install_dir = install_dir
        self.env_vars: Dict[str, str] = {}

    @abstractmethod
    async def install(self) -> bool:
        """Install the SDK"""
        pass

    @abstractmethod
    async def uninstall(self) -> bool:
        """Uninstall the SDK"""
        pass

    @abstractmethod
    async def update(self, version: str) -> bool:
        """Update the SDK to specified version"""
        pass

    def get_bin_path(self) -> Optional[Path]:
        """Get binary directory path"""
        bin_dir = self.install_dir / "bin"
        return bin_dir if bin_dir.exists() else None

    def update_environment(self) -> None:
        """Update environment variables"""
        if bin_path := self.get_bin_path():
            self.env_vars["PATH"] = str(bin_path) 