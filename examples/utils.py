"""Utility functions for examples."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Create and configure a common logger for each example."""
    logger = logging.getLogger(name)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logger
