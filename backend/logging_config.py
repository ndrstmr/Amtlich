import json
import logging


class JsonFormatter(logging.Formatter):
    def format(
        self, record: logging.LogRecord
    ) -> str:  # pragma: no cover - simple formatting
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging() -> None:
    """Configure root logger with JSON formatter."""
    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
