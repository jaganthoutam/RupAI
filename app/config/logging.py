"""
Enterprise Logging Configuration
Structured logging setup with multiple output formats and levels.
"""

import logging
import sys
from typing import Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler

from app.config.settings import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure enterprise-grade structured logging.
    
    Args:
        log_level: Override the default log level
    """
    level = log_level or settings.LOG_LEVEL
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Configure the root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[],
    )
    
    # Setup console handler with Rich for development
    if settings.is_development:
        # Use standard logging instead of Rich to avoid recursion errors
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(getattr(logging, level.upper()))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    else:
        # Production logging - structured JSON format
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s", '
            '"module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}'
        )
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Payment provider loggers
    logging.getLogger("stripe").setLevel(logging.INFO)
    logging.getLogger("razorpay").setLevel(logging.INFO)
    
    # Database loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    
    # Redis logger
    logging.getLogger("redis").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(
        f"🔧 Logging configured - Level: {level}, Environment: {settings.ENVIRONMENT}, Structured: {settings.is_production}"
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
