import sqlite3
from sqlite3 import Error
#import functools
#from typing import Any, Callable, List, Optional, Tuple

class Database:
    """ Class to handle SQlite operations """

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.dry_run_mode = False
        return

    def set_dry_run_mode(self, dry_run_mode):
        self.dry_run_mode = dry_run_mode

    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")
        self.connection = connection
        return connection

    def create_cursor(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    def execute(self, database_cursor, sql_string, *sql_values):
        if not self.dry_run_mode:
            database_cursor.execute(sql_string, *sql_values)

    def commit(self):
        if not self.dry_run_mode:
            # Commit changes to the database
            self.connection.commit()

    def get_last_row_id(self, database_cursor):
        if self.dry_run_mode:
            return None
        else:
            return database_cursor.lastrowid

    def fetch_all_results(self, database_cursor):
        if self.dry_run_mode:
            return None
        else:
            return database_cursor.fetchall()

    def vacuum(self):
        # Shrink to database to reclaim unused space in the database file as well fix defragmentation.
        self.connection.isolation_level = None
        self.execute(self.cursor, "VACUUM")
        self.connection.isolation_level = ''  # <- note that this is the default value of isolation_level
        # self.database_connection.commit()
        self.commit()














