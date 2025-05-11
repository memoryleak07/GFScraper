import logging
from typing import Optional

def setup_logger(name: str = 'AppLogger', 
                level: int = logging.INFO,
                log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Centralized logger configuration for the entire application.
    
    Args:
        name: Logger name
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_format: Format string for log messages
        log_file: Optional file path for file logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding handlers multiple times
    if not logger.handlers:
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger