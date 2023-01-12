import logging
import sqlite3
from datetime import datetime
from logging import FileHandler, StreamHandler
from pathlib import Path

import pandas as pd


now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

project_name = Path().cwd().parts[-1]



def get_logger(logger_name, log_level=logging.DEBUG):
    """
    Returns a logger object with the specified name, that writes to the specified file at the specified log level
    """

    log_file = Path(f"logs/{now}_{project_name}.log")

    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # create file handler and set level to info
    file_handler = FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # create console handler and set level to debug
    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

    # add formatter to handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
