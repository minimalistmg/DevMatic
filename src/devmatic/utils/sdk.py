"""
SDK utilities for DevMatic

Provides functions for managing SDK installations and metadata.
"""

from pathlib import Path
from rich.status import Status
import urllib.request

import os
import json
import time
import shutil
import subprocess
import ctypes
import zipfile
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.prompt import Confirm
from rich import box

from .format import format_size, format_time

ROOT_DIR = Path("C:/DevMatic")
DEVMATIC_DIR = ROOT_DIR / '.devmatic'
DOWNLOAD_DIR = DEVMATIC_DIR / 'downloads'
APPS_JSON_FILE = DEVMATIC_DIR / 'apps.json'
SDK_JSON_FILE = DEVMATIC_DIR / 'sdk.json'

console = Console()

def ensure_directories_and_files():
    """Ensure necessary directories and files exist"""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    APPS_JSON_FILE.touch(exist_ok=True)
    SDK_JSON_FILE.touch(exist_ok=True)

def fetch_apps_data():
    """Fetch Apps data from remote JSON with status indicator"""
    with Status("[bold blue]Fetching available Apps...", spinner="dots") as status:
        try:
            with urllib.request.urlopen("https://raw.githubusercontent.com/minimalistmg/DevMatic/refs/heads/main/src/devmatic/apps/apps.json") as response:
                data = json.loads(response.read())
                status.update("[bold green]✓ Apps list fetched successfully!")
                return data
        except Exception as e:
            status.update(f"[bold red]✗ Error fetching Apps data: {e}")
            raise RuntimeError(f"Failed to fetch Apps data: {e}")

def fetch_sdk_data():
    """Fetch SDK data from remote JSON with status indicator"""
    with Status("[bold blue]Fetching available SDKs...", spinner="dots") as status:
        try:
            with urllib.request.urlopen("https://raw.githubusercontent.com/minimalistmg/DevMatic/refs/heads/main/src/devmatic/apps/toolkit.json") as response:
                data = json.loads(response.read())
                status.update("[bold green]✓ SDK list fetched successfully!")
                return data
        except Exception as e:
            status.update(f"[bold red]✗ Error fetching SDK data: {e}")
            raise RuntimeError(f"Failed to fetch SDK data: {e}")

def get_local_sdk_versions():
    """Get versions of locally installed SDKs"""
    try:
        versions = {}
        # Check both json and actual directories
        if Path('sdk.json').exists():
            with open('sdk.json', 'r') as f:
                local_data = json.load(f)
                for sdk in local_data:
                    sdk_dir = DOWNLOAD_DIR / sdk['name']
                    if sdk_dir.exists() and any(sdk_dir.iterdir()):
                        versions[sdk['name']] = sdk['version']
                    else:
                        # Remove from json if directory doesn't exist
                        remove_sdk_version(sdk['name'])
        
        # Check for directories that exist but aren't in json
        for sdk_dir in DOWNLOAD_DIR.iterdir():
            if sdk_dir.is_dir() and sdk_dir.name not in versions:
                versions[sdk_dir.name] = "unknown"
        
        return versions
    except FileNotFoundError:
        # Check for existing directories even if json doesn't exist
        versions = {}
        if DOWNLOAD_DIR.exists():
            for sdk_dir in DOWNLOAD_DIR.iterdir():
                if sdk_dir.is_dir():
                    versions[sdk_dir.name] = "unknown"
        return versions

