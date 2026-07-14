import logging
from typing import Optional, Union


def parse_log_level(level: Union[int, str]) -> int:
    """
    Parse a log level name or number into a logging level constant.

    Args:
        level: Either an integer logging level or a string like 'INFO' or 'DEBUG'

    Returns:
        The corresponding logging level constant.
    """
    if isinstance(level, str):
        return getattr(logging, level.upper(), logging.INFO)
    return level


def setup_logger(name: str = 'AppLogger', 
                level: Optional[Union[int, str]] = None,
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
    if level is not None:
        logger.setLevel(parse_log_level(level))
    logger.propagate = False
    
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


def configure_logging(
    level: Union[int, str] = logging.INFO,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_file: Optional[str] = None,
) -> None:
    """
    Configure the log level for all existing and future loggers.

    Args:
        level: Either an integer logging level or a string like 'INFO' or 'DEBUG'
        log_format: Format string for log messages
        log_file: Optional file path for file logging
    """
    parsed_level = parse_log_level(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(parsed_level)
    root_logger.propagate = False

    if not root_logger.handlers:
        formatter = logging.Formatter(log_format)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)

    for existing_logger in logging.Logger.manager.loggerDict.values():
        if isinstance(existing_logger, logging.Logger):
            existing_logger.setLevel(parsed_level)


def configure_logging(
    level: Union[int, str] = logging.INFO,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_file: Optional[str] = None,
) -> None:
    """
    Configure the log level for all existing and future loggers.

    Args:
        level: Either an integer logging level or a string like 'INFO' or 'DEBUG'
        log_format: Format string for log messages
        log_file: Optional file path for file logging
    """
    parsed_level = parse_log_level(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(parsed_level)
    root_logger.propagate = False

    if not root_logger.handlers:
        formatter = logging.Formatter(log_format)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)

    for existing_logger in logging.Logger.manager.loggerDict.values():
        if isinstance(existing_logger, logging.Logger):
            existing_logger.setLevel(parsed_level)
