import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter, StreamHandler
import time
from functools import wraps
from uuid import uuid4

from contextvars import ContextVar

from src.config import settings

from src.loggers.main import add_logger_type
from src.loggers.main import main_logger


class FlowLogger(logging.Logger):
    class FlowFileHandler(RotatingFileHandler):
        detailed_formatter = Formatter(
            "[%(asctime)s][%(custom_func_name)s][%(custom_flow_id)s][%(levelname)s] - %(message)s"
        )

        def __init__(self) -> None:
            super().__init__(
                str(settings.LOGS_FOLDER.joinpath("flow.log")),
                mode="a",
                maxBytes=1000 * 1000 * 1000 * 5,
                backupCount=3,
            )
            self.setLevel(logging.DEBUG)
            self.setFormatter(self.detailed_formatter)

    class FlowStdoutHandler(StreamHandler):
        simple_formatter = Formatter(
            "[%(custom_func_name)s][%(custom_flow_id)s][%(levelname)s] - %(message)s"
        )

        def __init__(self) -> None:
            super().__init__()
            self.setLevel(logging.INFO)
            self.setFormatter(self.simple_formatter)

    TYPE = "FLOW"

    unique_id = None
    func_name = None
    function_deepness_ctx = ContextVar("function_deepness", default=0)

    def __init__(self) -> None:
        super().__init__(f"{settings.MAIN_APPLICATION_LOGGER_NAME}.flow")
        self.setLevel(logging.DEBUG)
        self.parent = main_logger
        self.propagate = True

    def handle(self, record: logging.LogRecord) -> None:
        record = add_logger_type(record, self)
        record.custom_flow_id = self.unique_id
        record.custom_func_name = self.func_name
        return super().handle(record)

    @staticmethod
    def set_func_name(func):
        if func is None:
            FlowLogger.func_name = None
            return
        module_parts = func.__module__.split(".")
        if len(module_parts) > 2:
            FlowLogger.func_name = f"{'.'.join(module_parts[-2:])}.{func.__name__}"
        else:
            FlowLogger.func_name = f"{func.__module__}.{func.__name__}"

    @staticmethod
    def get_function_deepness():
        return FlowLogger.function_deepness_ctx.get()

    @staticmethod
    def set_function_deepness(function_deepness):
        FlowLogger.function_deepness_ctx.set(function_deepness)

    @staticmethod
    def set_unique_id():
        FlowLogger.unique_id = str(uuid4())[:8]


flow_logger = FlowLogger()


def update_flow(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if (function_deepness := FlowLogger.get_function_deepness()) == 0:
            FlowLogger.set_unique_id()

        FlowLogger.set_function_deepness(function_deepness + 1)
        FlowLogger.set_func_name(func)

        exc = None
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            exc = e

        FlowLogger.set_function_deepness(function_deepness)
        FlowLogger.set_func_name(func)

        if exc:
            raise exc

        return result

    return wrapper


def log_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        flow_logger.info(f"finished in {end_time - start_time:.4f}s")
        return result

    return wrapper
