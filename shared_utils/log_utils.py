import logging
from datetime import datetime
from logging import FileHandler, StreamHandler
from pathlib import Path


def get_logger(logger_name, logs_dir, log_level=logging.DEBUG):
    """
    Returns a logger object with the specified name, that writes to the specified file at the specified log level
    """
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    log_filename = f"{Path().cwd().parts[-1]}_{now}.log"

    log_file = Path(logs_dir, log_filename)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    file_handler = FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
