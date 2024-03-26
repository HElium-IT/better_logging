from pathlib import Path

class Settings():
    MAIN_FOLDER = Path(__file__).parent.parent.resolve()
    LOGS_FOLDER = MAIN_FOLDER.joinpath("logs")

    MAIN_APPLICATION_LOGGER_NAME = 'my_app_name'

settings = Settings()