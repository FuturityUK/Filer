import sqlite3
from sqlite3 import Error
from sql import SQLDictionary
#import functools
#from typing import Any, Callable, List, Optional, Tuple
from typing import (
    cast,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Union,
    Optional,
    List,
    Tuple,
)


class Database:
    """ Class to handle SQlite operations """
    __verbose__ = False

    def __init__(self, path: str, create_tables: bool):
        self.connection = self.create_connection(path)
        self.cursor = self.create_cursor()
        self.sql_dictionary = SQLDictionary().sql_dictionary
        self.dry_run_mode = False
        self.__verbose__ = False
        if create_tables:
            print("Creating tables.")
        return

    def set_dry_run_mode(self, dry_run_mode: bool):
        self.dry_run_mode = dry_run_mode

    def set_verbose_mode(self, verbose: bool):
        self.__verbose__ = verbose
        if self.__verbose__:
            print(f"verbose enabled")
            self.connection.set_trace_callback(print)
        else:
            print(f"verbose disabled")
            self.connection.set_trace_callback(None)

    def __vprint__(self, string: str):
        if self.__verbose__:
            print(string)

    def close_database(self):
        self.commit()
        self.close_cursor()
        self.close_connection()

    def create_connection(self, path: str):
        self.connection = None
        try:
            self.connection = sqlite3.connect(path)
            self.__vprint__("Connection to SQLite DB successful")
        except Error as e:
            self.__vprint__(f"The error '{e}' occurred")
        return self.connection

    def close_connection(self):
        self.connection.close()

    def create_cursor(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    def close_cursor(self):
        self.cursor.close()

    # Decorator function
    """
    def my_decorator(self, original_function):
        def wrapper(*args, **kwargs):
            if not self.dry_run_mode:
                print(f"Calling {self.cursor.execute.__name__} with args: {args}, kwargs: {kwargs}")
                # Call the original function
                result = original_function(*args, **kwargs)
                # Log the return value
                print(f"{original_function.__name__} returned: {result}")
                # Return the result
                return result
        return wrapper

    @my_decorator
    def execute(self, ):
    """

    def execute(self,
        sql: str,
        parameters: Optional[Union[Iterable, dict]] = None
        ):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.

        :param sql: SQL statement to execute
        :param parameters: Parameters to use in that statement - an iterable for ``where id = ?``
          parameters, or a dictionary for ``where id = :id``
        """
        if parameters is not None:
            return self.cursor.execute(sql, parameters)
        else:
            return self.cursor.execute(sql)

    def executescript(self, sql: str):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.
        :param sql: SQL statement to execute
        """
        return self.cursor.executescript(sql)

    def commit(self):
        if not self.dry_run_mode:
            # Commit changes to the database
            self.connection.commit()

    def get_last_row_id(self):
        if self.dry_run_mode:
            return None
        else:
            return self.cursor.lastrowid

    def fetch_all_results(self):
        if self.dry_run_mode:
            return None
        else:
            return self.cursor.fetchall()

    def vacuum(self):
        # Shrink to database to reclaim unused space in the database file as well fix defragmentation.
        self.connection.isolation_level = None
        self.execute("VACUUM")
        self.connection.isolation_level = ''  # <- note that this is the default value of isolation_level
        # self.database_connection.commit()
        self.commit()

    def create_database_structure(self):
        print(f"Creating database.")
        self.__vprint__(f"SQL Query: \"{self.sql_dictionary["create_database_tables_and_indexes"]}\"")
        self.executescript(self.sql_dictionary["create_database_tables_and_indexes"])
        self.commit()
        print(f"Database created.")

    def find_filename_exact_match(self, filename: str):
        if self.__verbose__:
            print(f"SQL Query: \"{self.sql_dictionary["find_filename_exact_match"]}\"")
            print(f"filename: \"{filename}\"")

        self.execute(self.sql_dictionary["find_filename_exact_match"], [filename]
            )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            rows_found += 1
        print(f"{rows_found} results found")

    def find_filename_like(self, search: str):
        if self.__verbose__:
            print(f"SQL Query: \"{self.sql_dictionary["find_filename_like"]}\"")
            print(f"filename: \"{search}\"")

        self.execute(self.sql_dictionary["find_filename_like"], [search]
            )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            rows_found += 1
        print(f"{rows_found} results found")

### Class Test ###
#database = Database("I:\\FileProcessorDatabase\\database.sqlite")
#print(f"sql_dictionary: {database.sql_dictionary}")












