"""
DevMatic - Windows Development Environment Tool

A multi-purpose development environment installer tool for Windows that manages
installations in a single SDK folder without requiring admin privileges.
"""

__title__ = "DevMatic"
__version__ = "1.0.0"
__author__ = "DevMatic Team"
__license__ = "MIT"
__copyright__ = "Copyright 2024 DevMatic Team"

# Version info tuple for compatibility checks
VERSION_INFO = tuple(map(int, __version__.split('.')))

# SDK configuration
SDK_ROOT_ENV = "SDK_ROOT"
SDK_CONFIG_FILE = "sdk.json"
SDK_ENV_FILE = "sdk.env"

# Directory names
TOOLS_DIR = "tools"
TEMP_DIR = "temp"

# Package exports
__all__ = [
    "__version__",
    "VERSION_INFO",
    "SDK_ROOT_ENV",
    "SDK_CONFIG_FILE",
    "SDK_ENV_FILE",
    "TOOLS_DIR",
    "TEMP_DIR"
] 