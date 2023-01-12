import logging
from datetime import datetime
from logging import FileHandler, StreamHandler
from pathlib import Path


class ProjectLogger:
    def __init__(self, logger_name, log_dir="logs"):

        self.now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.project_name = Path().cwd().parts[-1]

        self.log_filename = f"{self.project_name}_{self.now}.log"

        self.log_file = Path(log_dir, self.log_filename).absolute()

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        # create file handler and set level to info
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)

        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            f"[%(asctime)s] [{self.project_name}] [%(name)s] [%(levelname)s] %(message)s")

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def info(self, message):
        self.logger.info(message)

    def log_location(self):
        self.logger.info(self.log_filename)


def get_logger(logger_name, logs_dir="logs", log_level=logging.DEBUG):
    """
    Returns a logger object with the specified name, that writes to the specified file at the specified log level
    """
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    project_name = Path().cwd().parts[-1]

    log_filename = f"{project_name}_{now}.log"

    log_file = Path(logs_dir, log_filename)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    file_handler = FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        f"[%(asctime)s] [{project_name}] [%(name)s] [%(levelname)s] %(message)s")

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
