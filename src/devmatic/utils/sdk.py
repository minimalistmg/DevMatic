"""
SDK Utilities for DevMatic

Provides functions for managing SDK data and directories.
"""

import json
import urllib.request
import time
from pathlib import Path
from rich.console import Console
from rich.status import Status

from ..core.config import SDK_URL, DOWNLOAD_DIR

console = Console()

def ensure_download_dir():
    """Ensure download directory exists"""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def fetch_sdk_data_with_status():
    """Fetch SDK data from remote JSON with status indicator"""
    with Status("[bold blue]Fetching available SDKs...", spinner="dots") as status:
        time.sleep(1)  # Sleep after showing "Fetching available SDKs"
        try:
            with urllib.request.urlopen(SDK_URL) as response:
                data = json.loads(response.read())
                status.update("[bold green]✓ SDK list fetched successfully!")
                time.sleep(1)
                return data
        except Exception as e:
            status.update(f"[bold red]✗ Error fetching SDK data: {e}")
            raise RuntimeError(f"Failed to fetch SDK data: {e}") 