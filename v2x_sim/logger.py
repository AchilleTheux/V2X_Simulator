"""Logging utilities for the V2X simulator."""

import logging


def build_logger(name: str = "v2x_sim", level: int = logging.INFO) -> logging.Logger:
    """Create and configure a shared logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)

    return logger
