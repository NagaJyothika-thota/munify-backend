"""
Standard logging configuration for the application
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level based on environment
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            # Root logger
            "": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            # Application loggers
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "app.core": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "app.api": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "app.services": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False,
            },
            "app.models": {
                "handlers": ["file"],
                "level": "DEBUG",
                "propagate": False,
            },
            # Third-party loggers
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["file"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    
    # Add error handler to root logger
    config["loggers"][""]["handlers"].append("error_file")
    
    return config


def setup_logging() -> None:
    """Setup logging configuration"""
    config = get_logging_config()
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with proper naming"""
    return logging.getLogger(f"app.{name}")


# Create a default logger for the logging module itself
logger = get_logger("core.logging")
