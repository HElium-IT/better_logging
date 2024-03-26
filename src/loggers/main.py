import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from src.config import settings


def add_logger_type(record, logger):
    if not hasattr(record, "logger_types"):
        record.logger_types = [logger.TYPE]
    else:
        record.logger_types.append(logger.TYPE)
    return record


def has_logger_type(record, logger):
    return hasattr(record, "logger_types") and logger.TYPE in record.logger_types


class AcceptedLoggersTypeFilter(logging.Filter):
    def __init__(self, accepted_loggers=None):
        self.accepted_loggers = accepted_loggers

    def filter(self, record):
        if not self.accepted_loggers:
            return True
        return any(has_logger_type(record, logger) for logger in self.accepted_loggers)


class MainQueueHandler(QueueHandler):
    def __init__(self, queue):
        super().__init__(queue)
        self.setLevel(logging.DEBUG)


class MainLogger(logging.Logger):
    TYPE = "MAIN"
    queue = Queue()
    queue_listener_handlers = []

    def __init__(self):
        super().__init__(settings.MAIN_APPLICATION_LOGGER_NAME)
        self.setLevel(logging.DEBUG)
        self.addHandler(MainQueueHandler(self.queue))

    def handle(self, record: logging.LogRecord) -> None:
        record = add_logger_type(record, self)
        return super().handle(record)

    def add_handler_to_queue(self, handler, accepted_loggers=None):
        handler.addFilter(AcceptedLoggersTypeFilter(accepted_loggers))
        self.queue_listener_handlers.append(handler)

    def start_queue_listener(self):
        self.queue_listener = QueueListener(
            self.queue,
            *self.queue_listener_handlers,
            respect_handler_level=True,
        )
        self.queue_listener.start()

    def stop_queue_listener(self):
        self.queue_listener.stop()


main_logger = MainLogger()