def show_sdk_menu(sdk_data):
    """Display interactive SDK menu"""
    margin = 2
    table_width = console.width - (margin * 2)
    
    # Get local versions with existence check
    local_versions = get_local_sdk_versions()
    remote_names = {sdk["name"] for sdk in sdk_data}
    
    # Only consider SDKs that actually exist
    obsolete_sdks = [name for name in local_versions.keys() 
                    if name not in remote_names 
                    and (DOWNLOAD_DIR / name).exists()]
    
    # Create table
    table = Table(
        show_header=True,
        title="[white not italic]SDK Manager[/white not italic]",
        width=table_width,
        show_edge=True,
        border_style="blue",
        header_style="bold cyan",
        box=box.ROUNDED
    )
    
    # Add columns
    id_width = 4
    name_width = 20
    version_width = 25  # Increased width for combined version/status
    desc_width = table_width - id_width - name_width - version_width - 8
    
    table.add_column("#", width=id_width, justify="center", style="cyan")
    table.add_column("Name", width=name_width, justify="left", style="bright_white", no_wrap=True)
    table.add_column("Version / Status", width=version_width, justify="left", style="yellow")
    table.add_column("Description", width=desc_width, justify="left", style="green", overflow="fold")
    
    # Track SDKs needing action
    needs_action = []
    
    # First add remote SDKs
    for idx, sdk in enumerate(sdk_data, 1):
        name = sdk["name"]
        new_version = sdk["version"]
        local_version = local_versions.get(name)
        
        if local_version:
            if local_version != new_version:
                # Show upgrade status
                version_status = f"[yellow]v{local_version}[/yellow] [dim]→[/dim] [bold yellow]v{new_version}[/bold yellow]"
                needs_action.append(("upgrade", name, new_version, local_version))
            else:
                # Show up-to-date status
                version_status = f"[green]v{local_version} (current)[/green]"
        else:
            # Show install status
            version_status = f"[green]v{new_version} (install)[/green]"
            needs_action.append(("install", name, new_version, None))
        
        table.add_row(
            f"[cyan]{idx}[/cyan]",
            f"[bright_white]{name}[/bright_white]",
            version_status,
            f"[green]{sdk['description']}[/green]"
        )
    
    # Then add local-only SDKs that need removal
    for name in obsolete_sdks:
        idx += 1
        version = local_versions[name]
        version_status = f"[red]v{version} (remove)[/red]"
        needs_action.append(("remove", name, version))
        
        table.add_row(
            f"[cyan]{idx}[/cyan]",
            f"[bright_white]{name}[/bright_white]",
            version_status,
            "[dim]Package no longer available in remote SDK list[/dim]"
        )
    
    # Show table
    console.print("\n")
    console.print(table, justify="center")
    
    # Show summary and ask for confirmation
    if needs_action:
        console.print("\n[bold]Available actions:[/bold]")
        for action, name, version, local_version in needs_action:
            if action == "install":
                console.print(f"[green]• Install {name} v{version}[/green]")
            elif action == "upgrade":
                console.print(f"[yellow]• Upgrade {name} from {local_version} to v{version}[/yellow]")
            elif action == "remove":
                console.print(f"[red]• Remove {name} v{version}[/red]")
        
        if Confirm.ask("\n[cyan]Would you like to proceed with selected actions?[/cyan]"):
            return needs_action
    else:
        console.print("\n[bold green]✨ All SDKs are up to date![/bold green]")
        console.print("[dim]Your development environment is ready to go[/dim]")
    
    return None

def organize_sdk_directory(sdk_name: str, install_dir: Path, extracted_dir: Path = None):
    """Organize SDK directory structure after extraction"""
    try:
        if not extracted_dir:
            extracted_dir = install_dir
            
        # Check directory contents
        contents = list(extracted_dir.iterdir())
        
        # Find the deepest directory containing actual SDK files
        def find_sdk_root(path):
            items = list(path.iterdir())
            if len(items) == 1 and items[0].is_dir():
                # Check if this single directory contains executables or important files
                subdir_items = list(items[0].iterdir())
                if any(item.suffix.lower() in ['.exe', '.dll', '.bat', '.cmd'] for item in subdir_items):
                    return items[0]
                # If not, go deeper
                return find_sdk_root(items[0])
            return path
        
        # Find the actual SDK root directory
        sdk_root = find_sdk_root(extracted_dir)
        
        # Move all contents to install directory
        for item in sdk_root.iterdir():
            target = install_dir / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(target))
        
        # Verify the installation
        installed_files = list(install_dir.iterdir())
        if not installed_files:
            console.print(f"[yellow]Warning: No files found in {install_dir}[/yellow]")
            return False
            
        # Log the directory structure
        console.print("[dim]Directory structure:[/dim]")
        console.print(f"[dim]SDK/{sdk_name}/[/dim]")
        for item in installed_files[:5]:  # Show first 5 items
            console.print(f"[dim]  ├─ {item.name}[/dim]")
        if len(installed_files) > 5:
            console.print(f"[dim]  └─ ... ({len(installed_files) - 5} more files)[/dim]")
            
        return True
        
    except Exception as e:
        console.print(f"[yellow]Warning: Error organizing SDK directory: {e}[/yellow]")
        return False

