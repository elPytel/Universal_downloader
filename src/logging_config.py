import logging
import os


def configure_app_logging(
    log_file: str = "logs/universal_downloader.log",
    log_level: str = "INFO",
) -> logging.Logger:
    """Configure the application logger used by terminal download workflows."""
    level = getattr(logging, log_level.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f"Unsupported log level: {log_level}")

    log_directory = os.path.dirname(log_file)
    if log_directory:
        os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger("universal_downloader")
    logger.setLevel(level)
    logger.propagate = False

    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == os.path.abspath(log_file):
            handler.setLevel(level)
            return logger

    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    return logger
