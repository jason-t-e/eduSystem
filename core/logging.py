# core/logging.py
import sys
import uuid
from contextvars import ContextVar
from loguru import logger as _logger
from pathlib import Path


# ContextVar stores the current correlation ID per async task
# Each asyncio task gets its own context — concurrent requests don't share IDs
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="--------")


def new_correlation_id() -> str:
    """Generate a new correlation ID and store it in the current async context."""
    cid = str(uuid.uuid4())[:8]
    _correlation_id.set(cid)
    return cid


def get_correlation_id() -> str:
    """Get the current correlation ID (for passing to child tasks)."""
    return _correlation_id.get()


def set_correlation_id(cid: str) -> None:
    """Set an existing correlation ID (used when propagating to child tasks)."""
    _correlation_id.set(cid)


def setup_logging(log_level: str = "DEBUG") -> None:
    """Configure loguru. Call once at application startup."""
    Path("logs").mkdir(exist_ok=True)

    _logger.remove()  # Remove default handler

    # Console: colored, human-readable
    _logger.add(
        sys.stdout,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<yellow>{extra[cid]}</yellow> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
        colorize=True,
    )

    # File: structured, for later analysis
    _logger.add(
        "logs/edusystem.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[cid]} | {name}:{line} | {message}",
        level=log_level,
    )


def get_logger(name: str):
    """
    Get a logger bound to the current correlation ID.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing concept", concept_id="acc11_ch1")
    """
    return _logger.bind(cid=get_correlation_id())


# Pre-configured root logger — use get_logger(__name__) in modules instead
logger = _logger.bind(cid="--------")