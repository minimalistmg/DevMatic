"""
Download Utilities

This module provides functions for downloading files with progress tracking
and error handling.
"""

import aiohttp
import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable
from tqdm import tqdm

logger = logging.getLogger(__name__)

async def download_file(url: str, target_path: Path, chunk_size: int = 8192) -> bool:
    """Download a file from URL to target path.
    
    Args:
        url: The URL to download from
        target_path: Path where the file should be saved
        chunk_size: Size of chunks to download
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to download {url}: {response.status}")
                    return False
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        
        return True
    
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return False

async def download_with_progress(
    url: str,
    target_path: Path,
    desc: Optional[str] = None,
    chunk_size: int = 8192
) -> bool:
    """Download a file with progress bar.
    
    Args:
        url: The URL to download from
        target_path: Path where the file should be saved
        desc: Description for the progress bar
        chunk_size: Size of chunks to download
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to download {url}: {response.status}")
                    return False
                
                # Get file size for progress bar
                total = int(response.headers.get('content-length', 0))
                
                # Create progress bar
                desc = desc or f"Downloading {target_path.name}"
                progress = tqdm(
                    total=total,
                    desc=desc,
                    unit='iB',
                    unit_scale=True
                )
                
                # Download with progress
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        progress.update(len(chunk))
                
                progress.close()
                return True
    
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        if 'progress' in locals():
            progress.close()
        return False 