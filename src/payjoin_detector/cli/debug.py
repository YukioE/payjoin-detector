import logging
import sys

LOGGER_NAME = "payjoin_detector"


def setup_debug_logger(path: str | None) -> logging.Logger:
    """
    Return the package logger.
    If *path* is given, attach a FileHandler at DEBUG level.
    Otherwise the logger is a no-op (no handlers, propagate=False).
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if path:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

        fh = logging.FileHandler(path, mode="a", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    return logger


def get_logger() -> logging.Logger:
    """Grab the package logger from anywhere in the codebase."""
    return logging.getLogger(LOGGER_NAME)