def install_sdk(sdk_name: str, file_path: Path, version: str):
    """Install SDK from downloaded file"""
    try:
        install_dir = DOWNLOAD_DIR / sdk_name
        start_time = time.time()
        file_size = file_path.stat().st_size
        
        # Clean up existing installation
        if install_dir.exists():
            try:
                shutil.rmtree(install_dir)
                time.sleep(1)
                console.print(f"[yellow]Removed existing directory: {install_dir.name}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not remove existing directory: {e}[/yellow]")
                return False, 0, 0
        
        install_dir.mkdir(parents=True, exist_ok=True)
        file_ext = file_path.suffix.lower()
        
        # Handle different file types
        if file_ext == '.msi':
            try:
                # Prepare command to extract MSI file
                print(f"Extracting MSI file to {install_dir}")
                print(f"File path: {file_path}")
                extract_cmd = f'msiexec /a "{file_path}" /qb TARGETDIR="{install_dir}"'
                # Run the extraction command
                result = subprocess.run(
                    extract_cmd,
                    shell=True,
                    check=True
                )
                
                # Create a startup script to run GitHub Desktop with local data storage
                BATCH_FILE = os.path.join(install_dir, "start-github-desktop.bat")
                with open(BATCH_FILE, "w") as f:
                    f.write(f'@echo off\n')
                    f.write(f'set "APPDATA={install_dir}"\n')
                    f.write(f'start "" "{install_dir}\\GitHubDesktop.exe"\n')
                
                # Wait for installation to complete
                time.sleep(5)  # Give installer time to finish
                
                # Verify installation
                if not install_dir.exists() or not any(install_dir.iterdir()):
                    console.print("[bold red]✗ Installation verification failed[/bold red]")
                    return False, 0, 0
                    
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]✗ MSI installation failed: {e.stderr}[/bold red]")
                return False, 0, 0
            except Exception as e:
                console.print(f"[bold red]✗ Installation error: {e}[/bold red]")
                return False, 0, 0
                
        elif file_ext == '.exe':
            # Run installer silently with user-level installation
            try:
                # Prepare installation arguments
                install_args = [
                    'runas',  # Run as administrator
                    str(file_path),
                    '/VERYSILENT',  # Silent installation
                    '/CURRENTUSER',  # Install for current user
                    '/NORESTART',    # Don't restart
                    f'/DIR={install_dir}'  # Custom install directory
                ]
                
                # Use ShellExecute to handle UAC elevation
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,           # Parent window handle
                    'runas',        # Operation
                    str(file_path), # File to execute
                    ' '.join(install_args[2:]),  # Parameters
                    str(DOWNLOAD_DIR),  # Working directory
                    1               # Show normal window
                )
                
                if result <= 32:  # ShellExecute returns error if <= 32
                    console.print(f"[bold red]✗ Installation failed: Error code {result}[/bold red]")
                    return False, 0, 0
                
                # Wait for installation to complete
                time.sleep(5)  # Give installer time to finish
                
                # Verify installation
                if not install_dir.exists() or not any(install_dir.iterdir()):
                    console.print("[bold red]✗ Installation verification failed[/bold red]")
                    return False, 0, 0
                    
            except Exception as e:
                console.print(f"[bold red]✗ Installation error: {e}[/bold red]")
                return False, 0, 0
                
        elif file_ext in ['.zip', '.gz', '.tgz', '.tar']:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description:<20}"),
                TextColumn("[bold green]{task.percentage:>3.1f}% [yellow]({task.elapsed:.1f}s)[/yellow]"),
                BarColumn(bar_width=20),
                TextColumn("[bold cyan]{task.completed}/{task.total}"),
                console=console,
                transient=True,
                expand=False,
            ) as progress:
                if file_ext == '.zip':
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # Get file list and total size for progress
                        files = zip_ref.namelist()
                        total_size = sum(zip_ref.getinfo(file).file_size for file in files)
                        task = progress.add_task(
                            f"[cyan]Extracting {sdk_name}...", 
                            total=total_size
                        )
                        
                        # Find root directory if it exists
                        root_dir = None
                        if files:
                            first_path = files[0].split('/')
                            if len(first_path) > 1 and all(f.startswith(f"{first_path[0]}/") for f in files):
                                root_dir = first_path[0]
                        
                        # Extract files with progress
                        extracted_size = 0
                        for file in files:
                            if file.startswith(('/', '..')):
                                console.print(f"[yellow]Skipping unsafe path: {file}[/yellow]")
                                continue
                                
                            try:
                                if root_dir:
                                    if file.startswith(f"{root_dir}/"):
                                        # Remove root directory from path
                                        target_path = file[len(root_dir)+1:]
                                        if target_path:  # Skip the root directory itself
                                            target = install_dir / target_path
                                            # Create parent directory if it doesn't exist
                                            target.parent.mkdir(parents=True, exist_ok=True)
                                            # Extract file only if it's not a directory
                                            if not file.endswith('/'):
                                                with zip_ref.open(file) as source, open(target, 'wb') as target_file:
                                                    target_file.write(source.read())
                                                extracted_size += zip_ref.getinfo(file).file_size
                                                progress.update(task, completed=extracted_size)
                                else:
                                    # No root directory, extract directly
                                    target = install_dir / file
                                    # Create parent directory if it doesn't exist
                                    target.parent.mkdir(parents=True, exist_ok=True)
                                    # Extract file only if it's not a directory
                                    if not file.endswith('/'):
                                        with zip_ref.open(file) as source, open(target, 'wb') as target_file:
                                            target_file.write(source.read())
                                        extracted_size += zip_ref.getinfo(file).file_size
                                        progress.update(task, completed=extracted_size)
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not extract {file}: {e}[/yellow]")
                                continue
            
            if start_time:
                extract_time = time.time() - start_time
                file_size = file_path.stat().st_size
                console.print(f"[bold green]✓ {sdk_name} installed successfully![/bold green] [dim]({format_size(file_size)} in {format_time(extract_time)})[/dim]")
        
        # Clean up downloaded file
        try:
            file_path.unlink()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not remove downloaded file: {e}[/yellow]")
        
        # Update version and environment file
        update_local_sdk_version(sdk_name, version)
        update_env_file()
        
        # Calculate total installation time
        install_time = time.time() - start_time
        return True, file_size, install_time  # Return success, size, and time
            
    except Exception as e:
        console.print(f"[bold red]✗ Installation error: {e}[/bold red]")
        if file_path.exists():
            file_path.unlink()
        return False, 0, 0

