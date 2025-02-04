import shutil
from pathlib import Path
from typing import List, Optional
import os

class FileUtils:
    @staticmethod
    def ensure_dir(path: Path) -> None:
        """Ensure directory exists"""
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def remove_dir(path: Path, ignore_errors: bool = False) -> bool:
        """Safely remove directory"""
        try:
            if path.exists():
                shutil.rmtree(path, ignore_errors=ignore_errors)
            return True
        except Exception:
            return False

    @staticmethod
    def copy_file(src: Path, dst: Path) -> bool:
        """Copy file with directory creation"""
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False

    @staticmethod
    def find_files(
        directory: Path,
        pattern: str = "*",
        recursive: bool = True
    ) -> List[Path]:
        """Find files matching pattern"""
        if recursive:
            return list(directory.rglob(pattern))
        return list(directory.glob(pattern)) 