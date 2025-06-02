import logging
import sys
import os
from logging import Logger
from typing import Optional
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


class AppLogger:
    _logger: Optional[Logger] = None

    @staticmethod
    def get_logger(name: str = "fyndly", level: int = logging.INFO, json_logs: bool = False) -> Logger:
        if AppLogger._logger:
            return AppLogger._logger

        logger = logging.getLogger(name)
        logger.setLevel(level)

        formatter = JsonFormatter() if json_logs else logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.propagate = False
        AppLogger._logger = logger
        return logger
