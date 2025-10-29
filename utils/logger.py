"""
Logging configuration for the test framework
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import LogConfig, LOGS_DIR


def setup_logger(name: str = __name__, level: str = None) -> logging.Logger:
    """
    Setup and configure logger with both file and console handlers

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    level = level or LogConfig.LOG_LEVEL

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LogConfig.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    # Formatters
    console_format = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )

    # Enhanced file format for Selenium debugging
    file_format = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | '
        '%(message)s'
        '%(webdriver_commands)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add custom filter for WebDriver commands
    class WebDriverFilter(logging.Filter):
        def filter(self, record):
            record.webdriver_commands = (
                f' | {record.args}' if (
                    'selenium.webdriver' in record.name
                    and record.levelno == logging.DEBUG
                ) else ''
            )
            return True

    file_handler.addFilter(WebDriverFilter())

    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Set selenium logger level
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.WARNING)  # Reduce Selenium's verbose logging

    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get or create logger

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)