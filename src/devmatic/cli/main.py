"""
DevMatic CLI

Main CLI functionality for DevMatic SDK management.
"""

import json
import typer
import urllib.request
from pathlib import Path
import os
import sys
import time
import subprocess
import tarfile
import zipfile
import ctypes
import hashlib
import asyncio
import aiohttp
import shutil
import io
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Rich imports
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.status import Status
from rich import box

from ..utils.format import format_size, format_time
from ..utils.download import download_file
from ..utils.sdk import (
    ensure_download_dir,
    fetch_sdk_data_with_status,
    show_sdk_menu,
    install_sdk,
    update_env_file,
    remove_sdk_version
)

app = typer.Typer()
console = Console()

def interactive():
    """Interactive SDK installer"""

    session_start = time.time()
    total_size = 0
    installed_count = 0
    
    apps_file_path = Path(__file__).parent / 'apps/apps.json' #fetch_sdk_data_with_status()
    with open(apps_file_path, 'r') as apps_file:
        apps_data = json.load(apps_file)
    console.print("[blue]Loaded applications data:[/blue]")
    for app in apps_data:
        console.print(f"[green]Name:[/green] {app['name']}")
        console.print(f"[green]Description:[/green] {app['description']}")
        console.print(f"[green]GitHub Repo:[/green] {app['github_repo_link']}")
        console.print(f"[green]Platform:[/green] {', '.join(app['platform'])}")
        console.print("-----")
    
    ensure_download_dir()
    
    actions = show_sdk_menu(apps_data)
    
    if actions:
        for action, name, version, local_version in actions:
            if action == "remove":
                try:
                    # Remove installation directory
                    install_dir = DOWNLOAD_DIR / name
                    if install_dir.exists():
                        import shutil
                        shutil.rmtree(install_dir)
                    
                    # Remove from version tracking
                    remove_sdk_version(name)
                    update_env_file()
                    console.print(f"[green]Successfully removed {name} v{version}[/green]")
                except Exception as e:
                    console.print(f"[red]Failed to remove {name}: {e}[/red]")
            else:
                # Handle install/upgrade
                sdk = next((s for s in sdk_data if s["name"] == name), None)
                if sdk:
                    filename = Path(sdk["url"]).name
                    destination = DOWNLOAD_DIR / filename
                    
                    # Get file hash if available
                    file_hash = sdk.get("hash")
                    
                    if download_file(sdk["url"], destination, sdk["name"], file_hash):
                        success, size, install_time = install_sdk(name, destination, version)
                        if success:
                            action_text = "installed" if action == "install" else "upgraded"
                            console.print(f"[green]Successfully {action_text} {name} to v{version}[/green] [dim](took {format_time(install_time)})[/dim]")
                            total_size += size
                            installed_count += 1
                        else:
                            console.print(f"[red]Failed to {action} {name}[/red]")
                    else:
                        console.print(f"[red]Failed to download {name}[/red]")
        
        # Show session summary
        session_time = time.time() - session_start
        if installed_count > 0:
            console.print("\n[bold cyan]Session Summary:[/bold cyan]")
            console.print("[dim]" + "\n".join([
                f"Total packages: {installed_count}",
                f"Total size: {format_size(total_size)}",
                f"Time elapsed: {format_time(session_time)}"
            ]) + "[/dim]")

def cli():
    """Main CLI function"""
    interactive()

if __name__ == "__main__":
    cli()
