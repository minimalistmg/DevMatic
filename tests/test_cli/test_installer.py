import pytest
from pathlib import Path
import shutil
import winreg
from devmatic.cli.commands.installer import InstallerCreator

def test_installer_version():
    """Test version extraction"""
    creator = InstallerCreator()
    version = creator._get_version()
    assert version.count('.') == 2, "Version should be in x.y.z format"
    assert all(part.isdigit() for part in version.split('.')), "Version parts should be numeric"

def test_installer_directories(tmp_path):
    """Test installer directory creation"""
    creator = InstallerCreator()
    creator.dist_dir = tmp_path / "dist"
    creator.installer_dir = creator.dist_dir / "installer"
    
    creator.create_installer_dirs()
    
    assert creator.installer_dir.exists(), "Installer directory not created"
    assert (creator.installer_dir / "bin").exists(), "Bin directory not created"
    assert (creator.installer_dir / "SDK").exists(), "SDK directory not created"

def test_installer_file_copy(tmp_path, temp_sdk_dir):
    """Test installer file copying"""
    # Setup test environment
    creator = InstallerCreator()
    creator.dist_dir = tmp_path / "dist"
    creator.installer_dir = creator.dist_dir / "installer"
    creator.create_installer_dirs()
    
    # Create dummy executable
    creator.dist_dir.mkdir(exist_ok=True)
    (creator.dist_dir / "devmatic.exe").write_bytes(b"dummy executable")
    
    creator.copy_files()
    
    assert (creator.installer_dir / "bin" / "devmatic.exe").exists(), "Executable not copied"
    assert (creator.installer_dir / "SDK").exists(), "SDK directory not copied"

def test_inno_script_creation(tmp_path):
    """Test Inno Setup script creation"""
    creator = InstallerCreator()
    creator.installer_dir = tmp_path / "installer"
    creator.installer_dir.mkdir(parents=True)
    
    creator.create_inno_script()
    
    script_file = creator.installer_dir / "setup.iss"
    assert script_file.exists(), "Inno Setup script not created"
    
    content = script_file.read_text()
    assert "#define MyAppName" in content, "App name not defined in script"
    assert "Source: \"bin\\" in content, "Binary source not defined in script"
    assert "Source: \"SDK\\" in content, "SDK source not defined in script"

@pytest.mark.skipif(
    not Path("resources/devmatic.ico").exists(),
    reason="Resource files not found"
)
def test_resource_files():
    """Test required resource files"""
    resources = [
        'devmatic.ico',
        'devmatic.manifest',
        'license.rtf',
        'banner.bmp',
        'dialog.bmp'
    ]
    
    for resource in resources:
        assert Path(f'resources/{resource}').exists(), f"Missing resource file: {resource}" 