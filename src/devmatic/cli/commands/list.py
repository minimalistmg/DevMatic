"""
List Command

This module implements the 'list' command for displaying available and installed
development tools in the DevMatic SDK environment.
"""

import click
import json
import logging
from pathlib import Path
from typing import Dict, List
from devmatic import SDK_CONFIG_FILE
from devmatic.utils.windows import WindowsUtils
from devmatic.core.base.installer import get_available_tools

logger = logging.getLogger(__name__)

def get_installed_tools() -> Dict[str, str]:
    """Get dictionary of installed tools and their versions"""
    sdk_root = WindowsUtils.get_install_root()
    config_file = sdk_root / SDK_CONFIG_FILE
    
    if not config_file.exists():
        return {}
    
    with open(config_file) as f:
        return json.load(f)

def format_tool_info(name: str, info: Dict) -> str:
    """Format tool information for display"""
    status = "Installed" if info.get("installed") else "Available"
    version = info.get("version", "latest")
    description = info.get("description", "No description available")
    
    return f"{name:15} [{status:^10}] {version:10} - {description}"

@click.command(name="list")
@click.option('--installed', '-i', is_flag=True, help='Show only installed tools')
@click.option('--available', '-a', is_flag=True, help='Show only available tools')
def list_tools(installed: bool = False, available: bool = False):
    """List available and installed development tools.
    
    If no options are specified, shows both installed and available tools.
    """
    try:
        # Get installed tools
        installed_tools = get_installed_tools()
        
        # Get available tools
        available_tools = get_available_tools()
        
        # Prepare display information
        tools_info = {}
        
        # Add installed tools
        if not available:
            for name, version in installed_tools.items():
                tools_info[name] = {
                    "installed": True,
                    "version": version
                }
        
        # Add available tools
        if not installed:
            for name, info in available_tools.items():
                if name not in tools_info:
                    tools_info[name] = {
                        "installed": False,
                        "version": "latest",
                        "description": info.get("description", "")
                    }
        
        # Display tools
        if not tools_info:
            logger.info("No tools found")
            return
        
        click.echo("\nAvailable Tools:\n")
        for name in sorted(tools_info.keys()):
            click.echo(format_tool_info(name, tools_info[name]))
        click.echo()
        
    except Exception as e:
        logger.error(f"Failed to list tools: {str(e)}")
        raise click.ClickException(str(e)) 