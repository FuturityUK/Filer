import sqlite3
from sqlite3 import Error

class Database:
    """ Class to handle SQlite operations """

    connection = None

    def __init__(self):
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




