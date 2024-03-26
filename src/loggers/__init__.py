from src.loggers.main import main_logger

from src.loggers.app import app_logger
from src.loggers.flow import flow_logger, update_flow, log_time


def setup_loggers():
    main_logger.add_handler_to_queue(app_logger.JsonHandler())
    main_logger.add_handler_to_queue(
        app_logger.StdoutHandler(),
        [main_logger, app_logger],
        )
    main_logger.add_handler_to_queue(
        app_logger.DebugHandler(),
        [app_logger, flow_logger],
    )
    main_logger.add_handler_to_queue(
        app_logger.InfoHandler(),
        [app_logger, flow_logger],
    )
    main_logger.add_handler_to_queue(
        flow_logger.FlowFileHandler(),
        [flow_logger],
    )
    main_logger.add_handler_to_queue(
        flow_logger.FlowStdoutHandler(),
        [flow_logger],
    )

def start_main_logger():
    main_logger.start_queue_listener()

def stop_main_logger():
    main_logger.stop_queue_listener()


__all__ = [
    "setup_loggers",
    "start_main_logger",
    "stop_main_logger",
    "app_logger",
    "flow_logger",
    "update_flow",
    "log_time",
]
