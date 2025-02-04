"""
Install Command

This module implements the 'install' command for installing development tools
into the DevMatic SDK environment.
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
@click.option('--version', '-v', help='Specific version to install')
@click.option('--force', '-f', is_flag=True, help='Force reinstall if already installed')
def install(tool: str, version: Optional[str] = None, force: bool = False):
    """Install a development tool.
    
    TOOL is the name of the tool to install (e.g. python, node, git)
    """
    try:
        # Get installer for tool
        installer_class = get_installer_class(tool)
        if not installer_class:
            raise click.ClickException(f"No installer found for tool: {tool}")
        
        # Create installer instance
        installer = installer_class({
            "version": version,
            "force": force
        })
        
        # Check if already installed
        if installer.is_installed() and not force:
            logger.info(f"{tool} is already installed")
            return
        
        # Run installation
        logger.info(f"Installing {tool}...")
        if not asyncio.run(installer.install()):
            raise click.ClickException(f"Failed to install {tool}")
        
        logger.info(f"Successfully installed {tool}")
        
    except Exception as e:
        logger.error(f"Installation failed: {str(e)}")
        raise click.ClickException(str(e)) 