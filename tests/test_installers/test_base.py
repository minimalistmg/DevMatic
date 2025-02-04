import pytest
from pathlib import Path
from devmatic.core.base.installer import WindowsInstaller

class TestInstaller(WindowsInstaller):
    """Test installer implementation"""
    async def install(self) -> bool:
        return True
    
    async def uninstall(self) -> bool:
        return True
    
    async def update(self, version: str) -> bool:
        return True
    
    def is_installed(self) -> bool:
        return True

def test_installer_paths(temp_sdk_dir):
    """Test installer path handling"""
    installer = TestInstaller({})
    tool_path = installer.get_tool_path("test-tool")
    assert tool_path.parent.name == "tools"
    assert tool_path.name == "test-tool"

def test_installer_shortcut(temp_sdk_dir):
    """Test shortcut creation"""
    installer = TestInstaller({})
    result = installer.create_shortcut(
        target=temp_sdk_dir / "tools/test-tool/test.exe",
        name="Test Tool"
    )
    assert result == True 