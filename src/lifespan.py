from src.loggers import setup_loggers, start_main_logger, stop_main_logger

def on_startup():
    setup_loggers()
    start_main_logger()

def on_shutdown():
    stop_main_logger()

