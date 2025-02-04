"""
DevMatic Utilities Package

This package provides utility functions and classes used throughout DevMatic,
including file downloads, hash verification, logging, and Windows-specific utilities.
"""

from .download import download_file, download_with_progress
from .hash import verify_hash, calculate_hash
from .logger import setup_logger
from .windows import WindowsUtils

__all__ = [
    "download_file",
    "download_with_progress",
    "verify_hash",
    "calculate_hash",
    "setup_logger",
    "WindowsUtils"
] 