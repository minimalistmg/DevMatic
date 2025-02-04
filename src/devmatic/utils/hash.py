"""
Hash Utilities

This module provides functions for calculating and verifying file hashes
to ensure file integrity during downloads.
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional, Union, Literal

logger = logging.getLogger(__name__)

HashAlgorithm = Literal["md5", "sha1", "sha256", "sha512"]

def calculate_hash(
    file_path: Path,
    algorithm: HashAlgorithm = "sha256",
    chunk_size: int = 8192
) -> str:
    """Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
        chunk_size: Size of chunks to read
        
    Returns:
        str: Calculated hash in hexadecimal format
        
    Raises:
        ValueError: If algorithm is not supported
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if algorithm not in hashlib.algorithms_guaranteed:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

def verify_hash(
    file_path: Path,
    expected_hash: str,
    algorithm: HashAlgorithm = "sha256"
) -> bool:
    """Verify file hash matches expected value.
    
    Args:
        file_path: Path to the file
        expected_hash: Expected hash value
        algorithm: Hash algorithm to use
        
    Returns:
        bool: True if hash matches, False otherwise
    """
    try:
        actual_hash = calculate_hash(file_path, algorithm)
        matches = actual_hash.lower() == expected_hash.lower()
        
        if not matches:
            logger.error(
                f"Hash mismatch for {file_path.name}\n"
                f"Expected: {expected_hash}\n"
                f"Actual: {actual_hash}"
            )
        
        return matches
        
    except Exception as e:
        logger.error(f"Error verifying hash: {str(e)}")
        return False 