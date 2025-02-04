"""
Update Command

This module implements the 'update' command for updating installed development tools
in the DevMatic SDK environment.
"""

import click
import logging
import asyncio
from typing import Optional
from pathlib import Path
from devmatic.core.base.installer import get_installer_class
from devmatic.core.environment import EnvironmentManager

logger = logging.getLogger(__name__)

@click.command()
@click.argument('tool')
@click.option('--version', '-v', help='Specific version to update to')
@click.option('--check', '-c', is_flag=True, help='Check for updates without installing')
def update(tool: str, version: Optional[str] = None, check: bool = False):
    """Update a development tool.
    
    TOOL is the name of the tool to update (e.g. python, node, git)
    """
    try:
        # Get installer for tool
        installer_class = get_installer_class(tool)
        if not installer_class:
            raise click.ClickException(f"No installer found for tool: {tool}")
        
        # Create installer instance
        installer = installer_class({
            "version": version
        })
        
        # Check if installed
        if not installer.is_installed():
            raise click.ClickException(f"{tool} is not installed")
        
        # Check for updates
        current_version = installer.get_installed_version()
        latest_version = installer.get_latest_version()
        
        if version:
            target_version = version
        else:
            target_version = latest_version
        
        if current_version == target_version:
            logger.info(f"{tool} is already up to date (version {current_version})")
            return
        
        logger.info(f"Current version: {current_version}")
        logger.info(f"Target version: {target_version}")
        
        if check:
            return
        
        # Run update
        logger.info(f"Updating {tool}...")
        if not asyncio.run(installer.update(target_version)):
            raise click.ClickException(f"Failed to update {tool}")
        
        logger.info(f"Successfully updated {tool} to version {target_version}")
        
    except Exception as e:
        logger.error(f"Update failed: {str(e)}")
        raise click.ClickException(str(e)) 