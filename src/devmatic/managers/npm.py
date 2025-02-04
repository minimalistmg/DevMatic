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

def find_npm():
    """Find npm executable using sdk.env"""
    env_vars = load_sdk_env()
    nodejs_path = env_vars.get('NODEJS_HOME')
    
    if not nodejs_path:
        console.print("[red]NodeJS path not found in sdk.env[/red]")
        return None
        
    if platform.system() == "Windows":
        npm_path = Path(nodejs_path) / "npm.cmd"
    else:
        npm_path = Path(nodejs_path) / "npm"
        
    if npm_path.exists():
        return str(npm_path)
    else:
        console.print(f"[red]npm not found at {npm_path}[/red]")
        return None

def get_installed_packages(global_packages=True):
    """Get list of installed npm packages"""
    try:
        npm = find_npm()
        if not npm:
            return []
            
        cmd = [npm, 'list', '--json']
        if global_packages:
            cmd.append('-g')
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        packages = json.loads(result.stdout)
        return packages.get('dependencies', {})
        
    except Exception as e:
        console.print(f"[red]Error getting installed packages: {str(e)}[/red]")
        return {}

def install_npm_package(package_name, global_install=True, version=None):
    """Install an npm package"""
    try:
        npm = find_npm()
        if not npm:
            return False
            
        # Check if already installed
        installed = get_installed_packages(global_install)
        package_info = installed.get(package_name)
        
        if package_info:
            current_version = package_info.get('version')
            if version and current_version != version:
                console.print(f"[yellow]Updating {package_name} from {current_version} to {version}[/yellow]")
            else:
                console.print(f"[green]✓ Package already installed: {package_name}@{current_version}[/green]")
                return True
        
        # Prepare install command
        cmd = [npm, 'install']
        if global_install:
            cmd.append('-g')
            
        # Add version if specified
        if version:
            cmd.append(f"{package_name}@{version}")
        else:
            cmd.append(package_name)
            
        console.print(f"Installing npm package: {package_name}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            console.print(f"[green]✓ Successfully installed {package_name}[/green]")
            return True
        else:
            console.print(f"[red]Error installing package: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error installing package: {str(e)}[/red]")
        return False

def install_npm_packages(package_list, global_install=True):
    """Install multiple npm packages"""
    success_count = 0
    failed = []
    
    for package in package_list:
        # Handle version specification
        if '@' in package:
            name, version = package.split('@', 1)
            if install_npm_package(name, global_install, version):
                success_count += 1
            else:
                failed.append(package)
        else:
            if install_npm_package(package, global_install):
                success_count += 1
            else:
                failed.append(package)
            
    console.print("\n[bold]Package Installation Summary:[/bold]")
    console.print(f"[green]✓ Successfully installed: {success_count}[/green]")
    if failed:
        console.print(f"[red]✗ Failed to install: {len(failed)}[/red]")
        console.print("[red]Failed packages:[/red]")
        for pkg in failed:
            console.print(f"  - {pkg}")
            
    return len(failed) == 0

# Example usage:
if __name__ == "__main__":
    # Install single package
    install_npm_package("typescript")
    
    # Install multiple packages with versions
    packages = [
        "typescript@4.9.5",
        "prettier",
        "eslint@8.40.0"
    ]
    install_npm_packages(packages) 