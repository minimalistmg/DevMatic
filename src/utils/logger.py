from rich.console import Console
from rich.status import Status
from rich.progress import Progress
from typing import Optional
import logging
import sys

class Logger:
    def __init__(self, log_file: str = "devmatic.log"):
        self.console = Console()
        self.log_file = log_file
        
        # Configure logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def info(self, message: str) -> None:
        """Log info message"""
        self.console.print(f"[blue]ℹ[/blue] {message}")
        logging.info(message)

    def success(self, message: str) -> None:
        """Log success message"""
        self.console.print(f"[green]✓[/green] {message}")
        logging.info(f"SUCCESS: {message}")

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message"""
        self.console.print(f"[red]✗[/red] {message}")
        if exception:
            logging.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            logging.error(message)

    def progress(self, description: str) -> Progress:
        """Create progress bar"""
        return Progress(
            *Progress.get_default_columns(),
            console=self.console,
            description=description
        )

    def status(self, message: str) -> Status:
        """Create status spinner"""
        return Status(message, console=self.console) 