import hashlib
from pathlib import Path
from typing import Optional

class HashUtils:
    @staticmethod
    def calculate_sha256(file_path: Path) -> Optional[str]:
        """Calculate SHA256 hash of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return None

    @staticmethod
    def verify_checksum(file_path: Path, expected_hash: str) -> bool:
        """Verify file checksum"""
        actual_hash = HashUtils.calculate_sha256(file_path)
        return actual_hash == expected_hash.lower() 