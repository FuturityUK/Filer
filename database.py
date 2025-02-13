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

    def __init__(self, path: str):
        self.__connection = self.create_connection(path)
        self.__cursor = self.create_cursor()
        self.__sql_dictionary = SQLDictionary().sql_dictionary
        self.__sql_versions = SQLDictionary().sql_versions
        self.__dry_run_mode = False
        self.__verbose = False
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
            # database_path_string = 'file:'+path+'?mode=rw'
            # __vprint__(f"database_path_string: {database_path_string}")
            self.__connection = sqlite3.connect(path)
            # if os.path.isfile(path):
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
            exit(2)  # Exit with system code 2 to indicate and error
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
                return self.__cursor.execute(sql, parameters)
            else:
                return self.__cursor.execute(sql)
        except sqlite3.Error as err:
            """
            # print(f"Error in SQL execute: {err.sqlite_errorname}")
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            #print("Exiting.")
            #exit(2)
            """
            return err

    def executescript(self, sql: str):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.
        :param sql: SQL statement to execute
        """
        self.__vprint(sql)
        try:
            return self.__cursor.executescript(sql)
        except sqlite3.Error as err:
            """
            print(f"Error in SQL executescript: {err.sqlite_errorname}")
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            #print("Exiting.")
            #exit(2)
            """
            return err

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

    def upgrade_database(self):
        db_version = None
        while True:
            # Loop until all upgrades have been applied
            '''
            print(f"SQL Query: \"{self.__sql_dictionary["does_database_information_table_exist"]}\"")
            self.execute(self.__sql_dictionary["does_database_information_table_exist"])
            rows_found = 0
            select_result = self.fetch_all_results()
            for row in select_result:
                #print(f"{row[0]}")
                rows_found += 1
            print(f"{rows_found} results found")
            if rows_found == 0:
                # DatabaseVersion table doesn't exist, so this must be the initial version 1 database
                db_version = 1
            else:
            '''
            # DatabaseVersion table does exist, so load the version of the database
            #print(f"SQL Query: \"{self.__sql_dictionary["find_db_version"]}\"")
            result = self.execute(self.__sql_dictionary["find_db_version"])
            #print(f"type(result): {type(result)}")
            if type(result) is sqlite3.OperationalError:
                print("DatabaseInformation table doesn't exist, so this must be database version 1")
                db_version = 1
            else:
                rows_found = 0
                select_result = self.fetch_all_results()
                for row in select_result:
                    db_version = int(row[0])
                    #print(f"db_version: {db_version}")
                    rows_found += 1
                #print(f"{rows_found} results found")

                if rows_found == 0:
                    # DBVersion not found
                    print("DBVersion not found in the DatabaseInformation table")
                    exit(2)
                elif rows_found > 1:
                    # More than one DBVersion found
                    print("More than one DBVersion found in the DatabaseInformation table. Can't continue.")
                    exit(2)
            # If we are here, then db_version have been loaded correctly
            print(f"Database version {db_version} detected.")

            sql_versions_length = len(self.__sql_versions)
            if db_version >= sql_versions_length:
                # Database is up to date
                print(f"Database version {db_version} is the latest version. No upgrade needed.")
                break
            else:
                # Database needs upgrading
                new_db_version = db_version + 1
                if str(new_db_version) not in self.__sql_versions:
                    print(f"No dictionary key found for upgrade version {new_db_version}")
                    exit(2)
                else:
                    sql_dictionary_key = self.__sql_versions[str(new_db_version)]
                    if sql_dictionary_key not in self.__sql_dictionary:
                        print(f"No upgrade SQL found for dictionary key {sql_dictionary_key} in the SQL dictionary")
                        exit(2)
                    else:
                        upgrade_sql = self.__sql_dictionary[sql_dictionary_key]
                        print(f"Upgrading database to version {new_db_version}.")
                        self.__vprint(f"SQL Query: \"{upgrade_sql}\"")
                        self.executescript(upgrade_sql)
                        self.commit()
                        print(f"Database upgraded to version {new_db_version} complete.")
        self.commit()

    def find_filenames_exact_match(self, filename: str, file_type: str, label: str = None):
        """
        if label is None:
            self.find_filenames(
                self.__sql_dictionary["find_filename_exact_match"],
                [filename]
            )
        else:
            self.find_filenames(
                self.__sql_dictionary["find_filename_exact_match_with_label"],
                [filename, label]
            )
        """
        self.find_filenames_search(filename, file_type, label, False)

    def find_filenames_search(self, file_search: str, file_category: str, label: str = None, like: bool = True):
        sql_string = self.__sql_dictionary["find_filename_base"]
        sql_argument_array = []
        clause_added = False

        if file_search is not None and file_search.count("%") == 0 and file_search.count("_") == 0:
            # We can replace this SQL "like" with an exact match '=' as it doesn't contain 'like" special characters
            like = False

        # Filename clause
        if like:
            sql_string += " " + self.__sql_dictionary["find_filename_like_filename_clause"]
            if file_search is not None and file_search != "":
                sql_argument_array.append(file_search)
            else:
                sql_argument_array.append("%")
        else:
            sql_string += " " + self.__sql_dictionary["find_filename_exact_match_filename_clause"]
            if file_search is not None and file_search != "":
                sql_argument_array.append(file_search)
            else:
                print("Filename can't be empty for an exact match search")
                exit()
        clause_added = True

        # Label clause
        if label is not None and label != "" :
            if clause_added:
                sql_string += " AND "
            sql_string += self.__sql_dictionary["find_filename_label_clause"]
            sql_argument_array.append(label)

        # Add table join
        sql_string += " " + self.__sql_dictionary["find_filename_post"]

        # Run the SQL
        print(f"sql_string: {sql_string}")
        print(f"sql_argument_array: {sql_argument_array}")
        self.find_filenames( sql_string, sql_argument_array )

    def find_filenames(self,
                       sql: str,
                       parameters: Optional[Union[Iterable, dict]] = None):
        result_array = []
        self.__vprint(f"SQL Query: \"{sql}\"")
        self.__vprint(f"filename: \"{parameters}\"")
        self.execute(sql,
                     parameters
                     )
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            print(f"{row[1]}, {row[0]}")
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
            #print(row[0])
            drive_ids.append(row[0])
            rows_found += 1
        self.__vprint(f"{rows_found} results found")
        return drive_ids

    def insert_drive(self, make: str, model: str, serial_number: str, hostname: str):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["insert_drive"]}\"")
        self.__vprint(
            f"make: \"{make}\", model: \"{model}\", serial_number: \"{serial_number}\", hostname: \"{hostname}\"")
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
                     [label]  # Use [] as a single parameter
                     )
        filesystem_ids = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            #print(row[0])
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
                     [filesystem_id]  # [] as a single parameter
                     )

    def delete_filesystem_listing_entries(self, filesystem_id: int):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["delete_filesystem_entries"]}\"")
        self.__vprint(f"filesystem_id: \"{filesystem_id}\"")
        self.execute(self.__sql_dictionary["delete_filesystem_entries"],
                     [filesystem_id]  # [] as a single parameter
                     )

    def update_filesystem_date(self, filesystem_id: int, date: int):
        self.__vprint(f"SQL Query: \"{self.__sql_dictionary["update_filesystem"]}\"")
        self.__vprint(f"filesystem_id: \"{filesystem_id}\", date: \"{date}\"")
        self.execute(self.__sql_dictionary["update_filesystem"],
                     (filesystem_id, date)  # () as a multiple parameters
                     )

    def empty_table(self, table_name: str):
        ## FIX ##
        # self.execute("DELETE FROM ?;", [table_name]) # As a single parameter, we have to wrap it in []
        # self.execute("DELETE FROM SQLITE_SEQUENCE WHERE name=?;", [table_name] )
        # Commit changes to the database
        # self.commit()
        return

### Class Test ###
# database = Database("I:\\FileProcessorDatabase\\database.sqlite")
# print(f"sql_dictionary: {database.sql_dictionary}")
