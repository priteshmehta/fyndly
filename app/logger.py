import logging
import sys
from logging import Logger
from typing import Optional

class AppLogger:
    _logger: Optional[Logger] = None

    @staticmethod
    def get_logger(name: str = "fyndly") -> Logger:
        if AppLogger._logger:
            return AppLogger._logger

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        # Avoid duplicate logs
        if not logger.handlers:
            logger.addHandler(console_handler)

        logger.propagate = False
        AppLogger._logger = logger
        return logger
