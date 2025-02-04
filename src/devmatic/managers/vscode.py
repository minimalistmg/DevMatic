import os
import subprocess
import platform
import json
from pathlib import Path
from rich.console import Console

console = Console()

def load_sdk_env():
    """Load SDK environment variables from sdk.env"""
    env_file = Path("sdk.env")
    if not env_file.exists():
        console.print("[red]sdk.env file not found[/red]")
        return {}
        
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

def find_vscode():
    """Find VS Code executable using sdk.env or system paths"""
    # First try sdk.env
    env_vars = load_sdk_env()
    vscode_path = env_vars.get('VSCODE_HOME')
    if vscode_path:
        if platform.system() == "Windows":
            exe_path = Path(vscode_path) / "bin" / "code.cmd"
        else:
            exe_path = Path(vscode_path) / "bin" / "code"
        if exe_path.exists():
            return str(exe_path)
    
    # Fallback to system paths
    system = platform.system()
    if system == "Windows":
        paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Microsoft VS Code', 'bin', 'code.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'Microsoft VS Code', 'bin', 'code.cmd'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Microsoft VS Code', 'bin', 'code.cmd'),
        ]
    elif system == "Darwin":
        paths = [
            '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code',
            os.path.expanduser('~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code'),
        ]
    else:  # Linux
        paths = [
            '/usr/bin/code',
            '/usr/local/bin/code',
            os.path.expanduser('~/.local/bin/code'),
        ]

    for path in paths:
        if os.path.exists(path):
            return path
    return None

def get_installed_extensions():
    """Get list of installed VS Code extensions"""
    try:
        vscode = find_vscode()
        if not vscode:
            console.print("[red]VS Code not found. Please ensure it's installed and path is in sdk.env[/red]")
            return []
            
        result = subprocess.run(
            [vscode, '--list-extensions'],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout.strip().split('\n')
        
    except Exception as e:
        console.print(f"[red]Error getting installed extensions: {str(e)}[/red]")
        return []

def install_vscode_extension(extension_id):
    """Install a VS Code extension by ID"""
    try:
        vscode = find_vscode()
        if not vscode:
            console.print("[red]VS Code not found. Please ensure it's installed and path is in sdk.env[/red]")
            return False
            
        # Check if already installed
        installed = get_installed_extensions()
        if extension_id in installed:
            console.print(f"[green]✓ Extension already installed: {extension_id}[/green]")
            return True
            
        console.print(f"Installing VS Code extension: {extension_id}")
        
        # Install extension
        result = subprocess.run(
            [vscode, '--install-extension', extension_id],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print(f"[green]✓ Successfully installed extension: {extension_id}[/green]")
            return True
        else:
            console.print(f"[red]Error installing extension: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error installing extension: {str(e)}[/red]")
        return False

def install_vscode_extensions(extension_list):
    """Install multiple VS Code extensions"""
    success_count = 0
    failed = []
    
    for ext in extension_list:
        if install_vscode_extension(ext):
            success_count += 1
        else:
            failed.append(ext)
            
    console.print("\n[bold]Extension Installation Summary:[/bold]")
    console.print(f"[green]✓ Successfully installed: {success_count}[/green]")
    if failed:
        console.print(f"[red]✗ Failed to install: {len(failed)}[/red]")
        console.print("[red]Failed extensions:[/red]")
        for ext in failed:
            console.print(f"  - {ext}")
            
    return len(failed) == 0

# Example usage:
if __name__ == "__main__":
    # Install single extension
    install_vscode_extension("ms-python.python")
    
    # Install multiple extensions
    extensions = [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter"
    ]
    install_vscode_extensions(extensions) 