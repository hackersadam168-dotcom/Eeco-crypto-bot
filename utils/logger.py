"""Logging utility."""
import logging
from pathlib import Path
from config.settings import settings

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(settings.LOG_LEVEL)
    
    # Create logs directory
    Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    
    # File handler
    fh = logging.FileHandler(settings.LOG_FILE)
    fh.setLevel(settings.LOG_LEVEL)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
