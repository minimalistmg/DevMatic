"""
Logger Utilities

This module provides logging configuration and utilities for DevMatic.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union, Dict
from logging.handlers import RotatingFileHandler

def setup_logger(
    name: str = "devmatic",
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Path] = None,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 3,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with console and optional file output.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        max_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        format_string: Custom format string for log messages
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Default format
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if requested)
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")
    
    return logger

def set_log_levels(levels: Dict[str, Union[int, str]]):
    """Set logging levels for multiple loggers.
    
    Args:
        levels: Dictionary mapping logger names to levels
    """
    for name, level in levels.items():
        logging.getLogger(name).setLevel(level)

# Default format strings
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
) 