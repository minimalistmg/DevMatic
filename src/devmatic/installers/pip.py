import os
import subprocess
import platform
import json
from pathlib import Path
from rich.console import Console
import time
import shutil
import pkg_resources
import sys

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

def find_python():
    """Find Python executables using sdk.env"""
    env_vars = load_sdk_env()
    python_home = env_vars.get('PYTHON_HOME')
    
    if not python_home:
        console.print("[red]Python path not found in sdk.env[/red]")
        return None
        
    python_path = Path(python_home)
    if platform.system() == "Windows":
        return {
            'python': python_path / "python.exe",
            'pip': python_path / "Scripts" / "pip.exe"
        }
    else:
        return {
            'python': python_path / "bin" / "python",
            'pip': python_path / "bin" / "pip"
        }

def get_installed_packages():
    """Get list of installed Python packages"""
    try:
        python_bins = find_python()
        if not python_bins:
            return {}
            
        result = subprocess.run(
            [str(python_bins['pip']), 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        packages = json.loads(result.stdout)
        return {pkg['name'].lower(): pkg['version'] for pkg in packages}
        
    except Exception as e:
        console.print(f"[red]Error getting installed packages: {str(e)}[/red]")
        return {}

def install_pip_package(package_name, version=None, upgrade=False):
    """Install a Python package using pip"""
    try:
        python_bins = find_python()
        if not python_bins:
            return False
            
        # Check if already installed
        installed = get_installed_packages()
        package_lower = package_name.lower()
        
        if package_lower in installed:
            current_version = installed[package_lower]
            if version and current_version != version:
                console.print(f"[yellow]Updating {package_name} from {current_version} to {version}[/yellow]")
            elif not upgrade:
                console.print(f"[green]✓ Package already installed: {package_name}@{current_version}[/green]")
                return True
            else:
                console.print(f"[yellow]Checking for updates: {package_name}[/yellow]")
        
        # Prepare installation command
        cmd = [str(python_bins['pip']), 'install']
        
        if upgrade:
            cmd.append('--upgrade')
            
        # Add version if specified
        if version:
            cmd.append(f"{package_name}=={version}")
        else:
            cmd.append(package_name)
            
        console.print(f"Installing Python package: {package_name}")
        
        # Run installation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Get installed version
            pkg_resources.working_set.by_key = {}  # Clear cache
            dist = pkg_resources.get_distribution(package_name)
            console.print(f"[green]✓ Successfully installed {package_name}@{dist.version}[/green]")
            return True
        else:
            console.print(f"[red]Error installing package: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error installing package: {str(e)}[/red]")
        return False

def install_pip_packages(package_list, upgrade=False):
    """Install multiple Python packages"""
    success_count = 0
    failed = []
    
    for pkg in package_list:
        # Handle version specification
        if '==' in pkg:
            name, version = pkg.split('==', 1)
            if install_pip_package(name, version, upgrade):
                success_count += 1
            else:
                failed.append(pkg)
        else:
            if install_pip_package(pkg, upgrade=upgrade):
                success_count += 1
            else:
                failed.append(pkg)
            
    console.print("\n[bold]Package Installation Summary:[/bold]")
    console.print(f"[green]✓ Successfully installed: {success_count}[/green]")
    if failed:
        console.print(f"[red]✗ Failed to install: {len(failed)}[/red]")
        console.print("[red]Failed packages:[/red]")
        for pkg in failed:
            console.print(f"  - {pkg}")
            
    return len(failed) == 0

def create_virtual_env(env_name, packages=None):
    """Create a virtual environment and install packages"""
    try:
        python_bins = find_python()
        if not python_bins:
            return False
            
        venv_path = Path(env_name)
        
        # Create virtual environment
        console.print(f"Creating virtual environment: {env_name}")
        result = subprocess.run(
            [str(python_bins['python']), '-m', 'venv', str(venv_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"[red]Error creating virtual environment: {result.stderr}[/red]")
            return False
            
        # Get virtual environment pip
        if platform.system() == "Windows":
            venv_pip = venv_path / "Scripts" / "pip.exe"
        else:
            venv_pip = venv_path / "bin" / "pip"
            
        # Install packages if specified
        if packages:
            console.print("Installing packages in virtual environment...")
            for pkg in packages:
                result = subprocess.run(
                    [str(venv_pip), 'install', pkg],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    console.print(f"[green]✓ Installed {pkg}[/green]")
                else:
                    console.print(f"[red]Failed to install {pkg}: {result.stderr}[/red]")
                    
        console.print(f"[green]✓ Virtual environment created: {env_name}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error creating virtual environment: {str(e)}[/red]")
        return False

# Example usage:
if __name__ == "__main__":
    # Install single package
    install_pip_package("requests")
    
    # Install multiple packages with versions
    packages = [
        "requests==2.31.0",
        "flask",
        "pandas==2.1.0"
    ]
    install_pip_packages(packages, upgrade=True)
    
    # Create virtual environment with packages
    create_virtual_env(
        "myenv",
        packages=[
            "flask",
            "requests",
            "pandas"
        ]
    ) 