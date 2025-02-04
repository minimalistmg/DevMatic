import pytest
from pathlib import Path
from devmatic.utils.windows import WindowsUtils

def test_install_root():
    """Test SDK root path"""
    root = WindowsUtils.get_install_root()
    assert root.name == "SDK"
    assert isinstance(root, Path)

def test_directory_structure():
    """Test directory structure creation"""
    dirs = WindowsUtils.ensure_install_dirs()
    assert "root" in dirs
    assert "tools" in dirs
    assert "temp" in dirs
    assert all(isinstance(p, Path) for p in dirs.values()) 