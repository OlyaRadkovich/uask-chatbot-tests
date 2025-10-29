"""
Logging configuration (renamed)
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import LogConfig, LOGS_DIR


def setup_logger(name: str = __name__, level: str = None) -> logging.Logger:
    level = level or LogConfig.LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    if logger.handlers:
        return logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    file_handler = RotatingFileHandler(LogConfig.LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s - %(message)s', datefmt='%H:%M:%S')
    file_format = logging.Formatter('{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)
