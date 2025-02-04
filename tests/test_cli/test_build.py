import pytest
from pathlib import Path
import shutil
from devmatic.cli.commands.build import build_executable, clean_build, copy_sdk_files

def test_clean_build(tmp_path):
    """Test cleaning build directories"""
    # Create dummy build dirs in temp
    build_dir = tmp_path / "build"
    dist_dir = tmp_path / "dist"
    
    for dir_path in [build_dir, dist_dir]:
        dir_path.mkdir()
        (dir_path / "test.txt").write_text("test")
    
    # Test cleaning
    clean_build()
    
    assert not build_dir.exists(), "Build directory should be removed"
    assert not dist_dir.exists(), "Dist directory should be removed"

def test_copy_sdk_files(tmp_path, temp_sdk_dir):
    """Test SDK file structure creation"""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    
    copy_sdk_files()
    
    sdk_dir = dist_dir / "SDK"
    assert sdk_dir.exists(), "SDK directory not created"
    assert (sdk_dir / "tools").exists(), "Tools directory not created"
    assert (sdk_dir / "temp").exists(), "Temp directory not created"
    assert (sdk_dir / "sdk.env").exists(), "Environment file not created"
    assert (sdk_dir / "sdk.json").exists(), "JSON config not created"

@pytest.mark.skipif(
    not Path("src/devmatic/cli/main.py").exists(),
    reason="Main script not found"
)
def test_build_executable(tmp_path):
    """Test executable build process"""
    # Temporarily change to tmp_path
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    
    try:
        result = build_executable()
        assert result is True, "Build should succeed"
        assert (tmp_path / "dist" / "devmatic.exe").exists(), "Executable not created"
    finally:
        # Restore original working directory
        os.chdir(original_cwd) 