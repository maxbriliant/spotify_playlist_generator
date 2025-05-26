"""
Logging Utilities - Centralized logging configuration
===================================================
Version: 2.0.0
Author: MaxBriliant

Provides centralized logging setup with console and file handlers.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(name: str = "spotify_generator", 
                debug: bool = False,
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup application logger with proper formatting.
    
    Args:
        name: Logger name
        debug: Enable debug level logging
        log_file: Path to log file (default: spotify_playlist.log)
    
    Returns:
        Configured logger instance
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_file = "spotify_playlist.log"
    
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

class ConsoleLogger:
    """Simple console logger that can be used in GUI applications."""
    
    def __init__(self, callback=None):
        """
        Initialize console logger.
        
        Args:
            callback: Function to call with log messages (for GUI integration)
        """
        self.callback = callback
        self.logger = logging.getLogger("console")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"{timestamp} - {level} - {message}"
        
        # Log to standard logger
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Send to callback (e.g., GUI console)
        if self.callback:
            self.callback(formatted_message)
    
    def info(self, message: str):
        """Log info message."""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message."""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Log error message."""
        self.log(message, "ERROR")