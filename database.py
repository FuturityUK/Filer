import sqlite3
import traceback
import sys
from typing import (
    Iterable,
    Union,
    Optional,
)
from sql import SQLDictionary


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

    def __vprint(self, string: str):
        if self.__verbose:
            print(string)

    def set_test(self, test: bool):
        self.__dry_run_mode = test

    def set_verbose_mode(self, verbose: bool):
        self.__verbose = verbose
        if self.__verbose:
            self.__connection.set_trace_callback(print)
        else:
            self.__connection.set_trace_callback(None)

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
        self.__vprint(sql)
        try:
            if parameters is not None:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
        except sqlite3.Error as err:
            #print(f"Error in SQL execute: {err.sqlite_errorname}")
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            print("Exiting.")
            exit(2)

    def executescript(self, sql: str):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.
        :param sql: SQL statement to execute
        """
        self.__vprint(sql)
        try:
            self.__cursor.executescript(sql)
        except sqlite3.Error as err:
            print(f"Error in SQL executescript: {err.sqlite_errorname}")
            print("Exiting.")
            exit(2)

    def commit(self):
        if not self.__dry_run_mode:
            # Commit changes to the database
            self.__connection.commit()

    def get_last_row_id(self):
        # Provides the row id of the last inserted row
        # Not that for other statements, after executemany() or executescript(), or if the insertion failed,
        # the value of lastrowid is left unchanged. Therefore, always check and handle insert errors.
        # The initial value of lastrowid is None.
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
                     [search]
                    )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            rows_found += 1
        self.__vprint(f"{rows_found} results found")

    def find_drive_id(self, make: str, model: str, serial_number: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["find_drive_id"]}\"")
        self.__vprint(f"make: \"{make}\", model: \"{model}\", serial_number: \"{serial_number}\"")
        self.execute(self.__sql_dictionary["find_drive_id"],
                     (make, model, serial_number)
                    )
        drive_ids = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            drive_ids.append(row[0])
            rows_found += 1
        self.__vprint(f"{rows_found} results found")
        return drive_ids

    def insert_drive(self, make: str, model: str, serial_number: str, hostname: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["insert_drive"]}\"")
        self.__vprint(f"make: \"{make}\", model: \"{model}\", serial_number: \"{serial_number}\", hostname: \"{hostname}\"")
        self.execute(self.__sql_dictionary["insert_drive"],
                     (make, model, serial_number, hostname)
                    )
        drive_id = self.get_last_row_id()
        self.__vprint(f"New row driveid: \"{drive_id}\"")
        return drive_id

    def find_filesystem_id(self, label: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["find_filesystem_id"]}\"")
        self.__vprint(f"label: \"{label}\"")
        self.execute(self.__sql_dictionary["find_filesystem_id"],
                     [label] # Use [] as a single parameter
                    )
        filesystem_ids = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(row[0])
            filesystem_ids.append(row[0])
            rows_found += 1
        self.__vprint(f"{rows_found} results found")
        return filesystem_ids

    def insert_filesystem(self, label: str, drive_id: int, date: int):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["insert_filesystem"]}\"")
        self.__vprint(f"label: \"{label}\", drive_id: \"{drive_id}\", date: \"{date}\"")
        self.execute(self.__sql_dictionary["insert_filesystem"],
                     (label, drive_id, date)
                    )
        filesystem_id = self.get_last_row_id()
        self.__vprint(f"New row filesystem_id: \"{filesystem_id}\"")
        return filesystem_id

    def delete_filesystem_listing(self, filesystem_id: int):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["delete_filesystem"]}\"")
        self.__vprint(f"filesystem_id: \"{filesystem_id}\"")
        self.execute(self.__sql_dictionary["delete_filesystem"],
                     [filesystem_id] # [] as a single parameter
                     )

    def delete_filesystem_listing_entries(self, filesystem_id: int):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["delete_filesystem_entries"]}\"")
        self.__vprint(f"filesystem_id: \"{filesystem_id}\"")
        self.execute(self.__sql_dictionary["delete_filesystem_entries"],
                     [filesystem_id] # [] as a single parameter
                     )

    def update_filesystem_date(self, filesystem_id: int, date: int):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["update_filesystem"]}\"")
        self.__vprint(f"filesystem_id: \"{filesystem_id}\", date: \"{date}\"")
        self.execute(self.__sql_dictionary["update_filesystem"],
                     (filesystem_id, date) # () as a multiple parameters
                     )

    def empty_table(self, table_name: str):
        ## FIX ##
        #self.execute("DELETE FROM ?;", [table_name]) # As a single parameter, we have to wrap it in []
        #self.execute("DELETE FROM SQLITE_SEQUENCE WHERE name=?;", [table_name] )
        # Commit changes to the database
        #self.commit()
        return

### Class Test ###
#database = Database("I:\\FileProcessorDatabase\\database.sqlite")
#print(f"sql_dictionary: {database.sql_dictionary}")