def update_local_sdk_version(sdk_name: str, version: str, previous_version: str = None):
    """Update local SDK version record with metadata"""
    try:
        sdk_file = Path('sdk.json')
        data = []
        
        if sdk_file.exists():
            with open(sdk_file, 'r') as f:
                data = json.load(f)
        
        # Get current timestamp
        current_time = datetime.now().isoformat()
        
        # Update or add SDK version with metadata
        sdk_entry = next((item for item in data if item['name'] == sdk_name), None)
        if sdk_entry:
            # Store version history
            sdk_entry.update({
                'previous_version': sdk_entry['version'],
                'version': version,
                'last_updated': current_time,
                'update_count': sdk_entry.get('update_count', 0) + 1,
                'version_history': sdk_entry.get('version_history', []) + [{
                    'from_version': sdk_entry['version'],
                    'to_version': version,
                    'update_date': current_time
                }]
            })
        else:
            data.append({
                'name': sdk_name,
                'version': version,
                'previous_version': previous_version,
                'installed_date': current_time,
                'last_updated': current_time,
                'update_count': 0,
                'status': 'active',
                'version_history': []
            })
            
        # Write updated data with pretty formatting
        with open(sdk_file, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
            
    except Exception as e:
        console.print(f"[bold red]✗ Error updating SDK version: {e}[/bold red]")

def remove_sdk_version(sdk_name: str):
    """Remove SDK from version tracking"""
    try:
        sdk_file = Path('sdk.json')
        if not sdk_file.exists():
            return
            
        with open(sdk_file, 'r') as f:
            data = json.load(f)
        
        # Remove SDK from data
        data = [sdk for sdk in data if sdk['name'] != sdk_name]
        
        # Write updated data
        with open(sdk_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        console.print(f"[bold red]✗ Error removing SDK version: {e}[/bold red]")

def update_env_file():
    """Update .env file with SDK paths"""
    try:
        env_file = APP_DIR / "sdk.env"
        sdk_dir = DOWNLOAD_DIR.resolve()  # Get absolute path
        
        # Prepare environment variables
        env_content = [
            "# DevMatic SDK Environment Variables",
            "# This file is auto-generated - DO NOT EDIT MANUALLY",
            f"SDK_ROOT={sdk_dir}",
            ""  # Empty line at end
        ]
        
        # Add paths for each installed SDK
        if Path('sdk.json').exists():
            with open('sdk.json', 'r') as f:
                installed_sdks = json.load(f)
                
            for sdk in installed_sdks:
                name = sdk['name'].upper().replace(' ', '_')
                path = sdk_dir / sdk['name']
                if path.exists():
                    env_content.append(f"{name}_HOME={path}")
                    
                    # Add bin directory to PATH if it exists
                    bin_dir = path / "bin"
                    if bin_dir.exists():
                        env_content.append(f"{name}_BIN={bin_dir}")
                    
                    # Add lib directory to PATH if it exists
                    lib_dir = path / "lib"
                    if lib_dir.exists():
                        env_content.append(f"{name}_LIB={lib_dir}")
                    
                    env_content.append("")  # Empty line between SDKs
        
        # Write the file
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content))
            
        console.print("[green]✓ Updated SDK environment variables[/green]")
        
    except Exception as e:
        console.print(f"[bold red]✗ Error updating environment variables: {e}[/bold red]") 