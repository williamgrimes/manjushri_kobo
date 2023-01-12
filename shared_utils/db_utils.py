"""Utility functions for interaction with sqlite database."""
import logging
import sqlite3
from typing import Type

import pandas as pd

from shared_utils.log_utils import get_logger, ProjectLogger

logger = ProjectLogger(__name__)


class KoboDB:
    """Setup and Teardown connection to sqlite database."""

    def __init__(self, db_path: str) -> None:
        self.db_name = db_path

    def __enter__(self) -> Type[sqlite3.Connection]:
        self.conn = sqlite3.connect(self.db_name)
        logger.info(
            f"Connected to sqlite database: {self.db_name}")
        return self.conn

    def __exit__(self, exc_type: Type, exc_val: Type, exc_tb: Type) -> None:
        logger.info(
            f"Closing sqlite connection: {self.db_name}")
        self.conn.close()

    def query_to_df(
        cursor: sqlite3.Connection,
        query_path: str,
    ) -> pd.DataFrame:
        """Run a query on database and return a pandas dataframe."""
        with open(query_path, 'r') as f:
            query_str = f.read()
        cursor.execute(query_str)
        results = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(results, columns=columns)
        logger.info(f"Query:\n{query_str}\nReturned Dataframe with "
                    f"{len(df)} rows and {len(df.columns)}.")
        return df
