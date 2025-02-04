"""
DevMatic CLI Entry Point

This module serves as the main entry point for the DevMatic CLI.
"""
from os import name as os_name, system as os_system
from sys import stdout as sys_stdout, exit as sys_exit

"""Set the console window title IMMEDIATELY"""
if os_name == 'nt':  # Windows
    os_system(f'title DevMatic v1.0.0')
else:  # macOS/Linux
    sys_stdout.write(f'\x1b]2;DevMatic v1.0.0\x07')
    sys_stdout.flush()

# Animated welcome banner
from rich.status import Status
splash = Status("[bold light_green]Starting DevMatic...", spinner="dots")
splash.start()

import time
import subprocess
from rich.console import Console

console = Console()

from cli.main import cli

def welcome():
    # Main title with an innovative design
    console.print(f"""
    [bold light_green]DevMatic v1.0.0[/bold light_green]
    \n[bold cyan]📦 Complete SDK Management | 🛠️  Easy Installations | 🔄 Auto Updates[/bold cyan]
    \n[dim]─────────────── Let's Get Started! ───────────────[/dim]
    """, justify="center")

def main():
    """Main entry point for the DevMatic CLI"""
    try:
        splash.stop()
        welcome()
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys_exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys_exit(1)

if __name__ == "__main__":
    main()