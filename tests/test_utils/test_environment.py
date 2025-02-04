import pytest
import json
from pathlib import Path
from devmatic.core.environment import EnvironmentManager

def test_environment_load(temp_sdk_dir):
    """Test environment loading"""
    env = EnvironmentManager()
    env.load()
    assert "SDK_ROOT" in env.env_vars

def test_tool_paths(temp_sdk_dir):
    """Test tool path management"""
    env = EnvironmentManager()
    
    # Add test tool paths
    env.add_tool_paths("python", {
        "home": temp_sdk_dir / "tools/python",
        "bin": temp_sdk_dir / "tools/python/Scripts",
        "lib": temp_sdk_dir / "tools/python/Lib"
    })
    
    # Verify paths were added
    assert "PYTHON_HOME" in env.env_vars
    assert "PYTHON_BIN" in env.env_vars
    assert "PYTHON_LIB" in env.env_vars

def test_sdk_structure(temp_sdk_dir):
    """Test SDK directory structure"""
    assert temp_sdk_dir.exists(), "SDK root directory missing"
    assert (temp_sdk_dir / "tools").exists(), "Tools directory missing"
    assert (temp_sdk_dir / "temp").exists(), "Temp directory missing"
    assert (temp_sdk_dir / "sdk.env").exists(), "Environment file missing"
    assert (temp_sdk_dir / "sdk.json").exists(), "JSON config file missing"

def test_env_file_content(temp_sdk_dir):
    """Test environment file contents"""
    env_file = temp_sdk_dir / "sdk.env"
    env_content = env_file.read_text()
    assert "SDK_ROOT=" in env_content, "SDK_ROOT not found in env file"
    assert str(temp_sdk_dir.absolute()) in env_content, "Invalid SDK path in env file"

def test_sdk_json_config(temp_sdk_dir):
    """Test SDK JSON configuration"""
    json_file = temp_sdk_dir / "sdk.json"
    with open(json_file) as f:
        data = json.load(f)
    assert isinstance(data, list), "JSON file should contain a list" 