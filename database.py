import sqlite3
from sqlite3 import Error
from sql import SQLDictionary
import os.path
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
    __verbose = False

    def __init__(self, path: str, create_tables: bool):
        self.__connection = self.create_connection(path)
        self.__cursor = self.create_cursor()
        self.__sql_dictionary = SQLDictionary().sql_dictionary
        self.__dry_run_mode = False
        self.__verbose = False
        if create_tables:
            print("Creating tables.")
        return

    def set_test(self, test: bool):
        self.__dry_run_mode = test

    def set_verbose_mode(self, verbose: bool):
        self.__verbose = verbose
        if self.__verbose:
            self.__connection.set_trace_callback(print)
        else:
            self.__connection.set_trace_callback(None)

    def __vprint(self, string: str):
        if self.__verbose:
            print(string)

    def close_database(self):
        self.commit()
        self.close_cursor()
        self.close_connection()

    def create_connection(self, path: str):
        self.__connection = None
        try:
            sqlite3.enable_callback_tracebacks(True)
            #database_path_string = 'file:'+path+'?mode=rw'
            #__vprint__(f"database_path_string: {database_path_string}")
            self.__connection = sqlite3.connect(path)
            #if os.path.isfile(path):
            if self.__connection is not None:
                self.__vprint("Connection to SQLite DB successful")
            else:
                self.__vprint("Connection to SQLite DB failed")
                raise sqlite3.OperationalError("Connection to SQLite DB failed")
        except sqlite3.OperationalError as e:
            print(f"sqlite3.OperationalError: '{e}'")
            exit(2)  # Exit with system code 2 to indicate and error
        except Exception as e:
            print(f"Exception: '{e}'")
            exit(2) # Exit with system code 2 to indicate and error
        return self.__connection

    def close_connection(self):
        self.__connection.close()

    def create_cursor(self):
        self.__cursor = self.__connection.cursor()
        return self.__cursor

    def close_cursor(self):
        self.__cursor.close()

    # Decorator function
    """
    def my_decorator(self, original_function):
        def wrapper(*args, **kwargs):
            if not self.__dry_run_mode:
                print(f"Calling {self.__cursor.execute.__name__} with args: {args}, kwargs: {kwargs}")
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
            return self.__cursor.execute(sql, parameters)
        else:
            return self.__cursor.execute(sql)

    def executescript(self, sql: str):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.
        :param sql: SQL statement to execute
        """
        return self.__cursor.executescript(sql)

    def commit(self):
        if not self.__dry_run_mode:
            # Commit changes to the database
            self.__connection.commit()

    def get_last_row_id(self):
        if self.__dry_run_mode:
            return None
        else:
            return self.__cursor.lastrowid

    def fetch_all_results(self):
        if self.__dry_run_mode:
            return None
        else:
            return self.__cursor.fetchall()

    def vacuum(self):
        # Shrink to database to reclaim unused space in the database file as well fix defragmentation.
        self.__connection.isolation_level = None
        self.execute("VACUUM")
        self.__connection.isolation_level = ''  # <- note that this is the default value of isolation_level
        # self.database_connection.commit()
        self.commit()

    def create_database_structure(self):
        print(f"Creating database.")
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["create_database_tables_and_indexes"]}\"")
        self.executescript(self.__sql_dictionary["create_database_tables_and_indexes"])
        self.commit()
        print(f"Database created.")

    def find_filename_exact_match(self, filename: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["find_filename_exact_match"]}\"")
        self.__vprint(f"filename: \"{filename}\"")
        self.execute(self.__sql_dictionary["find_filename_exact_match"], [filename]
            )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            rows_found += 1
        print(f"{rows_found} results found")

    def find_filename_like(self, search: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["find_filename_like"]}\"")
        self.__vprint(f"filename: \"{search}\"")

        self.execute(self.__sql_dictionary["find_filename_like"],
                     search
                    )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            rows_found += 1
        print(f"{rows_found} results found")

    def find_driveid(self, make: str, model: str, serial_number: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["find_driveid"]}\"")
        self.__vprint(f"make: \"{make}\", model: \"{model}\", serial_number: \"{serial_number}\"")
        self.execute(self.__sql_dictionary["find_driveid"],
                     (make, model, serial_number)
                    )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            rows_found += 1
        print(f"{rows_found} results found")

    def empty_table(self, database_cursor):
        ## FIX ##
        self.execute("DELETE FROM FileSystemEntries;")
        self.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='FileSystemEntries';")
        # Commit changes to the database
        self.commit()

### Class Test ###
#database = Database("I:\\FileProcessorDatabase\\database.sqlite")
#print(f"sql_dictionary: {database.sql_dictionary}")












