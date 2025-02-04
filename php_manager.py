import os
import subprocess
import platform
import json
from pathlib import Path
from rich.console import Console
import time
import shutil

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

def find_php():
    """Find PHP executables using sdk.env"""
    env_vars = load_sdk_env()
    php_home = env_vars.get('PHP_HOME')
    
    if not php_home:
        console.print("[red]PHP path not found in sdk.env[/red]")
        return None
        
    php_path = Path(php_home)
    if platform.system() == "Windows":
        return {
            'php': php_path / "php.exe",
            'pecl': php_path / "pecl.bat",
            'php-config': php_path / "php-config.bat"
        }
    else:
        return {
            'php': php_path / "bin" / "php",
            'pecl': php_path / "bin" / "pecl",
            'php-config': php_path / "bin" / "php-config"
        }

def get_installed_extensions():
    """Get list of installed PHP extensions"""
    try:
        php_bins = find_php()
        if not php_bins:
            return []
            
        result = subprocess.run(
            [str(php_bins['php']), '-m'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse extension list
        extensions = []
        in_extension_list = False
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line == '[PHP Modules]':
                in_extension_list = True
                continue
            elif line == '[Zend Modules]':
                break
            elif in_extension_list and line:
                extensions.append(line)
                
        return extensions
        
    except Exception as e:
        console.print(f"[red]Error getting installed extensions: {str(e)}[/red]")
        return []

def configure_pecl():
    """Configure PECL for extension installation"""
    try:
        php_bins = find_php()
        if not php_bins:
            return False
            
        env_vars = load_sdk_env()
        php_home = env_vars.get('PHP_HOME')
        
        # Create pecl configuration
        pecl_config = f"""
<?xml version="1.0" encoding="UTF-8"?>
<pearconfig version="1.0">
    <default_channel>pecl.php.net</default_channel>
    <php_dir>{php_home}/pear</php_dir>
    <download_dir>{php_home}/tmp</download_dir>
    <temp_dir>{php_home}/tmp</temp_dir>
    <cache_dir>{php_home}/tmp</cache_dir>
    <bin_dir>{php_home}/bin</bin_dir>
</pearconfig>
"""
        
        # Write configuration
        config_dir = Path(php_home) / "pear" / ".config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_dir / "pear.conf", 'w') as f:
            f.write(pecl_config)
            
        console.print("[green]✓ PECL configured successfully[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error configuring PECL: {str(e)}[/red]")
        return False

def install_pecl_extension(extension_name, version=None):
    """Install a PHP extension from PECL"""
    try:
        php_bins = find_php()
        if not php_bins:
            return False
            
        # Check if already installed
        installed = get_installed_extensions()
        if extension_name.lower() in [ext.lower() for ext in installed]:
            console.print(f"[green]✓ Extension already installed: {extension_name}[/green]")
            return True
            
        # Configure PECL if needed
        if not configure_pecl():
            return False
            
        # Prepare installation command
        cmd = [str(php_bins['pecl']), 'install']
        if version:
            cmd.append(f"{extension_name}-{version}")
        else:
            cmd.append(extension_name)
            
        console.print(f"Installing PHP extension: {extension_name}")
        
        # Run installation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Enable extension in php.ini
            env_vars = load_sdk_env()
            php_home = env_vars.get('PHP_HOME')
            ini_file = Path(php_home) / "php.ini"
            
            if ini_file.exists():
                with open(ini_file, 'a') as f:
                    f.write(f"\nextension={extension_name}.so\n")
                    
            console.print(f"[green]✓ Successfully installed extension: {extension_name}[/green]")
            return True
        else:
            console.print(f"[red]Error installing extension: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error installing extension: {str(e)}[/red]")
        return False

def install_pecl_extensions(extension_list):
    """Install multiple PHP extensions"""
    success_count = 0
    failed = []
    
    for ext in extension_list:
        # Handle version specification
        if '@' in ext:
            name, version = ext.split('@', 1)
            if install_pecl_extension(name, version):
                success_count += 1
            else:
                failed.append(ext)
        else:
            if install_pecl_extension(ext):
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
    install_pecl_extension("redis")
    
    # Install multiple extensions with versions
    extensions = [
        "redis@5.3.7",
        "xdebug",
        "mongodb@1.15.0"
    ]
    install_pecl_extensions(extensions) 