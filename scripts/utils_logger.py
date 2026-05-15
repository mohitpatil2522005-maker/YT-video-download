import logging
import sys
from datetime import datetime


def setup_logger(name: str = "yt_downloader", level=logging.INFO, log_file: str = None):
    """
    Configure logger with console and optional file output.
    
    Args:
        name: Logger name
        level: Logging level (default INFO)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    fmt_str = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt_str, datefmt=datefmt)
    
    logger = logging.getLogger(name)
    
    # Only add handlers if not already configured
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"Warning: Could not create log file {log_file}: {e}")
    
    logger.setLevel(level)
    return logger
