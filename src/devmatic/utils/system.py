import platform
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict

class SystemUtils:
    @staticmethod
    def get_os() -> str:
        """Get operating system name"""
        return platform.system().lower()

    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows"""
        return platform.system().lower() == "windows"

    @staticmethod
    def get_home_dir() -> Path:
        """Get user's home directory"""
        return Path.home()

    @staticmethod
    def get_program_files() -> Path:
        """Get Program Files directory on Windows"""
        if platform.system().lower() == "windows":
            return Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        return Path("/usr/local")

    @staticmethod
    def run_command(
        command: list,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None
    ) -> tuple[int, str, str]:
        """Run system command and return result"""
        try:
            process = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )
            return process.returncode, process.stdout, process.stderr
        except Exception as e:
            return 1, "", str(e) 