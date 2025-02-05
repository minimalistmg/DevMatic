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

# DevMatic imports
from utils.format import format_size, format_time
from utils.download import download_file
from utils.sdk import (
    ensure_directories_and_files,
    fetch_apps_data,
    fetch_sdk_data,
    show_sdk_menu,
    install_sdk,
    update_env_file,
    remove_sdk_version,
    DOWNLOAD_DIR,
    SDK_DIR
)

app = typer.Typer()
console = Console()

def interactive():
    """Interactive SDK installer"""
    try:
        session_start = time.time()
        total_size = 0
        installed_count = 0
        
        # Initialize environment
        with Status("[bold blue]Initializing DevMatic...", spinner="dots") as status:
            ensure_directories_and_files()
            status.update("[bold green]✓ Environment initialized")
            time.sleep(0.5)  # Small delay for visual feedback
        
        # Get apps data and show selection menu
        apps_data = fetch_apps_data()
        actions = show_sdk_menu(apps_data)
        if not actions:
            console.print("\n[yellow]No actions selected. Exiting...[/yellow]")
            return
        
        # Process selected actions
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[cyan]{task.completed}/{task.total}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Processing actions...", total=len(actions))
            
            for action, name, version, local_version in actions:
                if action == "remove":
                    try:
                        # Remove installation directory
                        install_dir = DOWNLOAD_DIR / name
                        if install_dir.exists():
                            shutil.rmtree(install_dir)
                            console.print(f"[green]✓ Removed installation directory for {name}[/green]")
                        
                        # Remove from version tracking and update environment
                        if remove_sdk_version(name) and update_env_file():
                            console.print(f"[green]Successfully removed {name} v{version}[/green]")
                        else:
                            console.print(f"[yellow]Warning: Partial removal of {name} - some components may remain[/yellow]")
                            
                    except Exception as e:
                        console.print(f"[red]Failed to remove {name}: {e}[/red]")
                        
                else:  # install or upgrade
                    try:
                        # Get SDK data
                        sdk_data = get_sdk_data()
                        sdk = next((s for s in sdk_data if s["name"] == name), None)
                        
                        if not sdk:
                            console.print(f"[red]Error: SDK data not found for {name}[/red]")
                            continue
                        
                        # Prepare download
                        filename = Path(sdk["url"]).name
                        destination = DOWNLOAD_DIR / filename
                        file_hash = sdk.get("hash")
                        
                        # Download SDK
                        console.print(f"\n[bold blue]Processing {name}...[/bold blue]")
                        if download_file(sdk["url"], destination, sdk["name"], file_hash):
                            # Install SDK
                            success, size, install_time = install_sdk(name, destination, version)
                            
                            if success:
                                action_text = "installed" if action == "install" else "upgraded"
                                console.print(f"[green]Successfully {action_text} {name} to v{version}[/green] [dim](took {format_time(install_time)})[/dim]")
                                total_size += size
                                installed_count += 1
                                
                                # Update environment after successful installation
                                if not update_env_file():
                                    console.print("[yellow]Warning: Failed to update environment variables[/yellow]")
                            else:
                                console.print(f"[red]Failed to {action} {name}[/red]")
                        else:
                            console.print(f"[red]Failed to download {name}[/red]")
                            
                    except Exception as e:
                        console.print(f"[red]Error processing {name}: {e}[/red]")
                        
                progress.advance(task)
                console.print()  # Add spacing between actions
        
        # Show session summary
        session_time = time.time() - session_start
        if installed_count > 0:
            console.print("\n[bold cyan]Session Summary:[/bold cyan]")
            summary = Table.grid(padding=1)
            summary.add_column(style="cyan")
            summary.add_column(style="green")
            summary.add_row("Total packages:", str(installed_count))
            summary.add_row("Total size:", format_size(total_size))
            summary.add_row("Time elapsed:", format_time(session_time))
            console.print(summary)
            
            console.print("\n[dim]Run [green]devmatic list[/dim] to see all installed SDKs[dim][/dim]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        console.print("[yellow]Please report this issue on GitHub[/yellow]")

def cli():
    """Main CLI function"""
    interactive()

if __name__ == "__main__":
    cli()
