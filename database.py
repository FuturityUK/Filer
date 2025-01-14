import sqlite3
from sqlite3 import Error
#import functools
#from typing import Any, Callable, List, Optional, Tuple

class Database:
    """ Class to handle SQlite operations """

    def __init__(self):
        self.connection = None
        self.cursor = None
        return

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















