"""
Windows Utilities

This module provides Windows-specific utility functions for DevMatic,
including path management and system operations.
"""

import os
import sys
import winreg
import logging
import ctypes
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WindowsUtils:
    """Utility class for Windows-specific operations."""
    
    @staticmethod
    def get_install_root() -> Path:
        """Get the SDK installation root directory.
        
        Returns:
            Path: SDK root directory
        """
        # Get user's AppData directory
        appdata = Path(os.getenv('APPDATA', ''))
        if not appdata:
            raise RuntimeError("Could not determine AppData directory")
        
        return appdata / "DevMatic" / "SDK"
    
    @staticmethod
    def ensure_install_dirs() -> Dict[str, Path]:
        """Ensure all required SDK directories exist.
        
        Returns:
            Dict[str, Path]: Dictionary of created directories
        """
        root = WindowsUtils.get_install_root()
        
        dirs = {
            "root": root,
            "tools": root / "tools",
            "temp": root / "temp"
        }
        
        for path in dirs.values():
            path.mkdir(parents=True, exist_ok=True)
        
        return dirs
    
    @staticmethod
    def get_user_path() -> List[str]:
        """Get the user's PATH environment variable.
        
        Returns:
            List[str]: List of paths in user's PATH
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_READ
            )
            path, _ = winreg.QueryValueEx(key, "Path")
            winreg.CloseKey(key)
            
            return [p for p in path.split(os.pathsep) if p]
        except Exception as e:
            logger.error(f"Failed to read user PATH: {str(e)}")
            return []
    
    @staticmethod
    def update_user_path(paths: List[str]):
        """Update the user's PATH environment variable.
        
        Args:
            paths: List of paths to set
        """
        try:
            path_str = os.pathsep.join(paths)
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Environment",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, path_str)
            winreg.CloseKey(key)
            
            # Notify Windows of environment change
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                5000,
                0
            )
            if result == 0:
                logger.warning("Failed to broadcast environment change")
                
        except Exception as e:
            logger.error(f"Failed to update user PATH: {str(e)}")
            raise
    
    @staticmethod
    def create_shortcut(
        target: Path,
        shortcut_path: Path,
        description: Optional[str] = None,
        arguments: Optional[str] = None,
        working_dir: Optional[Path] = None
    ) -> bool:
        """Create a Windows shortcut (.lnk file).
        
        Args:
            target: Path to the target file
            shortcut_path: Path where to create the shortcut
            description: Optional shortcut description
            arguments: Optional command line arguments
            working_dir: Optional working directory
            
        Returns:
            bool: True if shortcut was created successfully
        """
        try:
            import pythoncom
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(target)
            
            if description:
                shortcut.Description = description
            if arguments:
                shortcut.Arguments = arguments
            if working_dir:
                shortcut.WorkingDirectory = str(working_dir)
                
            shortcut.save()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create shortcut: {str(e)}")
            return False 