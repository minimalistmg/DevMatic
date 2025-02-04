import pytest
from pathlib import Path
import shutil
import os
import sys

# Add src to Python path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture
def temp_sdk_dir(tmp_path):
    """Create a temporary SDK directory"""
    sdk_dir = tmp_path / "SDK"
    sdk_dir.mkdir()
    (sdk_dir / "tools").mkdir()
    (sdk_dir / "temp").mkdir()
    
    # Create empty env file
    with open(sdk_dir / "sdk.env", "w") as f:
        f.write("# DevMatic SDK Environment Variables\n")
        f.write("SDK_ROOT=" + str(sdk_dir) + "\n")
    
    yield sdk_dir
    
    # Cleanup
    if sdk_dir.exists():
        shutil.rmtree(sdk_dir)

@pytest.fixture
def mock_windows_paths(monkeypatch):
    """Mock Windows-specific paths"""
    def mock_get_install_root():
        return Path("C:/DevMatic/SDK")
    
    from devmatic.utils.windows import WindowsUtils
    monkeypatch.setattr(WindowsUtils, "get_install_root", mock_get_install_root) 