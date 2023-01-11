"""Setup and teardown connection to sqlite database"""
import sqlite3
from typing import Type


class DBConnection:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def __enter__(self) -> Type[sqlite3.Connection]:
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type: Type, exc_val: Type, exc_tb: Type) -> None:
        self.conn.close()
