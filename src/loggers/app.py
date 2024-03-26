import json
import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter, StreamHandler

from src.config import settings
from src.loggers.main import add_logger_type

from src.loggers.main import main_logger


class AppLogger(logging.Logger):
    class JsonHandler(RotatingFileHandler):
        class JsonFormatter(Formatter):
            # Formats the log message as a JSON object
            def format(self, record):
                return json.dumps(
                    {
                        "timestamp": self.formatTime(record),
                        "level": record.levelname,
                        "logger_types": record.logger_types,
                        "message": record.getMessage(),
                        "module": record.module,
                        "filename": record.filename,
                        "funcName": record.funcName,
                        "lineno": record.lineno,
                        "thread": record.thread,
                        "process": record.process,
                    }
                )

        json_formatter = JsonFormatter()

        def __init__(self):
            super().__init__(
                str(settings.LOGS_FOLDER.joinpath("app_json.log")),
                mode="a",
                maxBytes=1000 * 1000 * 1000 * 5,
                backupCount=3,
            )
            self.setLevel(logging.DEBUG)
            self.setFormatter(self.json_formatter)

    class DebugHandler(RotatingFileHandler):
        detailed_formatter = Formatter(
            "[%(asctime)s][%(logger_types)s][%(levelname)s] - %(message)s"
        )

        def __init__(self):
            super().__init__(
                str(settings.LOGS_FOLDER.joinpath("debug.log")),
                mode="a",
                maxBytes=1000 * 1000 * 1000 * 5,
                backupCount=3,
            )
            self.setLevel(logging.DEBUG)
            self.setFormatter(self.detailed_formatter)

    class InfoHandler(RotatingFileHandler):
        simple_formatter = Formatter("[%(asctime)s][%(levelname)s] - %(message)s")

        def __init__(self):
            super().__init__(
                str(settings.LOGS_FOLDER.joinpath("info.log")),
                mode="a",
                maxBytes=1000 * 1000 * 1000 * 5,
                backupCount=3,
            )
            self.setLevel(logging.INFO)
            self.setFormatter(self.simple_formatter)

    class StdoutHandler(StreamHandler):
        simple_formatter = Formatter("%(levelname)s: %(message)s")

        def __init__(self):
            super().__init__()
            self.setLevel(logging.INFO)
            self.setFormatter(self.simple_formatter)

    TYPE = "APP"

    def __init__(self):
        super().__init__("app")
        self.setLevel(logging.DEBUG)
        self.parent = main_logger
        self.propagate = True

    def handle(self, record):
        record = add_logger_type(record, self)
        return super().handle(record)


app_logger = AppLogger()
